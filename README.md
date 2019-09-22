# Description

minjob is a simple, purely Python library which allows to monitor Python threads and subprocesses: it restarts them when an exception occurs with an optional
callback called when restarting and it can smoothly terminate them. Optionally, it can also send an email in the case a process has failed too many times.

This small library provides a simple way for dealing with fatal exceptions when running simple multi-threaded/multi-process applications 
with high availability requirements such as market trading bots.

# Installation and Usage


