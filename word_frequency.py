#! /usr/local/bin/python
# -*- coding: utf-8 -*-

# Scotty Jacobson
# 9/25/14
# COMP50 Concurrant Programming

import threading
import argparse

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
        """If word exists in the histogram, increment, else add it 
        to the histogram and increment it once"""
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
        """If word exists in histogram, return its current count,
        otherwise, return 0"""
        word = word.lower()
        word = word.strip()        
        self.dict_lock.acquire()
        return_count = 0
        if word in self.dictionary:
            return_count = self.dictionary[word].get_count()
        self.dict_lock.release()
        return return_count

    def sorted_word_freq_list(self):
        """Runs through each key in the histogram alphabetically, returning
        a formatted list of strings with each word and its count"""
        running_list = list()
        for word in self.dictionary:
            running_list.append((word, self.dictionary[word].get_count()))
        running_list.sort(key=lambda t:t[0])
        return running_list

def generate_histogram(input_contents):
    """Takes in a list of lines as input, and parses each line for words,
    adding each word to a final histogram list which it returns"""
    return_histogram = Histogram()
    for line in input_contents:
        words = line.split()
        for word in words:
            return_histogram.increase_count(word)
    return return_histogram



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", type=str)
    args = parser.parse_args()

    file_to_parse = open(args.input_file, 'r')
    lines_in_file = list(file_to_parse)
    final_histogram = generate_histogram(lines_in_file)

    word_freq_list = final_histogram.sorted_word_freq_list()
    output_string = ""
    for freq_pair in word_freq_list:
        output_string += "{0} {1}\n".format(freq_pair[0], freq_pair[1])
    print output_string        
    

if __name__ == '__main__':
    main()

