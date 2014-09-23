#! /usr/local/bin/python
# -*- coding: utf-8 -*-

# Scotty Jacobson
# 9/25/14
# COMP50 Concurrant Programming

import sys
import threading
import word_frequency
import word_histogram


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
    safelist_tester = word_histogram.SafeList()
    safelist_tester.append("Hello!")
    test_cmp(safelist_tester.pop(), "Hello!", "SafeList Simple Append and Pop")

    #SAFELIST LIFO APPEND AND POP TEST
    safelist_tester = word_histogram.SafeList()
    safelist_tester.append("Hello!")
    safelist_tester.append("Second")
    test_cmp(safelist_tester.pop(), "Second", "SafeList Simple Append and Pop")


    #SAFELIST APPEND, AND POP BY INDEX TEST
    safelist_tester = word_histogram.SafeList()
    safelist_tester.append("Zero Maca")
    safelist_tester.append("One Maca")
    safelist_tester.append("Two Maca")
    safelist_tester.append("Three Macarena")
    test_cmp(safelist_tester.pop(2), "Two Maca", "SafeList append, pop by index")

    #SAFELIST GET SIZE TEST
    safelist_tester = word_histogram.SafeList()
    safelist_tester.append("One Fish")
    safelist_tester.append("Two Fish")
    safelist_tester.append("Red Fish")
    safelist_tester.append("Blue Fish")
    test_cmp(safelist_tester.get_size(), 4, "SafeList get_size")

    #SAFELIST OUT OF BOUNDS TEST
    safelist_tester = word_histogram.SafeList()
    safelist_tester.append("On the Edge")
    safelist_tester.append("Of glory")
    caught_val = safelist_tester.pop(2)
    test_cmp(caught_val, None, "Out of bounds test")

    #SAFELIMITEDLIST APPEND AND POP TEST
    safelimited_tester = word_histogram.SafeLimitedList(5)
    safelimited_tester.append("Swag")
    safelimited_tester.append("Gerific")
    caught_val = safelimited_tester.pop()
    caught_val2 = safelimited_tester.pop()
    test_cmp(caught_val, "Gerific", "SafeLimited Append and Pop1")
    test_cmp(caught_val2, "Swag", "SafeLimited Append and Pop2")


    #SAFELIMITEDLIST THREADED ACCESS TESET
    safelimited_tester2 = word_histogram.SafeLimitedList(5)
    
    def add_to_safe_limited(safelimited_list, item_to_add):
        safelimited_list.append(item_to_add)

    def pop_from_safe_limited_onto(safelimited_list, external_list):
        return_value = safelimited_list.pop()
        external_list.append(return_value)

    threads_list = list()
    caught_values = list()
    threads_list.append(threading.Thread(target=pop_from_safe_limited_onto, args=((safelimited_tester2, caught_values))))
    threads_list.append(threading.Thread(target=add_to_safe_limited, args=((safelimited_tester2,"One"))))
    threads_list.append(threading.Thread(target=add_to_safe_limited, args=((safelimited_tester2,"Two"))))
    threads_list.append(threading.Thread(target=pop_from_safe_limited_onto, args=((safelimited_tester2, caught_values))))

    for thread in threads_list:
        thread.start()
    for thread in threads_list:
        thread.join()

    caught_values.sort()
    test_cmp(caught_values, ["One", "Two"], "SafeLimitedList Access")


    if tests_passed:
        print "Tests Passed."
        exit(0)
    else:
        print "Tests failed: {0}".format(tests_failed_string)
        exit(1)


if __name__ == '__main__':
    main()