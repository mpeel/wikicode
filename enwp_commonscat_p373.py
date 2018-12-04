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

maxnum = 1000
nummodified = 0

wikidata_site = pywikibot.Site("wikidata", "wikidata")
repo = wikidata_site.data_repository()  # this is a DataSite object
commons = pywikibot.Site('commons', 'commons')
enwp = pywikibot.Site('en', 'wikipedia')
debug = 1

targetcat = 'Category:Commons category link is on Wikidata using P373'
cat = pywikibot.Category(enwp, targetcat)
# subcats = pagegenerators.SubCategoriesPageGenerator(cat, recurse=False);
# for page in subcats:
pages = pagegenerators.CategorizedPageGenerator(cat, recurse=False);
for page in pages:
	try:
		# item_dict = page.get()
		# qid = page.title()
		wd_item = pywikibot.ItemPage.fromPage(page)
		item_dict = wd_item.get()
		qid = wd_item.title()
	except:
		print 'Huh - no page found'
		continue
	# print item_dict
	# exit()

	print "\n" + qid
	try:
		p373 = item_dict['claims']['P373']
	except:
		print 'Huh - no P373 found'
		continue
	p373_check = 0
	for clm in p373:
		p373_check += 1

	# If we have a P910 value, switch to using that item
	try:
		existing_id = item_dict['claims']['P910']
		print 'P910 exists, following that.'
		for clm2 in existing_id:
			wd_item = clm2.getTarget()
			item_dict = wd_item.get()
			print wd_item.title()
	except:
		null = 0

	# Double-check that we don't already have a sitelink
	try:
		sitelink = item_dict['sitelinks']['commonswiki']
		sitelink_check = 1
	except:
		sitelink_check = 0
	# Only attempt to do this if there is only one value for P373 and no existing sitelink
	if p373_check == 1 and sitelink_check == 0:
		for clm in p373:
			val = clm.getTarget()
			commonscat = u"Category:" + val
			# The commons category must already exist
			try:
				sitelink_page = pywikibot.Page(commons, commonscat)
			except:
				print 'Found a bad sitelink'
				# clm.changeTarget("", summary=u"Remove non-functional value of P373")
			else:
				# Check the category to see if it already has a Wikidata item
				commonscat_page = pywikibot.Page(commons, commonscat)
				try:
					wd_item = pywikibot.ItemPage.fromPage(commonscat_page)
					wd_item.get()
				except:

					# That didn't work, add it to the Wikidata entry
					data = {'sitelinks': [{'site': 'commonswiki', 'title': u"Category:" + val}]}
					try:
						print val
						print data
						# text = raw_input("Save? ")
						# if text == 'y':
						wd_item.editEntity(data, summary=u'Copy from P373 to commons sitelink')
						nummodified += 1
						print nummodified
					except:
						print 'Edit failed'

			if nummodified >= maxnum:
				print 'Reached the maximum of ' + str(maxnum) + ' entries modified, quitting!'
				exit()

print 'Done! Edited ' + str(nummodified) + ' entries'
		
# EOF