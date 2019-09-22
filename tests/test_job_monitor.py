import unittest
from datetime import datetime


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
        self.manager = JobManager()
        self.manager.add_process("process", run_process)
        self.manager.add_thread("thread", run_thread)

    def test_monitor(self):
        self.manager.monitor()
