#!/usr/bin/python
# -*- coding: utf-8  -*-
# Remove locally defined commons category links when bad or pointing to a redirect
# Mike Peel     01-Jan-2019      v1 - start
# Mike Peel     14-Jan-2019      v1.1 - tweaks for enwp bot approval
# Mike Peel     20-Jan-2019      v1.2 - last check for files in a category

from __future__ import unicode_literals

import pywikibot
import numpy as np
import time
import string
from pywikibot import pagegenerators
import urllib
from pibot_functions import *

maxnum = 10000
nummodified = 0
categories = 1

wikidata_site = pywikibot.Site("wikidata", "wikidata")
repo = wikidata_site.data_repository()  # this is a DataSite object
commons = pywikibot.Site('commons', 'commons')
enwp = pywikibot.Site('en', 'wikipedia')
debug = 0
trip = 1

targetcat = 'Category:Pages using authority control without Wikidata link'
cat = pywikibot.Category(commons, targetcat)

templates = ['Authority control', 'authority control']

if categories:
	pages = pagegenerators.SubCategoriesPageGenerator(cat, recurse=False);
else:
	pages = pagegenerators.CategorizedPageGenerator(cat, recurse=False);
for page in pages:

	# Cut-off at a maximum number of edits	
	print("")
	print(nummodified)
	if nummodified >= maxnum:
		print('Reached the maximum of ' + str(maxnum) + ' entries modified, quitting!')
		exit()

	# Get the Wikidata item
	try:
		wd_item = pywikibot.ItemPage.fromPage(page)
		item_dict = wd_item.get()
		qid = wd_item.title()
	except:
		# If that didn't work, go no further
		print(page.title() + ' - no page found')
		continue

	print("\n" + qid)
	print(page.title())

	# If we have a P910 value, switch to using that item
	have_followed_p910 = False
	try:
		existing_id = item_dict['claims']['P910']
		print('P910 exists, following that.')
		for clm2 in existing_id:
			wd_item = clm2.getTarget()
			item_dict = wd_item.get()
			print(wd_item.title())
		have_followed_p910 = True
	except:
		null = 0


	# That did work, let's see if we have the ID in the commons category
	target_text = page.get()
	if qid in target_text:
		continue

	# We don't. Let's add it!
	for i in range(0,len(templates)):
		try:
			target_text = target_text.replace(templates[i], templates[i]+'|wikidata='+qid)
		except:
			null = 1

	if page.get() != target_text:
		page.text = target_text
		test = 'y'
		savemessage = "Add the category's Wikidata ID (" + qid + ") to the authority control template"
		if debug == 1:
			test = 'n'
			print(target_text)
			print(qid)
			print(page.title())
			print(savemessage)
			test = input("Continue? ")
		if test != 'n':
			nummodified += 1
			page.save(savemessage)
			continue

print('Done! Edited ' + str(nummodified) + ' entries')
		
# EOF