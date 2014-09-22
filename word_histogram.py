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
and cumulative histograms for the files"

