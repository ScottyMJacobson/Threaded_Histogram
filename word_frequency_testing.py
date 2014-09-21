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
    example_safecount = word_frequency.SafeCount()
    example_safecount.increment()
    example_safecount.increment()
    if example_safecount.get_count() != 2:
        tests_passed = False

    

if __name__ == '__main__':
    main(sys.argv)