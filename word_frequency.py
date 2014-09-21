#! /usr/local/bin/python
# -*- coding: utf-8 -*-

# Scotty Jacobson
# 9/25/14
# COMP50 Concurrant Programming

"""word_frequency.py, a python module whose main function,
    generate_histogram, takes in a stream of input and returns
    a dictionary matching word keys to WordCount objects"""


class SafeCount:
"""SafeCount, a wrapper for an object that provides thread-safe access 
to a countable integer (this use case: for a particular word's frequency)"""    
    def __init__(self):
        self.count = 0
        self.lock = Lock()

    def increment(self):
        self.lock.acquire()
        self.count += 1
        self.lock.release()

    def decrement(self):
        self.lock.acquire()
        self.count += 1
        self.lock.release()

    def get_count(self):
        self.lock.acquire()
        count = self.count
        self.lock.release()
        return count
