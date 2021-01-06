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
from pibot_functions import *

maxnum = 1000
nummodified = 0

wikidata_site = pywikibot.Site("wikidata", "wikidata")
repo = wikidata_site.data_repository()  # this is a DataSite object
commons = pywikibot.Site('commons', 'commons')
enwp = pywikibot.Site('en', 'wikipedia')
debug = 1
trip = 1
templates = ['Commons cat', 'commons cat', 'Commons category', 'commons category']
targetcat = 'Category:Commons category link is on Wikidata using P373'
cat = pywikibot.Category(enwp, targetcat)
# subcats = pagegenerators.SubCategoriesPageGenerator(cat, recurse=False);
# for page in subcats:
pages = pagegenerators.CategorizedPageGenerator(cat, recurse=False);
for page in pages:
	if trip == 0:
		if "Category:South" in page.title():
			trip = 1
		else:
			print page.title()
			continue
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
	print page.title()

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
		sitelink = get_sitelink_title(item_dict['sitelinks']['commonswiki'])
		sitelink_check = 1
	except:
		sitelink_check = 0
	# Only attempt to do this if there is no existing sitelink
	if sitelink_check == 0:
		print sitelink_check
		id_val = 0
		target_text = page.get()
		for i in range(0,len(templates)):
			print templates[i]
			try:
				print templates[i]
				value = (target_text.split("{{"+templates[i]+"|"))[1].split("}}")[0]
				print value
				if value and id_val == 0:
					id_val = value
			except:
				null = 1
			try:
				print templates[i]
				value = (target_text.split("{{"+templates[i]+"|"))[1].split("|")[0]
				print value
				if value and id_val == 0:
					id_val = value
			except:
				null = 1
		
		if id_val != 0:
			if 'Category:' not in id_val:
				commonscat = u"Category:" + id_val
			else:
				commonscat = id_val
			print commonscat
			# exit()
			# The commons category must already exist
			try:
				sitelink_page = pywikibot.Page(commons, commonscat)
			except:
				print 'Found a bad sitelink'
				# clm.changeTarget("", summary=u"Remove non-functional value of P373")
			else:
				# Check the category to see if it already has a Wikidata item
				try:
					commonscat_page = pywikibot.Page(commons, commonscat)
					wd_item = pywikibot.ItemPage.fromPage(commonscat_page)
					wd_item.get()
				except:
					try:
						text = commonscat_page.get()
					except:
						print 'Commons category does not exist - fix that?'
						text = raw_input("Continue? ")
						continue

					if '{{Disambig' not in text and '{{disambig' not in text and '{{Category redirect' not in text and '{{category redirect' not in text:
						# That didn't work, add it to the Wikidata entry
						data = {'sitelinks': [{'site': 'commonswiki', 'title': commonscat}]}
						try:
							print id_val
							print data
							print page.title()
							text = raw_input("Save? ")
							if text == 'y':
								wd_item.editEntity(data, summary=u'Add commons sitelink from the English Wikipedia')
								nummodified += 1
							print nummodified
						except:
							print 'Edit failed'

	if nummodified >= maxnum:
		print 'Reached the maximum of ' + str(maxnum) + ' entries modified, quitting!'
		exit()

print 'Done! Edited ' + str(nummodified) + ' entries'
		
# EOF