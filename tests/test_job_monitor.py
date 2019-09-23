import unittest
import time
from datetime import datetime

from minjob.jobs import JobManager


def run_process(name="charlie", code="bravo"):
    elapsed = 0
    while True:
        print("PROCESS [{}] The {}-{} process is still running correctly after {} s".format(datetime.utcnow(),
                                                                                            name, code, elapsed))
        elapsed += 10
        time.sleep(10)
        if elapsed > 20:
            raise Exception("Terminating process abruptely")


def run_thread(name="hawk", code="alpha"):
    elapsed = 0
    while True:
        print("THREAD [{}] The {}-{} process is still running correctly after {} s".format(datetime.utcnow(),
                                                                                           name, code, elapsed))
        time.sleep(5)
        elapsed += 5
        if elapsed > 15:
            raise Exception("Terminating thread abruptly")


class JobManagerTests(unittest.TestCase):

    def setUp(self):
        self.names = ["test_process", "test_thread"]
        self.manager = JobManager()
        self.manager.add_process(self.names[0], run_process, daemonize=True)
        self.manager.add_thread(self.names[1], run_thread, daemonize=True)

    def test_available_jobs(self):
        self.manager.start_all()
        available_jobs = self.manager.available_jobs()
        self.assertListEqual(available_jobs, self.names)

    def test_monitor(self):
        stop = False
        self.manager.start_all()
        while not stop:
            print(self.manager.available_jobs())
            time.sleep(10)
            self.manager.stop_all()
            stop = True
        job_alive = [s.job.is_alive() for s in self.manager.jobs]
        job_alive.append(self.manager.supervisor.job.is_alive())
        print(job_alive)
        # j = zip(self.manager.available_jobs(), job_alive)
        # time.sleep(5)
        # for name, is_alive in j:
        #     print(name, is_alive)
        # print("supervisor", self.manager.supervisor.job.is_alive)
