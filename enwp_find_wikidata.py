#!/usr/bin/python
# -*- coding: utf-8  -*-
# Add enwp sitelinks based on commons categories
# Mike Peel     11-Jun-2020      v1 - start

from __future__ import unicode_literals

import pywikibot
import numpy as np
import time
import string
from pywikibot import pagegenerators
from pywikibot.data import api
import urllib
from pibot_functions import *
from database_login import *
from wir_newpages import *

wikidata_site = pywikibot.Site("wikidata", "wikidata")
repo = wikidata_site.data_repository()  # this is a DataSite object
commons = pywikibot.Site('commons', 'commons')
enwp = pywikibot.Site('en', 'wikipedia')
enwp_site = 'enwiki'
prefix = 'en'
# enwp = pywikibot.Site('simple', 'wikipedia')
# enwp_site = 'simplewiki'
# prefix = 'simple'
def newitem(category, enwp, items,commonscat_has_item=False):
	new_item = pywikibot.ItemPage(repo)
	new_item.editLabels(labels={"en":enwp.title()}, summary="Creating item")
	candidate_item = pywikibot.ItemPage(repo, new_item.getID())
	print(candidate_item)

	if commonscat_has_item:
		data = {'sitelinks': [{'site': 'commonswiki', 'title': category.title()}, {'site': enwp_site, 'title': enwp.title()}]}
		candidate_item.editEntity(data, summary=u'Add commons and '+enwp_site+' sitelink')
	else:
		data = {'sitelinks': [{'site': enwp_site, 'title': enwp.title()}]}
		candidate_item.editEntity(data, summary=u'Add '+enwp_site+' sitelink')


	for item in items:
		claim = pywikibot.Claim(repo, item[0])
		if item[0] == 'P569' or item[0] == 'P570':
			claim.setTarget(item[1])
		else:
			claim.setTarget(pywikibot.ItemPage(repo, item[1]))
		try:
			candidate_item.addClaim(claim, summary=u'Setting '+item[0]+' value')
			claim.addSources([statedin, retrieved], summary=u'Add source.')
		except:
			print("That didn't work")
	return

def search_entities(site, itemtitle):
	 params = { 'action' :'wbsearchentities', 
				'format' : 'json',
				'language' : 'en',
				'type' : 'item',
				'search': itemtitle}
	 request = api.Request(site=site, parameters=params)
	 return request.submit()

maxnum = 100000
nummodified = 0

debug = 1
trip = 0
newitems = 1

targetcats = ['Category:Articles_without_Wikidata_item']
# Also see https://www.wikidata.org/wiki/Wikidata:Metrics
# targetcats = ['Category:Short description with empty Wikidata description']
lang = 'en'

# for categories in range(0,2):
for targetcat in targetcats:
	cat = pywikibot.Category(enwp, targetcat)
	pages = pagegenerators.CategorizedPageGenerator(cat, recurse=False);
	# pages = enwp.querypage('UnconnectedPages')
	for page in pages:

		# Optional skip-ahead to resume broken runs
		if trip == 0:
			if "Mary" in page.title():
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
		# if not pageIsBiography(page=page, lang=lang):
		# 	print('Page is not a biography')

		# if authorIsNewbie(page=page, lang=lang):
		# 	print("Newbie author, checking quality...")
		# 	if pageIsRubbish(page=page, lang=lang) or \
		# 	   (not pageCategories(page=page, lang=lang)) or \
		# 	   (not pageReferences(page=page, lang=lang)) or \
		# 	   (not len(list(page.getReferences(namespaces=[0])))):
		# 		print("Page didnt pass minimum quality")

		# pagebirthyear = calculateBirthDate(page=page, lang=lang)
		# pagebirthyear = pagebirthyear and int(pagebirthyear.split('-')[0]) or ''
		# if not pagebirthyear:
		# 	print("Page doesnt have birthdate")

		# See if we have a Wikidata item already
		try:
			wd_item = pywikibot.ItemPage.fromPage(page)
			item_dict = wd_item.get()
			qid = wd_item.title()
			print("Has a sitelink already - " + qid)
			continue
		except:
			# If that didn't work, go no further
			print(page.title() + ' - no page found')
			wd_item = 0
			item_dict = 0
			qid = 0
			sitelink_check = 0
			# continue

		# If we're here, then we don't have one, see if we can add it through the commons category

		searchtag = page.title()
		try:
			searchtag = searchtag.split('(')[0].strip()
		except:
			null = 0
		wikidataEntries = search_entities(repo, searchtag)
		# print(wikidataEntries)
		data = {'sitelinks': [{'site': enwp_site, 'title': page.title()}]}
		# print(wikidataEntries['searchinfo'])
		done = 0
		if wikidataEntries['search'] != []:
			results = wikidataEntries['search']
			# prettyPrint(results)
			numresults = len(results)
			if numresults > 5:
				print('More than 5 candidates, bot would skip')
			for i in range(0,numresults):
				if done != 0:
					continue
				targetpage = pywikibot.ItemPage(wikidata_site, results[i]['id'])
				try:
					item_dict = targetpage.get()
				except:
					continue
				# print(item_dict)
				sitelink = ''
				try:
					sitelink = item_dict['sitelinks'][enwp_site]
				except:
					null = 0
				if sitelink == '':
					print('http://www.wikidata.org/wiki/'+results[i]['id'])
					try:
						print(item_dict['labels']['en'])
					except:
						print('')
					try:
						print(item_dict['descriptions']['en'])
					except:
						print('')
					print('http://'+prefix+'.wikipedia.org/wiki/' + page.title().replace(' ','_'))
					text = input("Save? ")
					if text != 'n':
						targetpage.editEntity(data, summary=u'Add enwp sitelink')
						done = 1

		if done == 0 and newitems == 1:
			text = input('Create a new item?')
			if text != 'n':
				# Start assembling the Wikdata entry
				items = []
				new_item = pywikibot.ItemPage(repo)
				new_item.editLabels(labels={"en":page.title()}, summary="Creating item")
				itemfound = pywikibot.ItemPage(repo, new_item.getID())
				data = {'sitelinks': [{'site': enwp_site, 'title': page.title()}]}
				itemfound.editEntity(data, summary=u'Add '+enwp_site+' sitelink')
				text = input('Is it a bio?')
				if text != 'n':
					addBiographyClaims(repo=repo, wikisite=enwp, item=itemfound, page=page, lang=lang)


# EOF