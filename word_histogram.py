#! /usr/local/bin/python
# -*- coding: utf-8 -*-

# Scotty Jacobson
# 9/25/14
# COMP50 Concurrant Programming

import word_frequency

import threading
import argparse
import os.path
import sys

"""word_histogram.py, a program, utilizing word_frequency, that takes in 
a list of text files and a max number of threads and generates seperate
and cumulative histograms for the files"""

class SafeList:
    """SafeList, a wrapper object that provides thread-safe access to a list
    (this use case: list of files remaining to parse, list of outputs)"""
    def __init__(self):
        self.items = list()
        self.list_lock = threading.Lock()

    def append(self, item):
        """appends item to the end of the list"""
        self.list_lock.acquire()
        self.items.append(item)
        self.list_lock.release()

    def pop(self, index=0):
        """pops item at index from the list and returns. If no index is 
        specified, pops from the back of the list"""
        self.list_lock.acquire()
        return_value = self.items.pop(index)
        self.list_lock.release()
        return return_value

    def get_size(self):
        self.list_lock.acquire()
        size_of_list = len(self.items)
        self.list_lock.release()
        return size_of_list

def thread_runtime(filename_buffer, global_histogram, \
                    per_file_histograms, stdout_buffer):
    #1 - producer check if there are filenames left to process

    #2 - consumer check if there are per_file_histograms to combine, wait on
    #    the global variable and have that kill the thread
    pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--max_threads", type=int)
    parser.add_argument("-o", "--outfile", type=str)
    args = parser.parse_args()

    filename_buffer = SafeList()

    for line in sys.stdin:
        if line.strip():
            filename_buffer.append(line.strip())

    per_file_histograms = SafeList()

    stdout_buffer = SafeList()

    global_histogram = word_frequency.Histogram()



if __name__ == '__main__':
    main()