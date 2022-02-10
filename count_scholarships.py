#!/usr/bin/python
# -*- coding: utf-8  -*-
# Code adapted from http://stackoverflow.com/questions/28418988/how-to-make-a-histogram-from-a-list-of-strings-in-python

from collections import Counter
import numpy as np
import matplotlib.pyplot as plt
import codecs

def plot_bar_from_counter(counter, ax=None):
    """"
    This function creates a bar plot from a counter.

    :param counter: This is a counter object, a dictionary with the item as the key
     and the frequency as the value
    :param ax: an axis of matplotlib
    :return: the axis wit the object in it
    """

    if ax is None:
        fig = plt.figure()
        ax = fig.add_subplot(111)

    frequencies = counter.values()
    names = counter.keys()

    x_coordinates = np.arange(len(counter))
    ax.bar(x_coordinates, frequencies, align='center')

    ax.xaxis.set_major_locator(plt.FixedLocator(x_coordinates))
    ax.xaxis.set_major_formatter(plt.FixedFormatter(names))

    return ax

text_file = codecs.open("count_scholarships.txt", "r", encoding='utf-8')
scholarships = text_file.readlines()
text_file.close()

counts = Counter(scholarships)
numtimes = np.zeros(10)
for letter in counts:
    numtimes[counts[letter]] = numtimes[counts[letter]]  + 1

print numtimes
print sum(numtimes)

plot_bar_from_counter(counts)
plt.savefig('scholarship_count.jpg')