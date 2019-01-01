#!/usr/bin/python
# -*- coding: utf-8  -*-
# Remove locally defined commons category links when bad or pointing to a redirect
# Mike Peel     01-Jan-2019      v1 - start

from __future__ import unicode_literals

import pywikibot
import numpy as np
import time
import string
from pywikibot import pagegenerators
import urllib
import mysql.connector
from database_login import *

maxnum = 1
nummodified = 0
categories = 1

wikidata_site = pywikibot.Site("wikidata", "wikidata")
repo = wikidata_site.data_repository()  # this is a DataSite object
commons = pywikibot.Site('commons', 'commons')
enwp = pywikibot.Site('en', 'wikipedia')
debug = 1
trip = 1
templates = ['commonscat', 'Commonscat', 'commonscategory', 'Commonscategory', 'commons category', 'Commons category', 'commons cat', 'Commons cat', 'Commons category-inline', 'commons category-inline', 'Commons cat-inline', 'commons cat-inline', 'commonscat-inline', 'Commonscat-inline']

catredirect_templates = ["category redirect", "Category redirect", "seecat", "Seecat", "see cat", "See cat", "categoryredirect", "Categoryredirect", "catredirect", "Catredirect", "cat redirect", "Cat redirect", "catredir", "Catredir", "redirect category", "Redirect category", "cat-red", "Cat-red", "redirect cat", "Redirect cat", "category Redirect", "Category Redirect", "cat-redirect", "Cat-redirect"]

targetcat = 'Category:Commons category link is locally defined'
cat = pywikibot.Category(enwp, targetcat)

if categories:
	pages = pagegenerators.SubCategoriesPageGenerator(cat, recurse=False);
else:
	pages = pagegenerators.CategorizedPageGenerator(cat, recurse=False);
