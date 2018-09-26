#!/usr/bin/python
# -*- coding: utf-8  -*-
# Create new Wikidata items
# Started 25 August 2018 by Mike Peel
from __future__ import unicode_literals

import pywikibot
import numpy as np
import time
import string
from pywikibot import pagegenerators
import urllib

commons = pywikibot.Site('commons', 'commons')
repo = commons.data_repository()  # this is a DataSite object

def newitem(category, items):
	new_item = pywikibot.ItemPage(repo)
	new_item.editLabels(labels={"en":category}, summary="Creating item")
	candidate_item = pywikibot.ItemPage(repo, new_item.getID())
	candidate_item = pywikibot.ItemPage(repo, new_item)
	print candidate_item

	data = {'sitelinks': [{'site': 'commonswiki', 'title': category}]}
	candidate_item.editEntity(data, summary=u'Add commons sitelink')

	for item in items:
		claim = pywikibot.Claim(repo, item[0])
		claim.setTarget(pywikibot.ItemPage(repo, item[1]))
		try:
			candidate_item.addClaim(claim, summary=u'Setting '+item[0]+' value')
		except:
			print "That didn't work"
	return

category = 'Category:1546 in Finland'
items = [['P31','Q4167836'],['P971','Q6570'],['P971','Q33']]
test = newitem(category, items)


