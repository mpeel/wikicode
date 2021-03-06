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

for option in range(0,2):
	candidates = []
	if option == 1:
		reportpage = pywikibot.Page(repo, 'Wikidata:Database reports/Constraint violations/P910')
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
		# if option == 2:
		# This times out, so isn't currently running
		# ... except we no longer have a choice.
		query = 'SELECT ?item ?itemLabel ?should_link_via_P301_to ?should_link_via_P301_toLabel '\
		'WHERE {'\
		'?should_link_via_P301_to wdt:P910 ?item .'\
		'FILTER NOT EXISTS { ?item wdt:P301 ?should_link_via_P301_to } .'\
		'SERVICE wikibase:label { bd:serviceParam wikibase:language "en" } .'\
		'}'
		# else:
		# This query no longer works per T274982
		# 	query = 'SELECT DISTINCT ?item ?itemLabel WHERE {'\
		# 	'?statement wikibase:hasViolationForConstraint wds:P910-87F11688-D962-490C-B67C-627142687E18 .'\
		# 	'?item ?p ?statement .'\
		# 	'FILTER( ?item NOT IN ( wd:Q4115189, wd:Q13406268, wd:Q15397819 ) ) .'\
		# 	'SERVICE wikibase:label { bd:serviceParam wikibase:language "en" } .'\
		# 	'}'
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
		if 'Property' in qid:
			print('Property, skipping')
			continue
		# print(item_dict)
		trip = 0
		try:
			if 'Property' in item_dict['labels']['enwiki']:
				trip = 1
		except:
			null = 0
		if trip:
			continue

		try:
			p301 = item_dict['claims']['P910']
		except:
			print('No P910')
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
				p910 = target_dict['claims']['P301']
				continue
			except:
				print('No P301 in target')

			newclaim = pywikibot.Claim(repo, 'P301')
			newclaim.setTarget(page)
			if debug == 1:
				text = input("Save link? ")
			else:
				text = 'y'
			if text != 'n':
				val.addClaim(newclaim, summary=u'Adding reciprocal P301 value to match P910 in target')
				nummodified += 1

			if nummodified >= maxnum:
				print('Reached the maximum of ' + str(maxnum) + ' entries modified, quitting!')
				exit()


print('Done! Edited ' + str(nummodified) + ' entries')
		
# EOF
