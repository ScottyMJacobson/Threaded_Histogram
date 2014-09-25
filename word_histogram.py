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

class SafeJobQueue:
    """SafeJobQueue, a FIFO object that provides thread-safe access to a 
    list and uses a Semaphore to keep track of availabilty. 
    Thus, it halts a thread if there's nothing available. """
    def __init__(self):
        self.items = list()
        self.items_available = threading.Semaphore(0)
        self.list_lock = threading.Lock()

    def enqueue(self, item):
        self.list_lock.acquire()
        self.items.insert(0, item)
        self.items_available.release()
        self.list_lock.release()

    def dequeue(self):
        self.items_available.acquire()
        self.list_lock.acquire()
        return_value = self.items.pop()
        self.list_lock.release()
        return return_value

class SafeStack:
    """SafeStack, a LIFO object that provides thread-safe access to a list
    (this use case: list of files remaining to parse, list of outputs)."""
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

class SafeLimitedStack:
    """A wrapper over safelist that uses a semaphore to halt threads calling 
    pop() when it is empty, and a second semaphore to limit the number of 
    objects that can flow through it. When this limit has been reached, 
    subsequent calls to pop will return a NoneType. Provides LIFO access"""
    def __init__(self, limit):
        self.items = SafeStack()
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

    def get_size(self):
        return self.items.get_size()

def make_filename_job(filename):
    return (("FILENAME", filename))

def make_per_file_histogram_job(histogram):
    return (("HISTOGRAM"), histogram)

def make_stop_order():
    return (("HEY_STOP_IT_YOU", "PRETTY_PLEASE"))

def thread_runtime(work_queue, global_histogram, print_lock):
    while 1:
        order_to_process = work_queue.dequeue()
        #If this signal was pushed onto the queue from main, and this thread
        #reaches it, it means there's nothing left for this thread to do 
        if order_to_process[0] == "HEY_STOP_IT_YOU":
            work_queue.enqueue(order_to_process)
            return
        #Task 1 - Acting as consumer and producer, a thread checks if the
        #current work order is a filename, and generates and prints its histo
        #it adds this histogram as a work order so it can possibly be absorbed 
        #by another thread while this thread is printing  
        elif order_to_process[0] == "FILENAME":
            filename_to_process = order_to_process[1]
            current_histogram = word_frequency.Histogram()
            if not (os.path.isfile(filename_to_process)):
                print>>sys.stderr, "Error: File \"{0}\" not found."\
                                                .format(filename_to_process)
            else:
                file_to_parse = open(filename_to_process, 'r')
                lines_in_file = list(file_to_parse)
                current_histogram = word_frequency.generate_histogram(\
                                                            lines_in_file)
                work_queue.enqueue(make_per_file_histogram_job(\
                                                        current_histogram))
                process_and_print(\
                                (filename_to_process, \
                                current_histogram.sorted_word_freq_list()), \
                                sys.stdout, print_lock, True)
            #End of Task 1

        #Task 2 - Acting as consumer, grab a per-file histogram to combine 
        #from the work queue and absorb it into the global histogram
        elif order_to_process[0] == "HISTOGRAM":
            global_histogram.absorb(order_to_process[1])
            #End of Task 2

def process_and_print(print_tuple, destination, \
                             print_lock, print_filename = False):
    """Takes in a tuple of (filename,sorted_word_freq_list) and prints
    to destination. 
    If print_filename is True, it prints in individual format, else it
    just prints the words line by line"""
    print_lock.acquire()
    current_filename = print_tuple[0]
    current_word_freq_list = print_tuple[1]
    for current_word_freq in current_word_freq_list:
        if print_filename:
            print>>destination, "{0}:\t{1} {2}".format(current_filename,\
                                current_word_freq[0], current_word_freq[1])
        else:
            print>>destination, "{0} {1}".format(\
                                    current_word_freq[0], current_word_freq[1])
    print_lock.release()



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--max_threads", type=int, default=10)
    parser.add_argument("-o", "--outfile", type=str)
    args = parser.parse_args()

    work_queue = SafeJobQueue()
    print_lock = threading.Lock()
    global_histogram = word_frequency.Histogram()

    thread_list = list()

    max_threads = args.max_threads if args.max_threads >= 2 else 2

    for thread_num in range(args.max_threads-1):
        thread_list.append(threading.Thread(target=thread_runtime, \
            args=(work_queue, global_histogram, print_lock)))
    for thread in thread_list:
        thread.start()

    filename = raw_input()
    while filename:
        if filename.strip():
            work_queue.enqueue(make_filename_job(filename.strip()))
        try:
            filename = raw_input()
            if not filename:
                work_queue.enqueue(make_stop_order())
        except KeyboardInterrupt:
            work_queue.enqueue(make_stop_order())
            break
        except EOFError:
            work_queue.enqueue(make_stop_order())
            break

    for thread in thread_list:
        thread.join()

    output_destination = sys.stdout
    if args.outfile:
        if args.outfile == "-":
            output_destination = sys.stdout
        else:
            output_destination = open(args.outfile, 'w')

    process_and_print(("Global",global_histogram.sorted_word_freq_list()),\
                                         output_destination, print_lock)
    exit(0)

if __name__ == '__main__':
    main()
    