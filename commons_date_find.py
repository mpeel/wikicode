#!/usr/bin/python
# -*- coding: utf-8  -*-
# Match Commons date categories with Wikidata items
# Mike Peel     11-Oct-2021      v1 - start

import pywikibot
import numpy as np
import time
import string
from pywikibot import pagegenerators
from pywikibot.data import api
import urllib
import random

# Settings
targetcat = 'Category:Days by day'
maxnum = 100
nummodified = 0
debug = 0
trip = 1

# Sites
wikidata_site = pywikibot.Site("wikidata", "wikidata")
repo = wikidata_site.data_repository()  # this is a DataSite object
commons = pywikibot.Site('commons', 'commons')

# Functions
def search_entities(site, itemtitle):
	 params = { 'action' :'wbsearchentities',
				'format' : 'json',
				'language' : 'en',
				'type' : 'item',
				'search': itemtitle}
	 request = api.Request(site=site, parameters=params)
	 return request.submit()

def do_date_find(page):
	print(page.title())
	# See if we have a Wikidata item already
	try:
		wd_item = pywikibot.ItemPage.fromPage(page)
		item_dict = wd_item.get()
		qid = wd_item.title()
		print("Has a sitelink already - https://www.wikidata.org/wiki/" + qid)
		return 0
	except:
		wd_item = 0
		item_dict = 0
		qid = 0
		sitelink_check = 0
		# continue

	# If we're here, we don't - search for a match.
	print('Searching for a match...')
	months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
	date = page.title().replace('Category:','')
	date = date.split('-')
	print(date)
	if len(date) != 3:
		print('Something odd happened, skipping')
		print(date)
		return 0

	day = date[2]
	if day[0] == '0':
		day = day[1]
	datestr = months[int(date[1])-1] + ' ' + str(day) + ', ' + str(date[0])
	print(datestr)

	wikidataEntries = search_entities(repo, datestr)
	if wikidataEntries['search'] != []:
		results = wikidataEntries['search']
		numresults = len(results)
		for i in range(0,numresults):
			targetpage = pywikibot.ItemPage(wikidata_site, results[i]['id'])
			item_dict = targetpage.get()
			print('http://www.wikidata.org/wiki/'+results[i]['id'])

			# Make sure we don't have a sitelink already
			sitelink_check = False
			try:
				sitelink = get_sitelink_title(item_dict['sitelinks']['commonswiki'])
				print('http://commons.wikimedia.org/wiki/'+sitelink.replace(' ','_'))
				sitelink_check = True
			except:
				pass
			if sitelink_check:
				print('Has sitelink')
				continue

			calday = False
			P31 = ''
			try:
				P31 = item_dict['claims']['P31']
			except:
				print('No P31, skipping')
				return 0
			if P31 != '':
				for clm in P31:
					# print(clm)
					# print(clm.getTarget().title())
					if clm.getTarget().title() == 'Q47150325':
						calday = True
			if not calday:
				print('Not a calendar day, skipping')
				return 0
			try:
				print(item_dict['labels']['en'])
			except:
				print('')
			print('http://commons.wikimedia.org/wiki/'+page.title().replace(' ','_'))
			text = 'y'
			if debug:
				text = input("Save? ")
			if text != 'n':
				data = {'sitelinks': [{'site': 'commonswiki', 'title': page.title()}]}
				targetpage.editEntity(data, summary=u'Add commons sitelink')
				return 1

	# If we're here, it hasn't worked, return 0
	return 0

# Run through the category contents
cat = pywikibot.Category(commons, targetcat)
for result in pagegenerators.SubCategoriesPageGenerator(cat, recurse=False):
	if trip == 0:
		if 'Category:2000' not in result.title():
			continue
		else:
			trip = 1
	nummodified += do_date_find(result)
	if nummodified >= maxnum:
		print('Reached the maximum of ' + str(maxnum) + ' entries modified, quitting!')
		break

# EOF
