#!/usr/bin/python
# -*- coding: utf-8  -*-
# Copy human names from selected other languages to English
# Mike Peel     21-Dec-2020      v1

from __future__ import unicode_literals

import pywikibot
import numpy as np
import time
import string
from pywikibot import pagegenerators
import urllib

maxnum = 10000
nummodified = 0
stepsize =  10000
maximum = 4000000
numsteps = int(maximum / stepsize)
debug = True

# Test function from https://stackoverflow.com/questions/27084617/detect-strings-with-non-english-characters-in-python
# Should probably tweak this to include é but not ł.
def isEnglish(s):
	try:
		s.encode(encoding='utf-8').decode('ascii')
	except UnicodeDecodeError:
		return False
	else:
		return True

wikidata_site = pywikibot.Site("wikidata", "wikidata")
repo = wikidata_site.data_repository()  # this is a DataSite object
commons = pywikibot.Site('commons', 'commons')

langs = 'de,fr,es,pt,nl,it,sv,pl'
lang_list = langs.split(',')
lang_sparql = ''
for l in lang_list:
	lang_sparql = lang_sparql + "'"+l+"',"
lang_sparql = lang_sparql[:-1]

langs_exclude = 'en,ru'
lang_list_exclude = langs_exclude.split(',')
lang_exclude_sparql = ''
for l in lang_list_exclude:
	lang_exclude_sparql = lang_exclude_sparql + "'"+l+"',"
lang_exclude_sparql = lang_exclude_sparql[:-1]

lang_combine_sparql = lang_sparql + "," + lang_exclude_sparql

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
	"    SERVICE wikibase:label { bd:serviceParam wikibase:language \""+lang_combine_sparql+"\". }\n"\
	"    FILTER(NOT EXISTS {\n"\
	"        ?item rdfs:label ?lang_label.\n"\
	"        FILTER(LANG(?lang_label) in ("+lang_exclude_sparql+"))\n"\
	"    })\n"\
	"    FILTER(EXISTS {\n"\
	"        ?item rdfs:label ?lang_label.\n"\
	"        FILTER(LANG(?lang_label) in ("+lang_sparql+"))\n"\
	"    })\n"\
	"}"

	print(query)

	generator = pagegenerators.WikidataSPARQLPageGenerator(query, site=wikidata_site)
	for page in generator:
		# Get the page
		item_dict = page.get()
		qid = page.title()
		print("\nhttps://www.wikidata.org/wiki/" + qid)

		# Check for excluded P27 values
		

		# Check that it hasn't already got an en label
		try:
			label = item_dict['labels']['en']
			print(label)
			print("That shouldn't have worked, continuing")
			continue
		except:
			print('No English label')

		# Get the new label
		label = ''
		labellang = ''
		for val in lang_list:
			if label != '':
				break
			try:
				if isEnglish(item_dict['labels'][val]):
					label = item_dict['labels'][val]
					labellang = val
			except:
				continue

		if label != '':
			if debug:
				print(label)
				print(labellang)
				test = input('Save?')
			else:
				test = 'y'
			if test == 'y':
				page.editLabels(labels={'en': label}, summary=u'Copy ' + labellang + " label to en label")
				nummodified += 1

		if nummodified >= maxnum:
			print('Reached the maximum of ' + str(maxnum) + ' entries modified, quitting!')
			exit()

print('Done! Edited ' + str(nummodified) + ' entries')
		 
# EOF