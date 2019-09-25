## Description

*minjob* is a simple, purely Python library which allows to monitor Python threads and processes. It restarts the processes it monitors when a 
fatal exception occurs and can smoothly terminate them. Optionally, it can also send an email in the case a process has failed too many times.

This small library provides a simple way for dealing with fatal exceptions when running simple multi-thread/multi-process applications 
with high availability requirements such as market trading bots.

## Installation and Usage

Install the library within your favorite virtual environment or locally using:

```bash
pip install minjob
```

A simple usage of the library for adding a monitored process and
thread goes like:

```python
from minjob.jobs import JobManager

def my_thread_func():
    do_some_work()
    
def my_process_func():
    do_other_work()
    
manager = JobManager(name="MyManager")
manager.add_process("MyProcess", target=my_process_func, daemonize=True)
manager.add_thread("MyThread", target=my_thread_func, daemonize=True)

manager.start_all()
```