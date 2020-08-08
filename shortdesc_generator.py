# !/usr/bin/python
# -*- coding: utf-8  -*-
# Test of generation of short descriptions
# Mike Peel     08-Aug-2020     v1 - start

import pywikibot
from pywikibot import pagegenerators
from pywikibot.data import api
from wir_newpages import *

def get_pageinfo(site, itemtitle):
	 params = { 'action' :'query', 
				'format' : 'json',
				'prop' : 'pageprops',
				'titles': itemtitle}
	 request = api.Request(site=site, parameters=params)
	 return request.submit()

maxnum = 100
nummodified = 0
debug = True
trip = True

wikipedia = pywikibot.Site('en', 'wikipedia')

targetcat = 'Category:English footballers'
cat = pywikibot.Category(wikipedia, targetcat)

count = 0
for page in pagegenerators.CategorizedPageGenerator(cat, recurse=False):
	enwiki_description = ''
	count += 1
	if not trip:
		if "Varanasi" in page.title():
			trip = True
		else:
			continue

	# Get the short description from enwp
	test = get_pageinfo(wikipedia,page)
	for item in test['query']['pages']:
		try:
			enwiki_description = test['query']['pages'][item]['pageprops']['wikibase-shortdesc']
		except:
			null = 0
	if len(enwiki_description) > 0:
		print('* [['+page.title()+']] - EXISTS: ' + enwiki_description)
	else:
		if 'nfobox' not in page.text:
			print('* [['+page.title()+"]] - '''NO INFOBOX'''")
		else:
			enwiki_description = 'English footballer'
			birthdate = calculateBirthDateFull(page=page,lang='en')
			deathdate = calculateDeathDateFull(page=page,lang='en')
			if birthdate and deathdate:
				enwiki_description += ' (' + str(birthdate[0:4]) + "-" + str(deathdate[0:4]) + ')'
			elif birthdate:
				enwiki_description += ' (b. ' + str(birthdate[0:4]) + ')'
			elif deathdate:
				enwiki_description += ' (d. ' + str(birthdate[0:4]) + ')'

			print('* [['+page.title()+"]] - '''NEW: " + enwiki_description+"'''")



	if count > maxnum:
		break

# print('Done! Edited ' + str(nummodified) + ' entries')
		
# EOF