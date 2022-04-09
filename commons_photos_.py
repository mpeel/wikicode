#!/usr/bin/python3
# -*- coding: utf-8  -*-
# Get a list of my photos from Wikimedia Commons, and compare them to a local list
# Mike Peel		17-Jul-2016		v1 - initial version
import pywikibot
import numpy as np
import time
import string
from pywikibot import pagegenerators
import sys
import csv
import unicodedata

# sys.setdefaultencoding() does not exist, here!
# reload(sys)  # Reload does the trick!
# sys.setdefaultencoding('UTF8')

# First get the list of existing photos
# This needs to be pre-generated by exporting from Lightroom using LT/Transporter
photolist = []
with open("commons_photos.txt", mode='r',encoding='utf8') as infile:
    reader = csv.reader(infile)
    for rows in reader:
	    photolist.append(rows[0])
# print photolist
# print len(photolist)
# exit()

# Now get the list from Commons, and report the differences
site = pywikibot.Site('commons', 'commons')
repo = site.data_repository()  # this is a DataSite object
cat = pywikibot.Category(site,'Category:Photos by Mike Peel')

for image in cat.members(recurse=True):
	if image.title() not in photolist:
	    print(image.title())