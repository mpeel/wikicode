#!/usr/bin/python
# -*- coding: utf-8  -*-
# Create a histogram of the dates when books were created
# Mike Peel     23-Apr-2022      v1 - start
import pywikibot
from pywikibot import pagegenerators
import numpy as np
import matplotlib.pyplot as plt

enwiki = pywikibot.Site('en', 'wikipedia')

hist_arr = []
years = 2000 + np.arange(4,23,1)
months = np.arange(1,13,1)
datearr = []
plot_arr = []
for year in years:
	for month in months:
		if month < 10:
			datearr.append(str(year)+'-0'+str(month))
			plot_arr.append(year+(month/12))
		else:
			datearr.append(str(year)+'-'+str(month))
			plot_arr.append(year+(month/12))
vals = np.zeros(len(datearr))

# max_num = 100
# count = 0

cat = pywikibot.Category(enwiki,"Category:User namespace book pages")
for page in pagegenerators.CategorizedPageGenerator(cat, recurse=False):
	# count += 1
	history = page.getVersionHistoryTable(reverse=True)
	hist = history.splitlines()
	trip = 0
	for line in hist:
		if '||' in line and 'oldid' not in line and trip == 0:
			date = line.split('||')[1].strip()[0:7]
			index = datearr.index(date)
			vals[index] += 1
			trip = 1
	# if count > max_num:
	# 	break

plt.plot(plot_arr, vals)
print(datearr)
print(vals)
plt.title('Book creation dates on enwiki')
plt.xlabel('Time (yrs)')
plt.ylabel('Count')
plt.savefig('book_histogram.pdf')
