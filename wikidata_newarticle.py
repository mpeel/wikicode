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
from wir_newpages import *

enwiki = pywikibot.Site('en', 'wikipedia')
repo = enwiki.data_repository()  # this is a DataSite object

while(True):
	url = input('URL?')
	url = url.replace('http://','')
	url = url.replace('https://','')
	siteid = url.split('.')[0]
	articlename = url.split('/')[-1].replace('_',' ')
	siteid = siteid.strip()
	lang = siteid + 'wiki'
	site = pywikibot.Site(siteid, 'wikipedia')
	page = pywikibot.Page(site, articlename)

	try:
		article = pywikibot.Page(site, articlename)
		text = article.get()
	except:
		print("That didn't work, try again?")
		continue

	new_item = pywikibot.ItemPage(repo)
	label = article.title()
	new_item.editLabels(labels={siteid:label}, summary="Creating item")
	candidate_item = pywikibot.ItemPage(repo, new_item.getID())
	print(candidate_item)

	title = article.title()
	try:
		title = title.split('(')[0]
	except:
		null = 0

	data = {'sitelinks': [{'site': siteid+'wiki', 'title': article.title()}]}
	candidate_item.editEntity(data, summary=u'Add sitelink')

	if pageIsBiography(page,lang=siteid):
		addBiographyClaims(repo=repo, wikisite=site, item=candidate_item, page=page, lang=siteid)

#EOF