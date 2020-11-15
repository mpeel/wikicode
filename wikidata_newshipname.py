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

maxnum = 10000
category = 'Category:Ships by IMO number'
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

def check_ship_cat(targetcat):
	counter = 0
	maincat_wd = 0
	print(targetcat.title())
	try:
		wd_item = pywikibot.ItemPage.fromPage(targetcat)
		item_dict = wd_item.get()
		print(wd_item.title())
		maincat_wd = 1
	except:
		print(targetcat.title())
		print('No Wikidata ID!')

	moved = 0
	for targetcat2 in pagegenerators.SubCategoriesPageGenerator(targetcat, recurse=False):
		print(targetcat2)
		try:
			wd_item2 = pywikibot.ItemPage.fromPage(targetcat2)
			item_dict2 = wd_item2.get()
			print('http://www.wikidata.org/wiki/'+str(wd_item2.title()))
			print(targetcat.title())
			if maincat_wd == 0:
				if debug:
					test = input('Move ID?')
				else:
					test = 'y'
				if test == 'y':
					data = {'sitelinks': [{'site': 'commonswiki', 'title': targetcat.title()}]}
					try:
						wd_item2.editEntity(data, summary=u'Use the IMO category as the commons sitelink')
					except:
						print("That didn't work")
						continue
				# repeat.append(targetcat)
				moved = 1
			continue
		except:
			null = 1

	if maincat_wd == 0 and moved == 0:
		try:
			query = 'SELECT ?item WHERE { ?item wdt:P458 ?id . FILTER (?id = "'+str(targetcat.title().replace('Category:IMO','').strip())+'") . } LIMIT 10'
			print(query)
			generator = pagegenerators.WikidataSPARQLPageGenerator(query, site=repo)
		except:
			print('Unable to run the query! Skipping this one.')
		count = 0
		for testpage in generator:
			wd_item = testpage
			count+=1
			print(count)
			if count == 1:
				item_dict = wd_item.get()
				qid = wd_item.title()
				print('http://www.wikidata.org/wiki/'+str(wd_item.title()))
				print('http://commons.wikimedia.org/wiki/'+str(targetcat.title().replace(' ','_')))
				if debug:
					test = input('Add to item?')
				else:
					test = 'y'
				if test != 'y':
					targetcat = False
				else:
					data = {'sitelinks': [{'site': 'commonswiki', 'title': targetcat.title()}]}
					try:
						wd_item.editEntity(data, summary=u'Add commons sitelink')
					except:
						print("That didn't work")
						continue
					maincat_wd = 1
		if count == 0:
			items = [['P31','Q11446']] # Instance of ship
			items.append(['P458',targetcat.title().replace('Category:IMO','').strip()]) # combines ship name

			print(items)
			print('http://commons.wikimedia.org/wiki/'+str(targetcat.title().replace(' ','_')))
			if debug:
				test = input('Create ship item - OK?')
			else:
				test = 'y'
			if test == 'y':
				wd_item = newitem(targetcat, items,cat=False)
				item_dict = wd_item.get()
				print(wd_item.title())
				maincat_wd = 1
				counter += 1



	# Work through the subcategories
	for targetcat2 in pagegenerators.SubCategoriesPageGenerator(targetcat, recurse=False):
		print(targetcat2)
		try:
			# See if we have an item already
			wd_item2 = pywikibot.ItemPage.fromPage(targetcat2)
			item_dict2 = wd_item2.get()
		except:
			if maincat_wd == 0:
				continue
			print('Hi')
			# Start assembling the Wikdata entry
			target_text = targetcat.get()
			items = [['P31','Q4167836']] # Instance of Wikimedia category
			items.append(['P971','Q56351075']) # combines ship name
			items.append(['P971',wd_item.title()]) # combines ship IMO

			print(items)
			if debug:
				test = input('OK?')
			else:
				test = 'y'
			if test != 'n':
				new_item = newitem(targetcat2, items)
				newclaim = pywikibot.Claim(repo, 'P7782')
				newclaim.setTarget(new_item)
				wd_item.addClaim(newclaim, summary=u'Setting P7782 value')
				counter += 1
	return counter

# Run through the categories
cat = pywikibot.Category(commons,category)
i = 0
j = 0
trip = 1
repeat = []
for target in pagegenerators.SubCategoriesPageGenerator(cat, recurse=False):
	j += 1
	print(j)
	# repeat.append(target)
	# print(len(repeat))
	# repeat_next = repeat.copy()
	# repeat = []
	# for targetcat in repeat_next:
	if trip == 0:
		if '5416565' in target.title():
			trip = 1
		else:
			continue
	else:
		trip = 1
	returnval = check_ship_cat(target)
	# if returnval != 0:
	# 	i += returnval
	# 	time.sleep(5)
	# 	i += check_ship_cat(target)

	if i > maxnum:
		exit()



