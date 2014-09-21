#! /usr/local/bin/python
# -*- coding: utf-8 -*-

# Scotty Jacobson
# 9/25/14
# COMP50 Concurrant Programming

import sys
import threading
import word_frequency

"""word_frequency_testing.py, a testing environment for module
word_frequency.py"""

tests_failed_string = ""

def test_cmp (test_value, correct_value, test_name):
    if test_value == correct_value:
        return True
    else:
        tests_failed_string += test_name
        tests_failed_string += " Failed: {0} != {1}\n"\
                                            .format(test_value, correct_value)
        return False

def main():
    tests_passed = True
    tests_failed_string = ""
    example_safecount = word_frequency.SafeCount()
    
    #TEST SIMPLE INCREMENT
    example_safecount.increment()
    example_safecount.increment()
    tests_passed = tests_passed or test_cmp(example_safecount.get_count(), 2, "Simple Increment")

    #TEST SIMPLE RESET
    example_safecount.reset(5)
    tests_passed = tests_passed or test_cmp(example_safecount.get_count(), 5, "Simple Reset")

    #TEST SIMPLE DECREMENT
    example_safecount.reset(5)
    example_safecount.decrement()
    example_safecount.decrement()
    tests_passed = tests_passed or test_cmp(example_safecount.get_count(), 3, "Simple Decrement")

    #TEST SIMPLE HISTOGRAM
    example_histogram = word_frequency.Histogram()

    example_histogram.increase_count("Dummy")
    example_histogram.increase_count("dummy")
    example_histogram.increase_count("dummy ")
    example_histogram.increase_count("dummy. ")

    tests_passed = tests_passed or test_cmp(example_histogram.get_count("dummy"), 3, "Simple Word Adding")

    example_input_string = "HEY hey Horses .lol      Hey    lol LOL    \n Hey Horses"

    #TEST SIMPLE HISTOGRAM GENERATION
    histogram_gen = word_frequency.generate_histogram(example_input_string)
    hey_count = histogram_gen.get_count("Hey")
    horses_count = histogram_gen.get_count("horses")
    lol_count = histogram_gen.get_count("lol")
    dotlol_count = histogram_gen.get_count(".lol")

    tests_passed = tests_passed or test_cmp(hey_count, 4, "Simple Histogram Generation Hey")
    tests_passed = tests_passed or test_cmp(horses_count, 2, "Simple Histogram Generation Horses")
    tests_passed = tests_passed or test_cmp(lol_count, 2, "Simple Histogram Generation LOL")
    tests_passed = tests_passed or test_cmp(dotlol_count, 1, "Simple Histogram Generation .LOL")


    if tests_passed:
        print "Tests Passed."
    else:
        print "Tests failed: {0}".format(tests_failed_string)


if __name__ == '__main__':
    main()