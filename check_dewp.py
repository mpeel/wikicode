#!/usr/bin/python
# -*- coding: utf-8  -*-
# Remove bad dewp sitelinks
# Mike Peel     24-Aug-2020      v1 - start

from __future__ import unicode_literals

import pywikibot
import numpy as np
import time
import string
from pywikibot import pagegenerators
import urllib
import csv

wikidata_site = pywikibot.Site("wikidata", "wikidata")
repo = wikidata_site.data_repository()  # this is a DataSite object
debug = 1

infile = 'quarry-47624-wikidata-sitelinks-run491913.csv'
lang = 'de'

with open(infile, mode='r') as infile:
	reader = csv.reader(infile)
	targets = {rows[0] for rows in reader}
for target in targets:
	# if test == 0 and 'Toyota JPN' not in target:
	target = target.strip()
	print(target)
	page = pywikibot.ItemPage(repo, target)
	try:
		item_dict = page.get()
		qid = page.title()
	except:
		print('Huh - no page found')
		continue
	print("\nhttps://www.wikidata.org/wiki/" + qid)
	try:
		sitelink = item_dict['sitelinks'][lang+'wiki']
		print(sitelink)
	except:
		print(lang + ' sitelink not found!')
		continue

	url = u'https://'+lang+'.wikipedia.org/wiki/'+sitelink.replace(' ','_')
	url = urllib.parse.quote(url.encode('utf8'), ':/')
	print(url)
	try:
		a=urllib.request.urlopen(url)
	except urllib.error.URLError as e:
		print(e.code)
		if e.code == 404:
			print('Removing link')
			page.removeSitelink(site=lang+'wiki', summary=u'Removing broken sitelink to '+lang+'wiki')
	# exit()
# EOF
