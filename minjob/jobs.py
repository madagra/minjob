import time
from multiprocessing import Process
from threading import Thread
from minjob.logger import logger
from minjob.logger import MailNotifier

RETRY_SLEEP_TIME = 300
JOB_MONITOR_TIME = 10


class Job:
    def __init__(self, name, target, *args):
        self.name = name
        self.target = target
        self.args = args
        self.job = None
        self.id = None
        self.nfail = 0

    def start(self):
        raise NotImplementedError("Not implemented")

    def is_alive(self):
        is_running = self.job.is_alive()
        if not is_running:
            self.nfail = self.nfail + 1
            self.job.join()
        return is_running

    def __str__(self):
        res = """
Name: {}
Args: {}
pid:  {}
        """.format(self.name, self.args, self.id)
        return res


class JobProcess(Job):

    def start(self):
        self.job = Process(target=self.target,
                           args=self.args,
                           name=self.name)
        self.job.start()
        self.id = self.job.pid


class JobThread(Job):

    def start(self):
        self.job = Thread(target=self.target,
                          args=self.args,
                          name=self.name)
        self.job.start()
        self.id = self.job.ident


class JobManager:
    def __init__(self, name="MyApp", mail_info=None):
        self.jobs = []
        self.name = name
        self.max_fails = 10
        self.mail_info = mail_info

    def add_process(self, name, target, *args):
        p = JobProcess(name, target, *args)
        self.jobs.append(p)

    def add_thread(self, name, target, *args):
        p = JobThread(name, target, *args)
        self.jobs.append(p)

    def monitor(self):
        for p in self.jobs:
            p.start()
        while True:
            for p in self.jobs:
                if not p.is_alive():
                    logger.warning("Job {} dead, restarting...".format(p.name))
                    if p.nfail % self.max_fails == 0:
                        info = "Job {} aborted".format(p.name)
                        if self.mail_info:
                            notifier = MailNotifier(app_name=self.name, job_name=p.name,
                                                    config=self.mail_info)
                            notifier.abort(info)
                    time.sleep(RETRY_SLEEP_TIME)
                    p.start()
            time.sleep(JOB_MONITOR_TIME)

