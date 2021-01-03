#!/usr/bin/python
# -*- coding: utf-8  -*-
# Create new Wikidata items for enwp articles and categories
# Mike Peel     03-Jan-2021      v1 - start

import pywikibot
import numpy as np
import time
import string
from pywikibot import pagegenerators
from pywikibot.data import api
import urllib
from pibot_functions import *
from wir_newpages import *

wikidata_site = pywikibot.Site("wikidata", "wikidata")
repo = wikidata_site.data_repository()  # this is a DataSite object

wikipedias = [['en','Category']]

maxnum = 100000
nummodified = 0
days_since_last_edit = 1.0
days_since_last_edit_but_search = 7.0
days_since_creation = 14.0

debug = True

def search_entities(site, itemtitle):
	 params = { 'action' :'wbsearchentities', 
				'format' : 'json',
				'language' : 'en',
				'type' : 'item',
				'search': itemtitle}
	 request = api.Request(site=site, parameters=params)
	 return request.submit()

for settings in wikipedias:
	prefix = settings[0]
	wikipedia = pywikibot.Site(prefix, 'wikipedia')
	pages = wikipedia.querypage('UnconnectedPages')

	for page in pages:
		# Articles and categories only
		if ':' in page.title() and settings[1]+':' not in page.title():
			continue
		if settings[1] not in page.title():
			continue

		# Exclude redirects
		if page.isRedirectPage():
			continue

		print("\n" + "http://"+prefix+".wikipedia.org/wiki/"+page.title().replace(' ','_'))

		# Check if we have a Wikidata item already
		try:
			wd_item = pywikibot.ItemPage.fromPage(page)
			item_dict = wd_item.get()
			qid = wd_item.title()
			print("Has a sitelink already - " + qid)
			continue
		except:
			print(page.title() + ' - no page found')

		# Check for the last edit time
		lastedited = page.editTime()
		lastedited_time = (datetime.datetime.now() - lastedited).seconds/(60*60*24)
		if lastedited_time < days_since_last_edit:
			print('Recently edited ('+str(lastedited_time)+')')
			continue

		# Check for the creation time
		edits = page.revisions(reverse=True,total=1)
		for edit in edits:
			# print(edit)
			difftime = datetime.datetime.now() - edit.timestamp
			if difftime.seconds/(60*60*24) < days_since_creation:
				print('Recently created ('+str(difftime.seconds/(60*60*24))+')')
				continue

		# See if search returns any items
		wikidataEntries = search_entities(repo, page.title())
		if wikidataEntries['search'] != []:
			if lastedited_time < days_since_last_edit_but_search:
				print('Recently edited with search results ('+str(lastedited_time)+')')
				continue

		# If we're here, then create a new item
		data = {'labels': {prefix: page.title()}, 'sitelinks': [{'site': prefix+'wiki', 'title': page.title()}]}
		test = 'y'
		if debug:
			print(data)
			test = input('Continue?')
		if test == 'y':
			new_item = pywikibot.ItemPage(repo)
			new_item.editEntity(data, summary="Creating item from " + prefix +"wiki")
			nummodified += 1
			if settings[1] in page.title():
				# We have a category, also add a P31 value
				claim = pywikibot.Claim(repo,'P31')
				claim.setTarget(pywikibot.ItemPage(repo, 'Q4167836'))
				new_item.addClaim(claim, summary='Category item')

		# Cut-off at a maximum number of edits	
		print("")
		print(nummodified)
		if nummodified >= maxnum:
			print('Reached the maximum of ' + str(maxnum) + ' entries modified, quitting!')
			exit()

# EOF