#!/usr/bin/python
# -*- coding: utf-8  -*-
# Create new Wikidata items for enwp articles and categories
# Mike Peel     02-Nov-2020      v1 - start

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
enwp = pywikibot.Site('en', 'wikipedia')
enwp_site = 'enwiki'
prefix = 'en'

def newitem(category, enwp, items,commonscat_has_item=False):
	new_item = pywikibot.ItemPage(repo)
	new_item.editLabels(labels={"en":enwp.title()}, summary="Creating item")
	candidate_item = pywikibot.ItemPage(repo, new_item.getID())

	for item in items:
		claim = pywikibot.Claim(repo, item[0])
		try:
			candidate_item.addClaim(claim, summary=u'Setting '+item[0]+' value')
			claim.addSources([statedin, retrieved], summary=u'Add source.')
		except:
			print("That didn't work")
	return

maxnum = 100000
nummodified = 0

debug = 1
trip = 1

pages = enwp.querypage('UnconnectedPages')
for page in pages:
	# Articles and categories
	if ':' not in page.title() and 'Category:' not in page.title():
		continue

	# Optional skip-ahead to resume broken runs
	if trip == 0:
		if "AK-19" in page.title():
			trip = 1
		else:
			print(page.title())
			continue

	# Cut-off at a maximum number of edits	
	print("")
	print(nummodified)
	if nummodified >= maxnum:
		print('Reached the maximum of ' + str(maxnum) + ' entries modified, quitting!')
		exit()

	print("\n" + "http://en.wikipedia.org/wiki/"+page.title().replace(' ','_'))
	if 'Articles for deletion' in page.title():
		continue
	if page.isRedirectPage():
		continue

	# See if we have a Wikidata item already
	try:
		wd_item = pywikibot.ItemPage.fromPage(page)
		item_dict = wd_item.get()
		qid = wd_item.title()
		print("Has a sitelink already - " + qid)
		continue
	except:
		print(page.title() + ' - no page found')

	# Check for the article/category age

	# Create it?

	if done == 0 and newitems == 1:
		text = input('Create a new bio item?')
		if text != 'n':
			# Start assembling the Wikdata entry
			items = []
			new_item = pywikibot.ItemPage(repo)
			new_item.editLabels(labels={"en":page.title()}, summary="Creating item")
			itemfound = pywikibot.ItemPage(repo, new_item.getID())
			data = {'sitelinks': [{'site': enwp_site, 'title': page.title()}]}
			itemfound.editEntity(data, summary=u'Add '+enwp_site+' sitelink')
			addBiographyClaims(repo=repo, wikisite=enwp, item=itemfound, page=page, lang=lang)


# EOF