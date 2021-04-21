#!/usr/bin/python
# -*- coding: utf-8  -*-
# Copy human names from one lang to another
# Mike Peel     21-Dec-2020      v1

from __future__ import unicode_literals

import pywikibot
import numpy as np
import time
import string
from pywikibot import pagegenerators
import urllib

maxnum = 1000000
nummodified = 0
stepsize =  10000
maximum = 12000000
numsteps = int(maximum / stepsize)
debug = False


wikidata_site = pywikibot.Site("wikidata", "wikidata")
repo = wikidata_site.data_repository()  # this is a DataSite object

sourcelang = ['pt-br','pt']
destlang = ['pt','pt-br']
# sourcelang = ['pt','pt-br']
# destlang = ['pt-br','pt']
for l in range(0,len(sourcelang)):
	for i in range(0,numsteps):
		print('Starting at ' + str(i*stepsize))

		query = "SELECT ?item\n"\
		"WITH { \n"\
		"  SELECT ?item WHERE {\n"\
		"    ?item wdt:P31 wd:Q5 . \n"\
		'  } LIMIT '+str(stepsize)+' OFFSET '+str(i*stepsize)+'\n'\
		"} AS %items\n"\
		"WHERE {\n"\
		"  INCLUDE %items .\n"\
		"    SERVICE wikibase:label { bd:serviceParam wikibase:language \""+sourcelang[l]+"\". }\n"\
		"    FILTER(NOT EXISTS {\n"\
		"        ?item rdfs:label ?lang_label.\n"\
		"        FILTER(LANG(?lang_label) in ('"+destlang[l]+"'))\n"\
		"    })\n"\
		"    FILTER(EXISTS {\n"\
		"        ?item rdfs:label ?lang_label.\n"\
		"        FILTER(LANG(?lang_label) in ('"+sourcelang[l]+"'))\n"\
		"    })\n"\
		"}"

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

			# Check that it hasn't already got a label in the destination langugae
			try:
				label = item_dict['labels'][destlang[l]]
				print(label)
				print("That shouldn't have worked, continuing")
				continue
			except:
				print('No label')

			# Get the new label
			try:
				label = item_dict['labels'][sourcelang[l]]
			except:
				label = ''
			if '(' in label or ')' in label:
				continue
			if label != '':
				if debug:
					print(label)
					test = input('Save?')
				else:
					test = 'y'
				if test == 'y':
					try:
						page.editLabels(labels={destlang[l]: label}, summary=u'Copy ' + sourcelang[l] + " label to " + destlang[l] + " label")
						nummodified += 1
					except:
						print('Edit failed')

			if nummodified >= maxnum:
				print('Reached the maximum of ' + str(maxnum) + ' entries modified, quitting!')
				exit()

	print('Done! Edited ' + str(nummodified) + ' entries')
			 
	# EOF