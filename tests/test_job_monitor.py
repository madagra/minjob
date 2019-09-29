import unittest
import time
from minjob.jobs import JobManager


def run_process(with_exception, name="charlie", code="bravo"):
    elapsed = 0
    while True:
        elapsed += 5
        time.sleep(5)
        if elapsed >= 5:
            if with_exception:
                raise Exception(f"Terminating process {name}-{code} abruptly")
            else:
                break


def run_thread(with_exception, name="hawk", code="alpha"):
    elapsed = 0
    while True:
        elapsed += 5
        time.sleep(5)
        if elapsed >= 5:
            if with_exception:
                raise Exception(f"Terminating thread {name}-{code} abruptly")
            else:
                break


class MinJobTests(unittest.TestCase):

    with_exceptions = [True, False]

    def setUp(self):
        self.names = ["test_process", "test_thread"]

    def _stop_jobs(self, with_exceptions):

        manager = JobManager()
        manager.add_process(self.names[0], run_process, with_exceptions, daemonize=True)
        manager.add_thread(self.names[1], run_thread, with_exceptions, daemonize=True)

        stop = False
        manager.start_all()
        available_jobs = manager.available_jobs()
        self.assertListEqual(available_jobs, self.names)
        while not stop:
            time.sleep(2)
            manager.stop_all()
            stop = True
        job_alive = [(s.is_alive(), s.name) for s in manager.jobs]
        job_alive.append(manager.supervisor.is_alive())
        self.assertFalse(all(job_alive))

    def _monitor_jobs(self, with_exceptions):

        manager = JobManager()
        manager.add_process(self.names[0], run_process, with_exceptions, daemonize=True)
        manager.add_thread(self.names[1], run_thread, with_exceptions, daemonize=True)

        manager.start_all()
        available_jobs = manager.available_jobs()
        self.assertListEqual(available_jobs, self.names)

        stop = False
        while not stop:
            time.sleep(9)
            job_alive = [(s.is_alive(), s.name) for s in manager.jobs]
            self.assertTrue(all(job_alive))
            stop = True

        manager.stop_all()
        job_alive = [(s.is_alive(), s.name) for s in manager.jobs]
        job_alive.append(manager.supervisor.is_alive())
        self.assertFalse(all(job_alive))

    # FIXME: migrate to pytest to use better test parametrization
    def test_stop_jobs(self):
        for ex in self.with_exceptions:
            self._stop_jobs(ex)

    def test_monitor_jobs(self):
        for ex in self.with_exceptions:
            self._monitor_jobs(ex)
