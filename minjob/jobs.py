import time
import ctypes
from multiprocessing import Process
from threading import Thread
from minjob.logger import logger
from minjob.logger import MailNotifier

RETRY_SLEEP_TIME = 10
JOB_MONITOR_TIME = 2


class Job:
    def __init__(self, name, target, *args, daemonize=False):
        self.name = name
        self.target = target
        self.args = args
        self.job = None
        self.id = None
        self.nfail = 0
        self.daemonize = daemonize

    def start(self):
        raise NotImplementedError("Not implemented")

    def stop(self):
        raise NotImplementedError("Not implement")

    def is_alive(self):
        is_running = self.job.is_alive()
        if not is_running:
            self.nfail = self.nfail + 1
            self.job.join()
            self.id = None
        return is_running

    def __str__(self):
        res = f"""
Name: {self.name}
pid:  {self.id}
"""
        return res


class JobProcess(Job):

    def start(self):
        self.job = Process(target=self.target,
                           args=self.args,
                           name=self.name,
                           daemon=self.daemonize)
        self.job.start()
        self.id = self.job.pid

    def stop(self):
        self.job.kill()


class JobThread(Job):

    def start(self):
        self.job = Thread(target=self.target,
                          args=self.args,
                          name=self.name,
                          daemon=self.daemonize)
        self.job.start()
        self.id = self.job.ident

    def stop(self):
        """
        The following code abruptly terminates a running thread. This has been adapted
        from https://github.com/munshigroup/kthread

        WARNING: it is a bad practice to abruptly kill a running thread since the resources
        will not properly release and no try/except/finally will be executed
        However this library has been conceived for bots which has to run for a long time without
        interruption and usually stopping the threads means that the program is going to terminate.
        """
        if not self.job.is_alive():
            return

        exc = ctypes.py_object(SystemExit)
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
            ctypes.c_long(self.id), exc)
        if res == 0:
            raise ValueError(f"The chosen thread ID {self.id} is not existent")
        elif res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(self.id, None)
            raise SystemError("PyThreadState_SetAsyncExc failed")


class JobManager:

    def __init__(self, name="MyApp", mail_info=None):
        # this list takes track of all available processes
        self.jobs = []
        self.name = name
        self.max_fails = 10
        self.mail_info = mail_info
        self.supervisor = None

    def add_process(self, name, target, *args, daemonize=False):
        p = JobProcess(name, target, *args, daemonize=daemonize)
        self.jobs.append(p)

    def add_thread(self, name, target, *args, daemonize=False):
        p = JobThread(name, target, *args, daemonize=daemonize)
        self.jobs.append(p)

    def start_all(self, blocking=False):
        for p in self.jobs:
            p.start()
        if not blocking:
            self.supervisor = JobThread("supervisor", self._monitor, daemonize=True)
            self.supervisor.start()
            assert self.supervisor.id is not None
        else:
            self._monitor()

    def stop_all(self):
        self.supervisor.stop()
        for p in self.jobs:
            p.stop()

    def available_jobs(self):
        return [p.name for p in self.jobs]

    def _monitor(self):
        while True:
            for p in self.jobs:
                if not p.is_alive():
                    logger.warning(f"Job {p.name} from the {self.name} application "
                                   f"has failed, restarting...")
                    if p.nfail % self.max_fails == 0:
                        info = f"Job {p.name} from the {self.name} application has failed " \
                            f"more than {self.max_fails} times.aborted"
                        logger.critical(info)
                        if self.mail_info:
                            notifier = MailNotifier(app_name=self.name, job_name=p.name,
                                                    config=self.mail_info)
                            notifier.abort(info)
                    time.sleep(RETRY_SLEEP_TIME)
                    p.start()
            time.sleep(JOB_MONITOR_TIME)