for page in pages:

	# Optional skip-ahead to resume broken runs
	if trip == 0:
		if "Category:Al-Nasr SC (Dubai)" in page.title():
			trip = 1
		else:
			print page.title()
			continue

	# Cut-off at a maximum number of edits	
	print ""
	print nummodified
	if nummodified >= maxnum:
		print 'Reached the maximum of ' + str(maxnum) + ' entries modified, quitting!'
		exit()

	# Get the Wikidata item
	try:
		wd_item = pywikibot.ItemPage.fromPage(page)
		item_dict = wd_item.get()
		qid = wd_item.title()
	except:
		# If that didn't work, go no further
		print page.title() + ' - no page found'
		continue

	print "\n" + qid
	print page.title()

	# Get the candidate commonscat link
	target_text = page.get()
	id_val = 0
	abort = 0
	commonscat_string = ""
	for i in range(0,len(templates)):
		try:
			value = (target_text.split("{{"+templates[i]+"|"))[1].split("}}")[0]
			if value and id_val == 0:
				id_val = value
				commonscat_string = "{{"+templates[i]+"|"+id_val+"}}"
				commonscat_string2 = "|"+id_val
				commonscat_string2a = "{{"+templates[i]
		except:
			null = 1
			try:
				value = (target_text.split("{{"+templates[i]+" |1="))[1].split("}}")[0]
				if value and id_val == 0:
					id_val = value
					commonscat_string = "{{"+templates[i]+"|1="+id_val+"}}"
					commonscat_string2 = "|1="+id_val
					commonscat_string2a = "{{"+templates[i]
			except:
				null = 2
	if id_val == 0:
		# We didn't find the commons category link, skip this one.
		continue

	# Do some tidying of the link
	if "|" in id_val:
		id_val = id_val.split("|")[0]
	try:
		id_val = id_val.strip()
	except:
		null = 1
	print id_val
	commonscat = u"Category:" + id_val

	# If we have a P910 value, switch to using that Wikidata item
	try:
		existing_id = item_dict['claims']['P910']
		print 'P910 exists, following that.'
		for clm2 in existing_id:
			wd_item = clm2.getTarget()
			item_dict = wd_item.get()
			print wd_item.title()
	except:
		null = 0

	# Double-check that there is a sitelink on Wikidata
	try:
		sitelink = item_dict['sitelinks']['commonswiki']
		sitelink_check = 1
	except:
		sitelink_check = 0
	print "sitelink: " + str(sitelink_check)

	# If we don't have a sitelink on Wikidata, let's at least check that the enwp one exists
	if id_val != 0 and sitelink_check == 0:
		try:
			commonscat_page = pywikibot.Page(commons, commonscat)
			text = commonscat_page.get()
		except:
			print 'Found a bad sitelink - removing it'
			target_text = target_text.replace(commonscat_string+"\n", '')
			target_text = target_text.replace(commonscat_string, '')
			page.text = target_text
			test = 'y'
			savemessage = "Removing Commons category ("+id_val+") as it does not exist"
			if debug == 1:
				print target_text
				print "Removing Commons link from " + page.title()
				print savemessage
				test = raw_input("Continue? ")
			if test == 'y':
				nummodified += 1
				page.save(savemessage)
				continue

	# Only attempt to do the next part if we have a commons category link both locally and on wikidata
	if id_val != 0 and sitelink_check == 1:

		# First, fix broken commons category links
		try:
			commonscat_page = pywikibot.Page(commons, commonscat)
			category_text = commonscat_page.get()
		except:
			print 'Found a bad sitelink, but there is one on wikidata we can use'
			target_text = target_text.replace(commonscat_string2a + commonscat_string2, commonscat_string2a)
			page.text = target_text
			test = 'y'
			savemessage = "Removing locally defined but non-existent Commons category ("+id_val+") to use the one from Wikidata"
			if debug == 1:
				print target_text
				print "Removing locally-defined commons link from " + page.title()
				print savemessage
				test = raw_input("Continue? ")
			if test == 'y':
				nummodified += 1
				page.save(savemessage)
				continue
		
		# Now check to see if the local one is a redirect to the wikidata one
		if 'Category:'+id_val != sitelink:
			sitelink_redirect = ''
			for option in catredirect_templates:
				if "{{" + option in category_text:
					try:
						sitelink_redirect = (category_text.split("{{" + option + "|"))[1].split("}}")[0]
					except:
						try:
							sitelink_redirect = (category_text.split("{{" + option + " |"))[1].split("}}")[0]
						except:
							print 'Wikitext parsing issue!'
					sitelink_redirect = sitelink_redirect.replace(u":Category:","").strip()
					sitelink_redirect = sitelink_redirect.replace(u"Category:","").strip()
			if sitelink_redirect != '':
				if sitelink == sitelink_redirect:
					print 'We have a redirect to the Wikidata entry, so use the wikidata entry'
					target_text = target_text.replace(commonscat_string2a + commonscat_string2, commonscat_string2a)
					page.text = target_text
					test = 'y'
					savemessage = "Removing locally defined Commons category ("+id_val+") as it points to a redirect - use the one from Wikidata instead"
					if debug == 1:
						print target_text
						print "Removing locally-defined commons link from " + page.title()
						print savemessage
						test = raw_input("Continue? ")
					if test == 'y':
						nummodified += 1
						page.save(savemessage)
						continue

		# What if it is pointing at a disambig page?
		if '{{Disambig' in target_text or '{{disambig' in target_text:
			if sitelink in target_text:
				print 'We have a disambig category, so use the wikidata entry'
				target_text = target_text.replace(commonscat_string2, '')
				page.text = target_text
				test = 'y'
				savemessage = "Removing locally defined Commons category ("+id_val+") as it points to a disambiguation page - use the one from Wikidata instead"
				if debug == 1:
					print target_text
					print "Removing locally-defined commons link from " + page.title()
					print savemessage
					test = raw_input("Continue? ")
				if test == 'y':
					nummodified += 1
					page.save()
					continue

		# ... That's all for now

print 'Done! Edited ' + str(nummodified) + ' entries'
		
# EOF