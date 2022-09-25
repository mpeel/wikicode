#!/usr/bin/python
# -*- coding: utf-8  -*-
# Add ISO dates to Wikidata items
# Mike Peel     25-Sep-2022      v1 - start

import pywikibot
import time
import string
from pywikibot import pagegenerators
import dateutil.parser as parser

# Sites
wikidata_site = pywikibot.Site("wikidata", "wikidata")
repo = wikidata_site.data_repository()  # this is a DataSite object
commons = pywikibot.Site('commons', 'commons')

query = 'SELECT DISTINCT ?item WHERE {'\
'     ?item p:P31 ?statement0.'\
'      ?statement0 (ps:P31/(wdt:P279*)) wd:Q47150325.'\
'}'
pages = pagegenerators.WikidataSPARQLPageGenerator(query, site=repo)
for page in pages:
	print('https://www.wikidata.org/wiki/'+page.title())
	item_dict = page.get()
	try:
		date = item_dict['labels']['en']
	except:
		continue
	print(date)
	newdate = parser.parse(date)
	isodate = newdate.isoformat().split('T')[0]
	print(isodate)
	aliases = []
	try:
		aliases = item_dict['aliases']['en']
	except:
		print('No existing aliases')
	found = 0
	for alias in aliases:
		if isodate in aliases:
			found = 1
	if found == 0:
		aliases.append(isodate)
		# input('Save?')
		page.editAliases(aliases={'en': aliases}, summary='Add ISO date ' + isodate + ' as en alias')

# EOF
