#!/usr/bin/python3
# -*- coding: utf-8  -*-
# Remove bad P373 values
# Mike Peel     17-Apr-2020      v1 - start

import pywikibot
import numpy as np
from pywikibot import pagegenerators
from pibot_functions import *

wikidata_site = pywikibot.Site("wikidata", "wikidata")
repo = wikidata_site.data_repository()
debug = 1

query = "SELECT ?item ?commonscat ?sitelink ?name WHERE { ?item wdt:P373 ?commonscat. ?sitelink schema:about ?item; schema:isPartOf <https://commons.wikimedia.org/>; schema:name ?name . FILTER( CONTAINS(STR(?sitelink), 'Category:') = true ) . FILTER( ?commonscat != SUBSTR(STR(?name), 10) ) .} LIMIT 100"
generator = pagegenerators.WikidataSPARQLPageGenerator(query, site=wikidata_site)
for page in generator:
	print('\n\n')
	try:
		item_dict = page.get()
	except:
		continue
	qid = page.title()
	print("\nhttp://www.wikidata.org/wiki/" + qid)

	# Follow P910 when available
	try:
		existing_id = item_dict['claims']['P910']
		print('P910 exists, following that.')
		for clm2 in existing_id:
			wd_item = clm2.getTarget()
			item_dict = wd_item.get()
			qid = wd_item.title()
			print(wd_item.title())
			p910_followed = True
	except:
		null = 0

	try:
		sitelink = get_sitelink_title(item_dict['sitelinks']['commonswiki'])
		print('http://commons.wikimedia.org/wiki/'+sitelink.replace(' ','_'))
	except:
		print('No sitelink')
		continue

	if 'Category:' not in sitelink:
		continue

	try:
		p373 = item_dict['claims']['P373']
		for clm in p373:
			val = clm.getTarget()
			p373cat = u"Category:" + val
			if p373cat != sitelink:
				try:
					print(item_dict['labels']['en'])
				except:
					print('')
				print('Remove P373?')
				print(' http://www.wikidata.org/wiki/'+qid)
				print('http://commons.wikimedia.org/wiki/' + str(p373cat).replace(' ','_'))
				if debug == 1:
					test = input('OK?')
				else:
					test = 'y'
				if test == 'y':
					# savemessage = "Remove bad P373 value"
					savemessage = "Remove P373 value that doesn't match the sitelink"
					# print(savemessage)
					page.removeClaims(clm,summary=savemessage)
	except:
		continue
# EOF