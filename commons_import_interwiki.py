#!/usr/bin/python
# -*- coding: utf-8  -*-
# Check for consistency in commons category usage
# Mike Peel     01-Mar-2018      v1 - start

from __future__ import unicode_literals

import pywikibot
import numpy as np
import time
import string
from pywikibot import pagegenerators
import urllib
import time
import pprint
import csv

def prettyPrint(variable):
	pp = pprint.PrettyPrinter(indent=4)
	pp.pprint(variable)

wikidata_site = pywikibot.Site("wikidata", "wikidata")
repo = wikidata_site.data_repository()  # this is a DataSite object
commons = pywikibot.Site('commons', 'commons')
enwiki = pywikibot.Site('en', 'wikipedia')

regex = 'insource:/"[[en"/'
generator = pagegenerators.SearchPageGenerator(regex, site=commons, namespaces=[14])
gen = pagegenerators.PreloadingGenerator(generator)
count = 0
for category in gen:
	print(str(count) + ' - ' + category.title())
	count += 1
	enwp = ''
	for iw in category.interwiki():
		if 'wikipedia:en' in str(iw):
			enwp = str(iw).replace('[[wikipedia:en:','').replace(']]','')
	page = pywikibot.Page(enwiki, enwp)
	try:
		wd_item = pywikibot.ItemPage.fromPage(page)
		print(wd_item)
		item_dict = wd_item.get()
	except:
		print('Huh - no page found')
		continue
	try:
		existing_id = item_dict['claims']['P910']
		print('P910 exists, following that.')
		for clm2 in existing_id:
			wd_item = clm2.getTarget()
			item_dict = wd_item.get()
			print(wd_item.title())
	except:
		print('P910 not found')
	try:
		sitelink = item_dict['sitelinks']['commonswiki']
		print('Has sitelink')
	except:
		# No existing sitelink found, add the new one
		data = {'sitelinks': [{'site': 'commonswiki', 'title': category.title()}]}
		print("\n\n")
		# prettyPrint(item_dict)
		# print(data)
		print('https://commons.wikimedia.org/wiki/'+category.title().replace(' ','_'))
		print('https://www.wikidata.org/wiki/'+str(wd_item.title()))
		try:
			# text = input("Save? ")
			# if text == 'y':
			wd_item.editEntity(data, summary=u'Add commons sitelink based on interwiki on Commons')
			# 	continue
			# else:
			# 	continue
		except:
			print('Edit failed')

# EOF