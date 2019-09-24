import time
import ctypes
from multiprocessing import Process
from threading import Thread
from minjob.logger import logger
from minjob.logger import MailNotifier

# These parameters are the default job monitoring and sleep before retry times
# they should be adjusted in the JobManager constructor depending on the
# needs of the application
JOB_RETRY_TIME = 1
JOB_MONITOR_TIME = 1


class Job:
    def __init__(self, name, target, *args, daemonize=False):

        self.name = name
        self.id = None
        self.nfail = 0
        self.daemonize = daemonize
        self.type = None

        self._target = target
        self._args = args
        self._job = None

    def start(self):
        """
        Start the job.
        """
        raise NotImplementedError("Not implemented")

    def stop(self):
        """
        Abruptly stop the job.
        """
        raise NotImplementedError("Not implement")

    def check_status(self):
        """
        Check the current status of the job and increment the
        failure count in the case it is not running.

        :return: the boolean returned by the is_alive() method
        """
        is_running = self.is_alive()
        if not is_running:
            self.nfail = self.nfail + 1
            self.id = None
        return is_running

    def is_alive(self):
        """
        Alias for the is_alive call of the Threading/Multiprocess APIs.

        :return: boolean which is True if the job is running and
        False otherwise
        """
        return self._job.is_alive()

    def __str__(self):
        res = f"""
Name: {self.name}
Type: {self.type}
pid:  {self.id}
"""
        return res


class JobProcess(Job):

    def __init__(self, name, target, *args, daemonize=False):
        super().__init__(name, target, *args, daemonize=daemonize)
        self.type = "Process"

    def start(self):
        self._job = Process(target=self._target,
                            args=self._args,
                            name=self.name,
                            daemon=self.daemonize)
        self._job.start()
        self.id = self._job.pid
        self.type = "Thread"

    def stop(self):

        if not self._job.is_alive():
            return

        self._job.terminate()
        self._job.join()


class JobThread(Job):

    def __init__(self, name, target, *args, daemonize=False):
        super().__init__(name, target, *args, daemonize=daemonize)
        self.type = "Thread"

    def start(self):
        self._job = Thread(target=self._target,
                           args=self._args,
                           name=self.name,
                           daemon=self.daemonize)
        self._job.start()
        self.id = self._job.ident

    def stop(self):
        """
        The following code abruptly terminates a running thread. This has been adapted
        from https://github.com/munshigroup/kthread

        WARNING: it is a bad practice to abruptly kill a running thread since the resources
        will not properly release and no try/except/finally will be executed
        However this library has been conceived for bots which has to run for a long time without
        interruption and usually stopping the threads means that the program is going to terminate.
        """

        if not self._job.is_alive():
            return

        exc = ctypes.py_object(SystemExit)
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
            ctypes.c_long(self.id), exc)
        if res == 0:
            raise ValueError(f"The chosen thread ID {self.id} is not existent")
        elif res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(self.id, None)
            raise SystemError("PyThreadState_SetAsyncExc failed")

        self._job.join()


class JobManager:

    """
    This is the main class of the library. It implements a simple job manager which
    monitors the jobs contained in the attribute `jobs` and restart them if a fatal
    exception occurs.
    """

    def __init__(self, name="MyApp", mail_info=None,
                 job_monitor_time=JOB_MONITOR_TIME,
                 job_retry_time=JOB_RETRY_TIME):
        """

        :param name: the name of the calling application
        :param mail_info: information for sending the email. If not set no email will be sent
        :param job_monitor_time: the time to wait after every check of the jobs
        :param job_retry_time: the time to wait before restarting a dead job
        """
        # this list takes track of all available processes
        self.jobs = []
        self.name = name
        self.max_fails = 10
        self.mail_info = mail_info
        self.supervisor = None

        self._job_monitor_time = job_monitor_time
        self._job_retry_time = job_retry_time

    def add_process(self, name, target, *args, daemonize=False):
        """
        Add a new Python Process to the monitored jobs
        :param name: a descriptive name of the process
        :param target: the function the process should execute
        :param args: the arguments of the function
        :param daemonize: start the process as daemon if the flag is set to True
        """
        p = JobProcess(name, target, *args, daemonize=daemonize)
        self.jobs.append(p)

    def add_thread(self, name, target, *args, daemonize=False):
        """
        Add a new Python Thread to the monitored jobs
        :param name: a descriptive name of the thread
        :param target: the function the thread should execute
        :param args: the arguments of the function
        :param daemonize: start the thread as daemon if the flag is set to True
        """
        p = JobThread(name, target, *args, daemonize=daemonize)
        self.jobs.append(p)

    def start_all(self, blocking=False):
        """
        Start all the monitored jobs. If the blocking flag is set to True
        the function will block until the script is killed otherwise it will
        release the execution
        :param blocking: if set to True block the execution on the job monitoring function
        :return:
        """
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
        """
        List of the available jobs by name
        :return: a list of strings with the name of the available jobs to be monitored
        """
        return [p.name for p in self.jobs]

    def _monitor(self):
        while True:
            for p in self.jobs:
                if not p.check_status():
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
                    time.sleep(self._job_retry_time)
                    p.start()
            time.sleep(self._job_monitor_time)
