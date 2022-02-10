from __future__ import unicode_literals
#!/usr/bin/python
# -*- coding: utf-8  -*-
# Add some text to a wiki page
# Mike Peel     11-Jul-2017     v1 - initial version
# Mike Peel		24-Nov-2021		v2 - British Library specific code

import pywikibot
import numpy as np
import time
import string
from pywikibot import pagegenerators
import time

# Settings
targetcat = "Category:British Library King's Topographical collection"
newcat = "Category:Uploaded by the British Library"
targetcat = newcat
nummodified = 0
maxnum = 1

# Connect to the wikis
site = pywikibot.Site('commons', 'commons')
repo = site.data_repository()  # this is a DataSite object

def addcat(page, newcat):
		if page.text == '':
			print("Error - page is empty!")
			return 0

		for cat in page.categories():
			if 'Uploaded by the British Library' in cat.title():
				print('Already in category')
				return 0

		if newcat not in page.text:
			page.text = page.text + "\n[[" + newcat + "]]"
			input('Would save!')
			page.save(u"Adding [[:" + newcat + "]]")
			return 1
		else:
			print("Already in category")
			return 0

cat = pywikibot.Category(site, targetcat)
pages = pagegenerators.CategorizedPageGenerator(cat, recurse=False);
for page in pages:
	print(page.title())
	nummodified += addcat(page, newcat)

	print(nummodified)
	if nummodified >= maxnum:
		print("Reached the maximum of " + str(maxnum) + " entries modified, quitting!")
		exit()
