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
from database_login import *
import time

maxnum = 10000000
nummodified = 0

wikidata_site = pywikibot.Site("wikidata", "wikidata")
repo = wikidata_site.data_repository()  # this is a DataSite object
commons = pywikibot.Site('commons', 'commons')
enwp = pywikibot.Site('en', 'wikipedia')
# enwp = pywikibot.Site('es', 'wikipedia')
debug = 1
trip = 1


# New style of category walker
numchecked = 0
catschecked = 0
do_articles = True
do_subcats = True

targetcats = []
# targetcats = ['Category:Aircraft by manufacturer']
# targetcats = ['Category:Astronomy']
# targetcats = ['Category:Science']
#targetcats = ['Category:Canary Islands']
#targetcats = ['Categoría:Canarias']
# targetcats = ['Category:2019–20 coronavirus pandemic']
# targetcats = ['Category:Commons category link is on Wikidata using P373']
targetcats = ['Category:Commons category link is locally defined']
# targetcats = ['Category:Commons link is the pagename','Category:Commons link is defined as the pagename']
# targetcats = ['Category:Commons link is locally defined']
targettemplates = []
# targettemplates = ['Commons']

subcats = False

catredirect_templates = ["category redirect", "Category redirect", "seecat", "Seecat", "see cat", "See cat", "categoryredirect", "Categoryredirect", "catredirect", "Catredirect", "cat redirect", "Cat redirect", "catredir", "Catredir", "redirect category", "Redirect category", "cat-red", "Cat-red", "redirect cat", "Redirect cat", "category Redirect", "Category Redirect", "cat-redirect", "Cat-redirect"]


def findmatch(page):
	# Get the Wikidata entry
	try:
		wd_item = pywikibot.ItemPage.fromPage(page)
		item_dict = wd_item.get()
		qid = wd_item.title()
		print('\n'+page.title())
		print(qid)
	except:
		# If that didn't work, go no further
		print('\n'+page.title() + ' - no page found')
		return 0

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

	# Double-check that there is no a sitelink on Wikidata
	try:
		sitelink = item_dict['sitelinks']['commonswiki']
		sitelink_check = 1
	except:
		sitelink_check = 0
	print("sitelink: " + str(sitelink_check))
	if sitelink_check == 1:
		return 0

	# See if we can get a Commons page with the same name
	try:
		if 'Category:' in page.title():
			commonscat_page = pywikibot.Page(commons, page.title())
		else:
			commonscat_page = pywikibot.Page(commons, 'Category:'+page.title())
		category_text = commonscat_page.get()
	except:
		try:
			if 'Category:' in page.title():
				commonscat_page = pywikibot.Page(commons, page.title()[:-1])
			else:
				commonscat_page = pywikibot.Page(commons, 'Category:'+page.title()[:-1])
			category_text = commonscat_page.get()
		except:
			print('No match found')
			return 0

	if any(option in category_text for option in catredirect_templates):
		print('Redirect page')
		return 0

	# See if it already has a Wikidata item
	test = 0
	try:
		wd_item2 = pywikibot.ItemPage.fromPage(commonscat_page)
		item_dict2 = wd_item2.get()
		qid2 = wd_item2.title()
		print(qid)
		test = 1
	except:
		# If that didn't work, go no further
		print(commonscat_page.title() + ' - no linked Wikidata item found')
	if test != 0:
		print('Commons has Wikidata ID already')
		input('Check?')
		return 0

	print(' http://en.wikipedia.org/wiki/'+page.title().replace(' ','_'))
	print(' http://commons.wikimedia.org/wiki/'+commonscat_page.title().replace(' ','_'))
	print(category_text)
	test = 'y'
	# test = input("Continue? ")

	if test != 'n':
		# Add the sitelink
		data = {'sitelinks': [{'site': 'commonswiki', 'title': commonscat_page.title()}]}
		try:
			print(data)
			if debug == 1:
				text = input("Save sitelink? ")
			else:
				text = 'y'
			if text == 'y':
				wd_item.editEntity(data, summary=u'Add Commons category sitelink from name matching')
		except:
			print('Edit failed')


		if debug == 1:
			# Remove any bad P373 values
			try:
				p373 = item_dict['claims']['P373']
				for clm in p373:
					val = clm.getTarget()
					p373cat = u"Category:" + val
					print('Remove P373?')
					print(' http://www.wikidata.org/wiki/'+qid)
					print(' ' + str(p373cat))
					test = 'y'
					savemessage = 'Remove incorrect P373 value'
					if debug == 1:
						print(savemessage)
						test = input("Continue? ")
					if test == 'y':
						wd_item.removeClaims(clm,summary=savemessage)
			except:
				null = 0
	return 1

if len(targetcats) > 0:
	seen   = set(targetcats)
	active = set(targetcats)
	while active:
		next_active = set()
		for item in sorted(active):
			cat = pywikibot.Category(enwp,item)
			if do_articles:
				for result in pagegenerators.CategorizedPageGenerator(cat, recurse=False):
					nummodified += findmatch(result)
			nummodified += findmatch(cat)
			numchecked += 1
			print(str(nummodified) + " - " + str(numchecked) + "/" + str(len(seen)) + "/" + str(len(active)) + "/" + str(len(next_active)))

			if do_subcats:
				do_subcats = subcats
				# See if there are subcategories that we want to check in the future
				for result in pagegenerators.SubCategoriesPageGenerator(cat, recurse=False):
					if result.title() not in seen:
						seen.add(result.title())
						next_active.add(result.title())
		active = next_active
		if nummodified >= maxnum:
			print('Reached the maximum of ' + str(maxnum) + ' entries modified, quitting!')
			break
elif len(targettemplates) > 0:
	for tpl in targettemplates:
		template = pywikibot.Page(enwp, 'Template:'+tpl)
		# targetcats = template.embeddedin(namespaces='14')
		targetcats = template.embeddedin(namespaces='0')
		for target in targetcats:
			nummodified += findmatch(target)
			if nummodified >= maxnum:
				print('Reached the maximum of ' + str(maxnum) + ' entries modified, quitting!')
				break

else:
	# Pick random categories
	while nummodified < maxnum:
		# targets = pagegenerators.RandomPageGenerator(total=100, site=enwp, namespaces='14')
		targets = pagegenerators.RandomPageGenerator(total=100, site=enwp, namespaces='0')
		for target in targets:
			print(target.title())
			nummodified += findmatch(target)
			# print(nummodified)
			
			if nummodified >= maxnum:
				print('Reached the maximum of ' + str(maxnum) + ' entries modified, quitting!')
				break


print('Done! Edited ' + str(nummodified) + ' entries')
		
# EOF