#!/usr/bin/python
# -*- coding: utf-8  -*-
# Remove text in brackets from human item labels 
# Mike Peel     21-Dec-2020      v1

from __future__ import unicode_literals

import pywikibot
import numpy as np
import time
import string
from pywikibot import pagegenerators
import urllib

maxnum = 1000
nummodified = 0
stepsize =  10000
maximum = 12000000
numsteps = int(maximum / stepsize)
debug = False


wikidata_site = pywikibot.Site("wikidata", "wikidata")
repo = wikidata_site.data_repository()  # this is a DataSite object

for i in range(0,numsteps):
	print('Starting at ' + str(i*stepsize))

	query = 'SELECT * '\
	' WITH '\
	' { '\
	'  SELECT ?value (count(*) as ?ct)\n'\
	'  {\n'\
	'    ?item wdt:P106 ?value\n'\
	'  }\n'\
	'  GROUP BY ?value\n'\
	'  ORDER BY DESC(?ct)\n'\
	'  OFFSET ' + str(i*stepsize)+'\n'\
	'  LIMIT '+str(stepsize)+'\n'\
	' }\n'\
	' AS %value\n'\
	' WHERE\n'\
	' {\n'\
	'  INCLUDE %value\n'\
	'  hint:Query hint:optimizer "None".\n'\
	'  ?value rdfs:label ?v . FILTER( lang(?v) = "en" )\n'\
	'  BIND( CONCAT( \'inlabel:"\',?v,\'@en" haswbstatement:P31=Q5\') as ?search)\n'\
	'  {\n'\
	'  SERVICE wikibase:mwapi {\n'\
	'    bd:serviceParam wikibase:endpoint "www.wikidata.org" .\n'\
	'    bd:serviceParam wikibase:api "Generator" .\n'\
	'    bd:serviceParam mwapi:generator "search" .\n'\
	'    bd:serviceParam mwapi:gsrsearch ?search .\n'\
	'    bd:serviceParam mwapi:gsrlimit "max" .\n'\
	'    bd:serviceParam mwapi:gsrnamespace "0" .\n'\
	'    ?item wikibase:apiOutputItem mwapi:title  .\n'\
	'  }\n'\
	'  }\n'\
	'  ?item rdfs:label ?l.\n'\
	'  FILTER(REGEX(?l, "\\\\)$") && lang(?l)="en").\n'\
	'}'
	print(query)

	generator = pagegenerators.WikidataSPARQLPageGenerator(query, site=wikidata_site)
	for page in generator:
		# Get the page
		try:
			item_dict = page.get()
			qid = page.title()
		except:
			continue
		print("\nhttps://www.wikidata.org/wiki/" + qid)

		for i, val in enumerate(item_dict['labels']):
			if item_dict['labels'][val][-1] == ')':
				page_title = item_dict['labels'][val][:item_dict['labels'][val].rfind('(')].strip()
				print(item_dict['labels'][val])
				test = 'n'
				if debug:
					test = input('Save?')
				else:
					test = 'y'
				if test == 'y':
					try:
						page.editLabels(labels={val: page_title}, summary=u'Remove text in brackets from ' + val + ' label')
						nummodified += 1
					except:
						print('Edit failed')

		if nummodified >= maxnum:
			print('Reached the maximum of ' + str(maxnum) + ' entries modified, quitting!')
			exit()

print('Done! Edited ' + str(nummodified) + ' entries')
		 
# EOF