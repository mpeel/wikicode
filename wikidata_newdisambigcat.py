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

while(True):
	siteid = input('Site?')
	siteid = siteid.strip()
	lang = siteid + 'wiki'
	categoryname = input('Category?')
	categoryname = categoryname.strip()
	site = pywikibot.Site(siteid, 'wikipedia')

	try:
		print(siteid)
		print(categoryname)
		category = pywikibot.Page(site, categoryname)
		text = category.get()
	except:
		print("That didn't work, try again?")
		continue

	new_item = pywikibot.ItemPage(repo)
	label = category.title()
	print(lang)
	print(label)
	new_item.editLabels(labels={siteid:label}, summary="Creating item")
	candidate_item = pywikibot.ItemPage(repo, new_item.getID())
	print(candidate_item)

	data = {'sitelinks': [{'site': siteid+'wiki', 'title': category.title()}]}
	candidate_item.editEntity(data, summary=u'Add sitelink')
	claim = pywikibot.Claim(repo, 'P31')
	claim.setTarget(pywikibot.ItemPage(repo, 'Q15407973'))
	candidate_item.addClaim(claim, summary=u'Disambiguation category')

#EOF