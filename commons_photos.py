from __future__ import unicode_literals
#!/usr/bin/python
# -*- coding: utf-8  -*-
# Get a list of my photos from Wikimedia Commons
# python commons_photos.py > commons_photos.txt
# Mike Peel		17-Jul-2016		v1 - initial version

import pywikibot
import numpy as np
import time
import string
from pywikibot import pagegenerators

site = pywikibot.Site('commons', 'commons')
repo = site.data_repository()  # this is a DataSite object

cats = ['Category:Photos by Mike Peel','Category:Figures by Mike Peel','Category:Presentations by Mike Peel']
for catname in cats:
	cat = pywikibot.Category(site,catname)
	# print(cat)

	for image in cat.articles(recurse=True):
		print(image.title())
