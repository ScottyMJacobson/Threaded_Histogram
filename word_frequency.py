#! /usr/local/bin/python
# -*- coding: utf-8 -*-

# Scotty Jacobson
# 9/25/14
# COMP50 Concurrant Programming

import threading

"""word_frequency.py, a python module whose main function,
    generate_histogram, takes in a stream of input and returns
    a dictionary matching word keys to WordCount objects"""


class SafeCount:
    """SafeCount, a wrapper for an object, similar to a semaphore, 
    that provides thread-safe access to a countable integer 
    (this use case: counts a particular word's frequency)"""    
    def __init__(self):
        self.count = 0
        self.count_lock = threading.Lock()

    def increment(self):
        self.count_lock.acquire()
        self.count += 1
        self.count_lock.release()

    def decrement(self):
        self.count_lock.acquire()
        self.count -= 1
        self.count_lock.release()

    def reset(self, new_count=0):
        self.count_lock.acquire()
        self.count = new_count
        self.count_lock.release()

    def get_count(self):
        self.count_lock.acquire()
        count = self.count
        self.count_lock.release()
        return count

class Histogram:
    """Histogram, a class that wraps and provides thread-safe access to 
    a dict whose keys are strings and whose objects are SafeCounts"""
    def __init__(self):
        self.dictionary = dict()
        self.dict_lock = threading.Lock()

    def increase_count(self, word):
        word = word.lower()
        word = word.strip()
        self.dict_lock.acquire()
        if word in self.dictionary:
            self.dictionary[word].increment()
        else:
            self.dictionary[word] = SafeCount()
            self.dictionary[word].increment()
        self.dict_lock.release()

    def get_count(self, word):
        word = word.lower()
        word = word.strip()        
        self.dict_lock.acquire()
        return_count = 0
        if word in self.dictionary:
            return_count = self.dictionary[word].get_count()
        self.dict_lock.release()
        return return_count



