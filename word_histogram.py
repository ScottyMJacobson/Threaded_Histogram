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
    (this use case: list of files remaining to parse, list of outputs)
    if items_to_expect is provided, create a semaphore that """
    def __init__(self):
        self.items = list()
        self.list_lock = threading.Lock()

    def append(self, item):
        """appends item to the end of the list"""
        self.list_lock.acquire()
        self.items.append(item)
        self.list_lock.release()

    def pop(self, index=-1):
        """pops item at index from the list and returns. 
        If index is not valid or list is empty, squelches exception 
        and returns None
        If no index is specified, pops from the back of the list."""
        self.list_lock.acquire()
        if index:
            try:
                return_value = self.items.pop(index)
            except IndexError:
                return_value = None
        else:
            return_value = self.items.pop()
        self.list_lock.release()
        return return_value

    def get_size(self):
        self.list_lock.acquire()
        size_of_list = len(self.items)
        self.list_lock.release()
        return size_of_list

class SafeLimitedList:
    """A wrapper over safelist that uses a semaphore to halt threads calling 
    pop() when it is empty, and a second semaphore to limit the number of 
    objects that can flow through it. When this limit has been reached, 
    subsequent calls to pop will return a NoneType"""
    def __init__(self, limit):
        self.items = SafeList()
        self.flow_limit = threading.Semaphore(limit) #decremented with pop
        self.items_available = threading.Semaphore(0)

    def append(self, item):
        self.items.append(item)
        self.items_available.release()

    def pop(self):
        """pops from the back of the list.
        If the limit has been used up, there's no object, and there's
        never gonna be an object, kid. Give up. (tell the calling thread that
        there's nothing coming by returning None)"""
        if not self.flow_limit.acquire(False):
            if self.items.get_size():
                return None
            return None
        self.items_available.acquire()
        return_value = self.items.pop()
        return return_value


def thread_runtime(filename_buffer, global_histogram, \
                    per_file_histograms, per_file_print_buffer):
    #Task 1 - Acting as producer, a thread checks if there are filenames left 
    #to process and generates a histogram with each
    filename_to_process = filename_buffer.pop()
    current_histogram = word_frequency.Histogram()
    while (filename_to_process):
        if not (os.path.isfile(filename_to_process)):
            print>>sys.stderr, "Error: File \"{0}\" not found."\
                                                    .format(args.input_file)
        file_to_parse = open(filename_to_process, 'r')
        lines_in_file = list(file_to_parse)
        current_histogram = word_frequency.generate_histogram(lines_in_file)
        per_file_print_buffer.append(\
                (filename_to_process,current_histogram.sorted_word_freq_list()))
        per_file_histograms.append(current_histogram)
        filename_to_process = filename_buffer.pop()

    #Task 2 - Acting as consumer, check if there are per_file_histograms 
    #to combine, wait on per_file_histograms if none, pop one, or terminate
    histogram_to_process = per_file_histograms.pop()
    if not histogram_to_process: #SafeCyclesList returns a nonetype if its                             
        return                   #cycles have been used up. We're done here!
    while (histogram_to_process):
        global_histogram.absorb(histogram_to_process)
        histogram_to_process = per_file_histograms.pop()
    return


def process_list_and_print(print_buffer, destination, \
                                                    print_filename = False):
    """Takes in a list of (filename,sorted_word_freq_list) tuples and prints
    to destination. 
    If print_filename is True, it prints in individual format, else it
    just prints the words line by line"""
    current_tuple = print_buffer.pop()
    while (current_tuple):
        current_filename = current_tuple[0]
        current_word_freq_list = current_tuple[1]
        for current_word_freq in current_word_freq_list:
            if print_filename:
                print>>destination, "{0}:\t{1} {2}".format(current_filename,\
                                current_word_freq[0], current_word_freq[1])
            else:
                print>>destination, "{0} {1}".format(\
                                    current_word_freq[0], current_word_freq[1])
        current_tuple = print_buffer.pop()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--max_threads", type=int, default=10)
    parser.add_argument("-o", "--outfile", type=str)
    args = parser.parse_args()

    filename_buffer = SafeList()

    for line in sys.stdin:
        if line.strip():
            filename_buffer.append(line.strip())

    per_file_histograms = SafeLimitedList(filename_buffer.get_size())
    per_file_print_buffer = SafeList()
    global_histogram = word_frequency.Histogram()

    thread_list = list()

    for thread_num in range(args.max_threads):
        thread_list.append(threading.Thread(target=thread_runtime, \
            args=(filename_buffer, global_histogram, \
                per_file_histograms, per_file_print_buffer)))

    per_file_histogram_available = threading.Condition()

    for thread in thread_list:
        thread.start()
    for thread in thread_list:
        thread.join()

    process_list_and_print(per_file_print_buffer, sys.stdout, True)
    global_print_buffer = SafeList()
    global_print_buffer.append(\
                        ("Global",global_histogram.sorted_word_freq_list()) )
    output_destination = sys.stdout
    if args.outfile:
        if args.outfile == " ":
            output_destination = sys.stdout
        else:
            output_destination = open(args.outfile, 'w')

    process_list_and_print(global_print_buffer, output_destination)


if __name__ == '__main__':
    main()
    