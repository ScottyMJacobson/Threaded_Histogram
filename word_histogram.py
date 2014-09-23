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
        specified, pops from the back of the list. If the list is empty,
        returns as void with NoneType object"""
        self.list_lock.acquire()
        if len(self.items):
            return_value = self.items.pop(index)
        else:
            return_value = None
        self.list_lock.release()
        return return_value

    def get_size(self):
        self.list_lock.acquire()
        size_of_list = len(self.items)
        self.list_lock.release()
        return size_of_list

def thread_runtime(filename_buffer, global_histogram, \
                    per_file_histograms, per_file_print_buffer):
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

    #1 - producer check if there are filenames left to process and process a 
        # histogram with each

    #2 - consumer check if there are per_file_histograms to combine, wait on
        # the global variable and have that kill the thread
    
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

    per_file_histograms = SafeList()
    per_file_print_buffer = SafeList()
    global_histogram = word_frequency.Histogram()

    thread_list = list()

    for thread_num in range(args.max_threads):
        thread_list.append(threading.Thread(target=thread_runtime, \
            args=(filename_buffer, global_histogram, \
                per_file_histograms, per_file_print_buffer)))

    for thread in thread_list:
        thread.start()
    for thread in thread_list:
        thread.join()

    process_list_and_print(per_file_print_buffer, sys.stdout, True)
    global_print_buffer = SafeList()
    global_print_buffer.append(\
                        ("Global",global_histogram.sorted_word_freq_list())   )
    output_destination = sys.stdout
    if args.outfile:
        if args.outfile == " ":
            output_destination = sys.stdout
        else:
            output_destination = open(args.outfile, 'w')

    process_list_and_print(global_print_buffer, output_destination)


if __name__ == '__main__':
    main()