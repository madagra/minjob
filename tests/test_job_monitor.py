import unittest
import time
from minjob.jobs import JobManager


def run_process(name="charlie", code="bravo"):
    elapsed = 0
    while True:
        elapsed += 5
        time.sleep(5)
        if elapsed >= 5:
            raise Exception(f"Terminating process {name}-{code} abruptly")


def run_thread(name="hawk", code="alpha"):
    elapsed = 0
    while True:
        elapsed += 5
        time.sleep(5)
        if elapsed >= 5:
            raise Exception(f"Terminating thread {name}-{code} abruptly")


class MinJobTests(unittest.TestCase):

    def setUp(self):
        self.names = ["test_process", "test_thread"]
        self.manager = JobManager()
        self.manager.add_process(self.names[0], run_process, daemonize=True)
        self.manager.add_thread(self.names[1], run_thread, daemonize=True)

    def test_stop_jobs(self):
        stop = False
        self.manager.start_all()
        available_jobs = self.manager.available_jobs()
        self.assertListEqual(available_jobs, self.names)
        while not stop:
            time.sleep(2)
            self.manager.stop_all()
            stop = True
        job_alive = [(s.is_alive(), s.name) for s in self.manager.jobs]
        job_alive.append(self.manager.supervisor.is_alive())
        self.assertFalse(all(job_alive))

    def test_monitor_jobs(self):
        self.manager.start_all()
        available_jobs = self.manager.available_jobs()
        self.assertListEqual(available_jobs, self.names)

        stop = False
        while not stop:
            time.sleep(9)
            job_alive = [(s.is_alive(), s.name) for s in self.manager.jobs]
            self.assertTrue(all(job_alive))
            stop = True

        self.manager.stop_all()
        job_alive = [(s.is_alive(), s.name) for s in self.manager.jobs]
        job_alive.append(self.manager.supervisor.is_alive())
        self.assertFalse(all(job_alive))
