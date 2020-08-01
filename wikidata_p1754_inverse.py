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

maxnum = 1000
nummodified = 0

wikidata_site = pywikibot.Site("wikidata", "wikidata")
repo = wikidata_site.data_repository()  # this is a DataSite object
commons = pywikibot.Site('commons', 'commons')
debug = 0
attempts = 0
count = 0

for option in range(0,3):
	candidates = []
	if option == 1:
		reportpage = pywikibot.Page(repo, 'Wikidata:Database reports/Constraint violations/P1754')
		text = reportpage.get()
		text = text.split('== "Inverse" violations ==')[1].split('== "Single value" violations ==')[0]
		lines = text.splitlines()
		for line in lines:
			try:
				qid = line.split('* [[')[1].split(']]')[0]
				# print(qid)
				candidates.append(qid)
			except:
				continue
	else:
		if option == 2:
			query = 'SELECT ?item ?itemLabel ?should_link_via_P1753_to ?should_link_via_P1753_toLabel '\
			'WHERE {'\
			'?should_link_via_P1753_to wdt:P1754 ?item .'\
			'FILTER NOT EXISTS { ?item wdt:P1753 ?should_link_via_P1753_to } .'\
			'SERVICE wikibase:label { bd:serviceParam wikibase:language "en" } .'\
			'}'
		else:
			query = 'SELECT DISTINCT ?item ?itemLabel WHERE {'\
			'?statement wikibase:hasViolationForConstraint wds:P1754-015956CB-8C8E-49C9-9E43-ABA092CEE6A7 .'\
			'?item ?p ?statement .'\
			'FILTER( ?item NOT IN ( wd:Q4115189, wd:Q13406268, wd:Q15397819 ) ) .'\
			'SERVICE wikibase:label { bd:serviceParam wikibase:language "en" } .'\
			'}'
		if debug:
			query = query + " LIMIT 20"

		print(query)

		generator = pagegenerators.WikidataSPARQLPageGenerator(query, site=wikidata_site)


	for page in generator:
	# for pageid in candidates:
		# page = pywikibot.ItemPage(repo, pageid)
		try:
			item_dict = page.get()
		except:
			continue
		qid = page.title()
		print("\nhttp://www.wikidata.org/wiki/" + qid)
		# print(item_dict)
		try:
			p301 = item_dict['claims']['P1754']
		except:
			print('No P1754')
			continue
		for clm in p301:
			val = clm.getTarget()
			print(val)
			wd_id = val.title()
			try:
				target_dict = val.get()
			except:
				continue

			try:
				p910 = target_dict['claims']['P1753']
				continue
			except:
				print('No P1753 in target')

			newclaim = pywikibot.Claim(repo, 'P1753')
			newclaim.setTarget(page)
			if debug == 1:
				text = input("Save link? ")
			else:
				text = 'y'
			if text != 'n':
				val.addClaim(newclaim, summary=u'Adding reciprocal P1753 value to match P1754 in target')
				nummodified += 1

			if nummodified >= maxnum:
				print('Reached the maximum of ' + str(maxnum) + ' entries modified, quitting!')
				exit()


print('Done! Edited ' + str(nummodified) + ' entries')
		
# EOF
