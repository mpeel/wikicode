#!/usr/bin/python
# -*- coding: utf-8  -*-
# Remove bad P373 links
# Mike Peel     17-Jun-2019      v1 - start

from __future__ import unicode_literals

import pywikibot
import numpy as np
import time
import string
from pywikibot import pagegenerators
import urllib
from pibot_functions import *

maxnum = 10
nummodified = 0

wikidata_site = pywikibot.Site("wikidata", "wikidata")
repo = wikidata_site.data_repository()  # this is a DataSite object
commons = pywikibot.Site('commons', 'commons')
debug = 0
attempts = 0
count = 0

while(True):
	categoryname = input('Category name?')
	category = pywikibot.Page(commons, categoryname)
	page = pywikibot.ItemPage.fromPage(category)
	item_dict = page.get()
	qid = page.title()
	print("\nhttp://www.wikidata.org/wiki/" + qid)
	# print(item_dict)
	try:
		p301 = item_dict['claims']['P301']
	except:
		print('No P301')
		continue
	for clm in p301:
		val = clm.getTarget()
		print(val)
		wd_id = val.title()
		target_dict = val.get()

		try:
			p910 = target_dict['claims']['P910']
			print("Has P910, aborting")
			continue
		except:
			print('No P910 in target')

		newclaim = pywikibot.Claim(repo, 'P910')
		newclaim.setTarget(page)
		if debug == 1:
			text = input("Save link? ")
		else:
			text = 'y'
		if text != 'n':
			val.addClaim(newclaim, summary=u'Adding reciprocal P910 value to match P301 in target')
		
# EOF
