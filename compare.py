from __future__ import unicode_literals
#!/usr/bin/python
# -*- coding: utf-8  -*-
# Compare the lists outputted by commons_photos.py and Lightroom_extract_filenames.py to get unique ones.
# Mike Peel		17-Jul-2016		v1 - initial version

import numpy as np
import time
import string
from pywikibot import pagegenerators
import codecs
import csv
import unicodedata

# List of photos from category
text_file = codecs.open("commons_photos.txt", "r", encoding='utf-8')
commons = text_file.readlines()
text_file.close()

# Watchlist
text_file = codecs.open('commons_watchlist.txt', "r", encoding='utf-8')
watchlist = text_file.readlines()
text_file.close()

lightroom = []
with open('sorted.csv', encoding="utf-8") as csvfile:
	read_in = csv.reader(csvfile)
	for row in read_in:
		vals = row[2].splitlines()
		if vals[0] != "Title":
			for i in range(0,len(vals)):
				vals[i] += '\n'
			# print(vals)
			lightroom = lightroom + vals

# print(len(lightroom))
# print(len(commons))
# print(len(watchlist))
# print(lightroom[0])
# print(commons[0])
# print(watchlist[0])
# exit()

lightroom2 = [unicodedata.normalize('NFD', x).encode('ascii', 'ignore') for x in lightroom]
commons2 = [unicodedata.normalize('NFD', x).encode('ascii', 'ignore') for x in commons]
# lightroom2 = unicodedata.normalize('NFC', lightroom[0])
# commons2 = unicodedata.normalize('NFC', commons[0])

commons_only = list(set(commons) - set(watchlist))

local_only = list(set(watchlist) - set(commons))

# commons_not_lightroom = list(set(commons) - set(lightroom))
#
# lightroom_not_commons = list(set(lightroom) - set(commons))

commons_not_lightroom = list(set(commons2) - set(lightroom2))

lightroom_not_commons = list(set(lightroom2) - set(commons2))

print(len(commons_only))
print(len(local_only))
print(len(commons_not_lightroom))
print(len(lightroom_not_commons))

text_file = codecs.open('category_only.txt', 'w', encoding='utf-8')
for item in commons_only:
  text_file.write("%s" % item)
text_file.close()


text_file = codecs.open('watchlist_only.txt', 'w', encoding='utf-8')
for item in local_only:
  text_file.write("%s" % item)
text_file.close()

text_file = codecs.open('commons_not_lightroom.txt', 'w', encoding='utf-8')
for item in commons_not_lightroom:
  text_file.write(str(item.decode('ascii')))
text_file.close()

text_file = codecs.open('lightroom_not_commons.txt', 'w', encoding='utf-8')
for item in lightroom_not_commons:
  text_file.write(str(item.decode('ascii')))
text_file.close()
