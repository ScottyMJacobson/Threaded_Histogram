#! /usr/local/bin/python
# -*- coding: utf-8 -*-

# Scotty Jacobson
# 9/25/14
# COMP50 Concurrant Programming

import sys
import threading
import word_frequency
from word_histogram import SafeList

"""word_frequency_testing.py, a testing environment for module
word_frequency.py"""

tests_failed_string = ""
tests_passed = True

def test_cmp (test_value, correct_value, test_name):
    if test_value == correct_value:
        return
    else:
        global tests_failed_string
        tests_failed_string += test_name
        tests_failed_string += " Failed: {0} != {1}\n"\
                                            .format(test_value, correct_value)
        print tests_failed_string
        global tests_passed
        tests_passed = False
        return

def main():
    tests_failed_string = ""
    example_safecount = word_frequency.SafeCount()
    
    #TEST SIMPLE INCREMENT
    example_safecount.increment()
    example_safecount.increment()
    test_cmp(example_safecount.get_count(), 2, "Simple Increment")

    #TEST SIMPLE RESET
    example_safecount.reset(5)
    test_cmp(example_safecount.get_count(), 5, "Simple Reset")

    #TEST INCREASE BY
    example_safecount.reset(5)
    example_safecount.increase_by(7)
    test_cmp(example_safecount.get_count(), 12, "Simple Increase By")

    #TEST SIMPLE DECREMENT
    example_safecount.reset(5)
    example_safecount.decrement()
    example_safecount.decrement()
    test_cmp(example_safecount.get_count(), 3, "Simple Decrement")

    #TEST THREADED DECREMENT
    example_safecount.reset(5)
    thread1 = threading.Thread(target=example_safecount.decrement())
    thread2 = threading.Thread(target=example_safecount.decrement())
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()
    test_cmp(example_safecount.get_count(), 3, "Threaded Decrement")

    #TEST SIMPLE HISTOGRAM
    example_histogram = word_frequency.Histogram()

    example_histogram.increment_count("Dummy")
    example_histogram.increment_count("dummy")
    example_histogram.increment_count("dummy ")
    example_histogram.increment_count("dummy. ")

    test_cmp(example_histogram.get_count("dummy"), 3, "Simple Word Adding")

    #TEST HISTOGRAM INCREASE_COUNT_BY
    example_histogram.increase_count_by("dummy", 2)
    test_cmp(example_histogram.get_count("dummy"), 3+2, "Increase_Count_By")


    example_input_string_list = ["HEY hey Horses .lol      Hey    lol LOL    \n Hey Horses"]

    #TEST SIMPLE HISTOGRAM GENERATION
    histogram_gen = word_frequency.generate_histogram(example_input_string_list)
    hey_count = histogram_gen.get_count("Hey")
    horses_count = histogram_gen.get_count("horses")
    lol_count = histogram_gen.get_count("lol")
    dotlol_count = histogram_gen.get_count(".lol")

    test_cmp(hey_count, 4, "Simple Histogram Generation Hey")
    test_cmp(horses_count, 2, "Simple Histogram Generation Horses")
    test_cmp(lol_count, 2, "Simple Histogram Generation LOL")
    test_cmp(dotlol_count, 1, "Simple Histogram Generation .LOL")

    test_list = histogram_gen.sorted_word_freq_list()
    golden_list = [(".lol",1),("hey",4),("horses",2),("lol",2)]

    test_cmp(test_list, golden_list, "sorted_word_freq_list Check")

    #TEST ABSORB LIST INTO BLANK
    master_hist1 = word_frequency.Histogram()
    master_hist1.absorb(histogram_gen)
    test_cmp(master_hist1.sorted_word_freq_list(), histogram_gen.sorted_word_freq_list(), "Sorted absorb list test")

    #TEST ABSORB FULL LIST INTO FULL LIST
    example_input_string_list2 = ["hardy har har horses hey .lol LOL lol \n"]
    master_hist2 = word_frequency.generate_histogram(example_input_string_list2)

    master_hist2.absorb(histogram_gen)
    golden_list2 = [(".lol",2),("har", 2),("hardy",1),("hey",5),("horses",3),("lol",4)]
    test_cmp(master_hist2.sorted_word_freq_list(), golden_list2, "Absorb original list into master_list2")

    #TEST ABSORB TWO LISTS AT ONCE
    example_input_string_list3 = ["the cake is a lie LOL \n"]
    listogram = list()
    listogram.append(word_frequency.generate_histogram(example_input_string_list3))
    listogram.append(word_frequency.generate_histogram(example_input_string_list2))
    listogram.append(word_frequency.generate_histogram(example_input_string_list))

    threads_list = list()
    for histo in listogram[1:]:
        threads_list.append(threading.Thread(target=listogram[0].absorb, args=(histo,)))

    for thread in threads_list:
        thread.start()
    for thread in threads_list:
        thread.join()

    golden_cumulative = [(".lol",2), ("a", 1), ("cake", 1), ("har", 2),("hardy",1),("hey",5),("horses",3)]
    golden_cumulative += [("is", 1), ("lie", 1), ("lol",5), ("the", 1)]

    test_cmp(listogram[0].sorted_word_freq_list(), golden_cumulative, "Threaded huge multi absorb")

    #SAFELIST SIMPLE APPEND AND POP TEST
    safelist_tester = SafeList()
    safelist_tester.append("Hello!")
    test_cmp(safelist_tester.pop(), "Hello!", "SafeList Simple Append and Pop")

    if tests_passed:
        print "Tests Passed."
    else:
        print "Tests failed: {0}".format(tests_failed_string)


if __name__ == '__main__':
    main()