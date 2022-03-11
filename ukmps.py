#!/usr/bin/python
# -*- coding: utf-8  -*-
# Get a list of my photos from Wikimedia Commons
# Mike Peel     17-Jul-2016     v1 - initial version

from __future__ import unicode_literals
import pywikibot
import numpy as np
import time
import string
from pywikibot import pagegenerators
import time
import sys


reload(sys)
sys.setdefaultencoding('utf-8')

site = pywikibot.Site('en', 'wikipedia')
repo = site.data_repository()  # this is a DataSite object

print 'Fetch list 1'
cat1 = pywikibot.Category(site,'Category:UK MPs 2017–')

lines = []
i = 0
for page in cat1.articles(recurse=False):
    lines.append(page.title())
    print page.title()
    i += 1
