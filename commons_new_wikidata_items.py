#!/usr/bin/python
# -*- coding: utf-8  -*-
# Create new Wikidata items based on Commons categories
# Mike Peel     13-Jun-2020      v1 - start

from __future__ import unicode_literals

import pywikibot
import numpy as np
import time
import string
from pywikibot import pagegenerators
from pywikibot.data import api
import urllib
import random

wikidata_site = pywikibot.Site("wikidata", "wikidata")
repo = wikidata_site.data_repository()  # this is a DataSite object
commons = pywikibot.Site('commons', 'commons')

def newitem(category, items):
	new_item = pywikibot.ItemPage(repo)
	if items != []:
		new_item.editLabels(labels={"en":category.title()}, summary="Creating item")
	else:
		new_item.editLabels(labels={"en":category.title().replace('Category:','')}, summary="Creating item")
	candidate_item = pywikibot.ItemPage(repo, new_item.getID())
	print(candidate_item)

	data = {'sitelinks': [{'site': 'commonswiki', 'title': category.title()}]}
	candidate_item.editEntity(data, summary=u'Add commons sitelink')

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

def search_entities_es(site, itemtitle):
	 params = { 'action' :'wbsearchentities', 
				'format' : 'json',
				'language' : 'es',
				'type' : 'item',
				'search': itemtitle}
	 request = api.Request(site=site, parameters=params)
	 return request.submit()

maxnum = 100000
nummodified = 0

debug = 1
trip = 1
catredirect_templates = ["category redirect", "Category redirect", "seecat", "Seecat", "see cat", "See cat", "categoryredirect", "Categoryredirect", "catredirect", "Catredirect", "cat redirect", "Cat redirect", "catredir", "Catredir", "redirect category", "Redirect category", "cat-red", "Cat-red", "redirect cat", "Redirect cat", "category Redirect", "Category Redirect", "cat-redirect", "Cat-redirect"]


def do_check(page,create=True, search=True):
	print(page.title())
	# See if we have a Wikidata item already
	try:
		wd_item = pywikibot.ItemPage.fromPage(page)
		item_dict = wd_item.get()
		qid = wd_item.title()
		print("Has a sitelink already - https://www.wikidata.org/wiki/" + qid)
		# If we have a P910 value, switch to using that item
		try:
			existing_id = item_dict['claims']['P301']
			print('P301 exists, following that.')
			for clm2 in existing_id:
				page2 = clm2.getTarget()
				item_dict = page2.get()
				print(page2.title())
		except:
			null = 0
		print('Hi')
		iscat = False
		# print(item_dict['claims']['P31'])
		try:
			if '4167836' in str(item_dict['claims']['P31']):
				iscat = True
				print('Is cat')
		except:
			iscat = False
		ishuman = False
		try:
			test = item_dict['claims']['P21']
			ishuman = True
			print('Is human')
		except:
			ishuman = False
		hascoord = False
		try:
			test = item_dict['claims']['P625']
			hascoord = True
			print('Has coord')
		except:
			hascoord = False
		if iscat==False and hascoord==False and ishuman==False:
			input('Add coordinate?')
		return 0
	except:
		print(page.title() + ' - no page found')
		wd_item = 0
		item_dict = 0
		qid = 0
		sitelink_check = 0
		# continue

	if search:
		print('Searching for a match...')
		wikidataEntries = search_entities(repo, page.title().replace('Category:',''))
		if wikidataEntries['search'] != []:
			results = wikidataEntries['search']
			numresults = len(results)
			for i in range(0,numresults):
				targetpage = pywikibot.ItemPage(wikidata_site, results[i]['id'])
				item_dict = targetpage.get()
				print('http://www.wikidata.org/wiki/'+results[i]['id'])
				try:
					print(item_dict['labels']['en'])
				except:
					print('')
				print('http://commons.wikimedia.org/wiki/'+page.title().replace(' ','_'))
				text = input("Save? ")
				if text != 'n':
					data = {'sitelinks': [{'site': 'commonswiki', 'title': page.title()}]}
					targetpage.editEntity(data, summary=u'Add commons sitelink')
					return 1
		wikidataEntries = search_entities_es(repo, page.title().replace('Category:',''))
		if wikidataEntries['search'] != []:
			results = wikidataEntries['search']
			numresults = len(results)
			for i in range(0,numresults):
				targetpage = pywikibot.ItemPage(wikidata_site, results[i]['id'])
				item_dict = targetpage.get()
				print('http://www.wikidata.org/wiki/'+results[i]['id'])
				try:
					print(item_dict['labels']['en'])
				except:
					print('')
				print('http://commons.wikimedia.org/wiki/'+page.title().replace(' ','_'))
				text = input("Save? ")
				if text != 'n':
					data = {'sitelinks': [{'site': 'commonswiki', 'title': page.title()}]}
					targetpage.editEntity(data, summary=u'Add commons sitelink')
					return 1

	# if 'in Tenerife' in page.title():
	# 	return 0

	if create:
		text = page.title()
		print('http://commons.wikimedia.org/wiki/'+text.replace(' ','_'))
		text = input("Create a new item? use 'c' for a category: ")
		if text != 'n':
			# Start assembling the Wikidata entry
			items = []
			if text == 'c':
				items.append(['P31','Q4167836'])
			test = newitem(page, items)
			return 1
	return 0

# targetcats = ['Category:La Palma']
# targetcats = ['Category:San Cristóbal de La Laguna']
# targetcats = ['Category:Santa Cruz de La Palma']
# targetcats = ['Category:Museums in La Palma']
# targetcats = ['Category:Uses of Wikidata Infobox with manual qid']
targetcats = ['Category:Tenerife']
numchecked = 0
catschecked = 0
create = True
search = True
i = 0
seen   = set(targetcats)
active = set(targetcats)
if targetcats != []:
	while active:
		i+=1
		next_active = set()
		for item in active:
			cat = pywikibot.Category(commons,item)
			nummodified += do_check(cat,create,search)
			numchecked += 1
			print(str(nummodified) + " - " + str(numchecked) + "/" + str(len(seen)) + "/" + str(len(active)) + "/" + str(len(next_active)))

			# See if there are subcategories that we want to check in the future
			for result in pagegenerators.SubCategoriesPageGenerator(cat, recurse=False):
				if result.title() not in seen:
					seen.add(result.title())
					next_active.add(result.title())
		temp = list(next_active)
		random.shuffle(temp)
		active = set(temp)
		if nummodified >= maxnum:
			print('Reached the maximum of ' + str(maxnum) + ' entries modified, quitting!')
			break
else:
	while nummodified < maxnum:
		targets = pagegenerators.RandomPageGenerator(total=100, site=commons, namespaces='14')
		for target in targets:
			print(target.title())
			nummodified += do_check(target,create)
			print(nummodified)
			
			if nummodified >= maxnum:
				print('Reached the maximum of ' + str(maxnum) + ' entries modified, quitting!')
				break

# EOF