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
date = pywikibot.WbTime(year=2020, month=3, day=11)
retrieved.setTarget(date)

maxnum = 100

def search_entities(site, itemtitle):
	 params = { 'action' :'wbsearchentities', 
				'format' : 'json',
				'language' : 'en',
				'type' : 'item',
				'search': itemtitle}
	 request = api.Request(site=site, parameters=params)
	 return request.submit()

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

# category = 'Category:Ships by IMO number'
# cat = pywikibot.Category(commons,category)
i = 0
trip = 1
template = pywikibot.Page(commons, 'Template:IWM')
targetcats = template.embeddedin(namespaces='14')
for targetcat in targetcats:
	if trip == 0:
		if targetcat.title() == 'Category:Even Aas':
			trip = 1
		else:
			continue
	else:
		trip = 1

	try:
		wd_item = pywikibot.ItemPage.fromPage(targetcat)
		item_dict = wd_item.get()
		print(wd_item.title())
		continue
	except:
		print(targetcat.title())

	# Also search for other matches
	searchname = targetcat.title().replace('Category:','')
	searchname2 = searchname.split('(', 1)[0]
	if searchname2 != '':
		searchname = searchname2
	wikidataEntries = search_entities(repo, searchname)
	print(wikidataEntries)
	abort = 0
	if wikidataEntries['search'] != []:
		results = wikidataEntries['search']
		# prettyPrint(results)
		numresults = len(results)
		for i in range(0,numresults):
			abort = 1
	# if abort == 1:
	# 	continue

	# Start assembling the Wikdata entry
	target_text = targetcat.get()
	items = [['P31','Q575759']]
	print(items)
	# test = input('OK?')
	# if test == 'y':
	test = newitem(targetcat, items,cat=False)
	i += 1
	if i > maxnum:
		exit()
