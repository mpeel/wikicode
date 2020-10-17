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

wikidatainfobox = ["Wikidata Infobox", "Wikidata infobox", "wikidata infobox", "wikidata Infobox", "Infobox Wikidata", "infobox Wikidata", "infobox wikidata", "Infobox wikidata", "Wikidata  infobox", "wikidata  infobox", "Wikidata  Infobox", "wikidata  Infobox", "Wdbox", "wdbox", 'WI']

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
		except:
			print("That didn't work")
	return candidate_item

category = 'Category:Uses of Wikidata Infobox with manual qid'
targetcats = pagegenerators.SubCategoriesPageGenerator(cat, recurse=False);

for targetcat in targetcats:
	# Get the page contents
	commonscat_page = pywikibot.Page(commons, targetcat)
	text = commonscat_page.get()

	# See if we can find the QID
	id_val = (text.split("{{"+templates[i]+"|qid="))[1].split("}}")[0]
	try:
		id_val = id_val.split('|')[0]
	except:
		# null = 1
		continue

	# Make sure the category isn't already connected to an item
	try:
		# item_dict = page.get()
		# qid = page.title()
		wd_item = pywikibot.ItemPage.fromPage(commonscat_page)
		item_dict = wd_item.get()
		qid = wd_item.title()
		print('Matching item found')
		continue
	except:
		null = 1

	# Get the item, and make sure it doesn't have a P910 value
	try:
		# item_dict = page.get()
		# qid = page.title()
		wd_item = pywikibot.ItemPage.fromPage(commonscat_page)
		item_dict = wd_item.get()
		qid = wd_item.title()
		print('Matching item found')
		continue
	except:
		null = 1

	# Start assembling the Wikdata entry
	items = [['P31','Q4167836']] # Instance of Wikimedia category
	items.append(['P301',id_val]) # Main topic

	print(items)
	test = input('Create new category item?')
	if test == 'y':
		new_item = newitem(commonscat_page, items)
		newclaim = pywikibot.Claim(repo, 'P910')
		newclaim.setTarget(new_item)
		topic_item.addClaim(newclaim, summary=u'Link to category item')

#EOF