#!/usr/bin/python
# -*- coding: utf-8  -*-
# Create new Wikidata items
# Started 25 August 2018 by Mike Peel
# 3 November 2018 - focus on people for now
from __future__ import unicode_literals

import pywikibot
import numpy as np
import time
import string
from pywikibot import pagegenerators
from pywikibot.data import api
import urllib

commons = pywikibot.Site('commons', 'commons')
repo = commons.data_repository()  # this is a DataSite object

statedin = pywikibot.Claim(repo, u'P143')
itis = pywikibot.ItemPage(repo, "Q565")
statedin.setTarget(itis)
retrieved = pywikibot.Claim(repo, u'P813')
date = pywikibot.WbTime(year=2018, month=12, day=1)
retrieved.setTarget(date)

debug = False

def newitem(category, items,cat=True):
	new_item = pywikibot.ItemPage(repo)
	label = category.title()
	if cat == False:
		label = label.replace('Category:','')
	new_item.editLabels(labels={"en":label}, summary="Creating item")
	candidate_item = pywikibot.ItemPage(repo, new_item.getID())
	print(candidate_item)

	data = {'sitelinks': [{'site': 'commonswiki', 'title': category.title()}]}
	candidate_item.editEntity(data, summary=u'Add commons sitelink')

	for item in items:
		claim = pywikibot.Claim(repo, item[0])
		if item[0] == 'P458':
			claim.setTarget(item[1])
		else:
			claim.setTarget(pywikibot.ItemPage(repo, item[1]))
		try:
			candidate_item.addClaim(claim, summary=u'Setting '+item[0]+' value')
			# claim.addSources([statedin, retrieved], summary=u'Add source.')
		except:
			print("That didn't work")
	return candidate_item

query = 'SELECT DISTINCT ?item WHERE {	?item wdt:P3722 ?value . }'
if debug:
	query = query + " LIMIT 10"

print(query)

generator = pagegenerators.WikidataSPARQLPageGenerator(query, site=repo)

i = 0
j = 0
trip = 1
repeat = []
for target in generator:
	j += 1
	print(j)
	repeat.append(target)
	repeat_next = repeat.copy()
	repeat = []
	for wd_item in repeat_next:
		maincat_wd = 0
		print(wd_item.title())
		if trip == 0:
			if '5341813' in wd_item.title():
				trip = 1
			else:
				continue
		else:
			trip = 1

		item_dict = wd_item.get()

		try:
			P3722 = item_dict['claims']['P3722']
		except:
			print('No P3722')
			continue
		for clm in P3722:
			val = clm.getTarget()
			commonscat = u"Category:" + val
			print(commonscat)

			# See if we have an item there already
			existing_id = False
			try:
				commonscat_page = pywikibot.Page(commons, commonscat)
				wd_item2 = pywikibot.ItemPage.fromPage(commonscat_page)
				item_dict2 = wd_item2.get()
				print('http://www.wikidata.org/wiki/'+str(wd_item2.title()))
				existing_id = True
			except:
				null = 1

			if existing_id == False:
				# Start assembling the Wikdata entry
				commonscat_page = pywikibot.Page(commons, commonscat)
				items = [['P31','Q4167836']] # Instance of Wikimedia category
				items.append(['P971','Q4006']) # combines map
				items.append(['P971',wd_item.title()]) # combines main item

				print(items)
				# test = input('Create new item?')
				# if test != 'n':
				wd_item2 = newitem(commonscat_page, items)


			newclaim = pywikibot.Claim(repo, 'P7867')
			newclaim.setTarget(wd_item2)
			print(newclaim)
			# test = input('Save new P7867 value?')
			# if test == 'y':
			wd_item.addClaim(newclaim, summary=u'Setting P7867 value')
			wd_item.removeClaims(clm, summary=u"Remove obsolete P3722 value")
