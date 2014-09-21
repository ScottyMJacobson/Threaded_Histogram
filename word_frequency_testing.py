#! /usr/local/bin/python
# -*- coding: utf-8 -*-

# Scotty Jacobson
# 9/25/14
# COMP50 Concurrant Programming

import threading
import word_frequency

"""word_frequency_testing.py, a testing environment for module
word_frequency.py"""

def main():
    tests_passed = True
    tests_failed_string = ""
    example_safecount = word_frequency.SafeCount()
    
    #TEST 1
    example_safecount.increment()
    example_safecount.increment()
    if example_safecount.get_count() != 2:
        tests_passed = False
        tests_failed_string += "Simple increment \n"

    #TEST 2
    example_safecount.reset(5)
    example_safecount.decrement()
    example_safecount.decrement()
    if example_safecount.get_count() != 3:
        tests_passed = False
        tests_failed_string += "Simple decrement"


    if tests_passed:
        print "Tests Passed."
    else:
        print "Tests failed: {0}".format(tests_failed_string)


if __name__ == '__main__':
    main(sys.argv)