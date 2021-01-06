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

while(True):
	categoryname = input('Category name?')
	topicid = input('Topic QID?')
	categoryname = categoryname.strip()

	try:
		commonscat_page = pywikibot.Page(commons, categoryname)
		text = commonscat_page.get()
	except:
		try:
			commonscat_page = pywikibot.Page(commons, categoryname[-1])
			text = commonscat_page.get()
		except:
			print("That didn't work, try again?")
			continue

	topic_item = pywikibot.ItemPage(repo, topicid)
	topic_dict = topic_item.get()

	try:
		p910 = topic_dict['claims']['P910']
		print('There is already a P910 value - check?')
		continue
	except:
		test = 0

		# Start assembling the Wikdata entry
		items = [['P31','Q4167836']] # Instance of Wikimedia category
		items.append(['P301',topicid]) # Main topic

		print(items)
		new_item = newitem(commonscat_page, items)
		newclaim = pywikibot.Claim(repo, 'P910')
		newclaim.setTarget(new_item)
		topic_item.addClaim(newclaim, summary=u'Link to category item')

#EOF