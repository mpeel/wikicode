# !/usr/bin/python
# -*- coding: utf-8  -*-
# Synchronise enwp short description and wikidata en descriptions
# Mike Peel     03-Aug-2020     v1 - start

import pywikibot
from pywikibot import pagegenerators
from pywikibot.data import api

def get_pageinfo(site, itemtitle):
	 params = { 'action' :'query', 
				'format' : 'json',
				'prop' : 'pageprops',
				'titles': itemtitle}
	 request = api.Request(site=site, parameters=params)
	 return request.submit()

maxnum = 10000
nummodified = 0
debug = True
trip = True
replace_existing = True

wikidata_site = pywikibot.Site("wikidata", "wikidata")
repo = wikidata_site.data_repository()  # this is a DataSite object
commons = pywikibot.Site('commons', 'commons')
wikipedia = pywikibot.Site('en', 'wikipedia')

templates = ['Short description', 'short description']

for page in pagegenerators.RandomPageGenerator(total=num, site=wikipedia, namespaces=[0]):
	enwiki_description = ''
	wikidata_description = ''

	if not trip:
		if "Varanasi" in page.title():
			trip = True
		else:
			print(page.title())
			continue

	try:
		wd_item = pywikibot.ItemPage.fromPage(page)
		item_dict = wd_item.get()
		qid = wd_item.title()
	except:
		print('Huh - no page found')
		continue

	print("\n" + qid)
	print('https://en.wikipedia.org/wiki/'+page.title().replace(' ','_'))

	# Get the short description from enwp
	test = get_pageinfo(wikipedia,page)
	for item in test['query']['pages']:
		try:
			enwiki_description = test['query']['pages'][item]['pageprops']['wikibase-shortdesc']
		except:
			null = 0
	if len(enwiki_description) > 0:
		enwiki_description = enwiki_description[0].lower() + enwiki_description[1:]
	else:
		continue

	# Get the description from Wikidata
	try:
		wikidata_description = item_dict['descriptions']['en']
	except:
		null = 0

	# Save it to enwiki
	if enwiki_description == '' and wikidata_description != '':
		target_text = page.get()
		print(wikidata_description)
		if debug:
			test = input('No description, import it?')
		else:
			test = 'y'
		target_text = '{{Short description|' + wikidata_description + '}}' + target_text
		if test == 'y':
			page.text = target_text
			savemessage = 'Importing short description from Wikidata'
			page.save(savemessage,minor=False)
			nummodified += 1
	elif wikidata_description.lower() != enwiki_description.lower() and replace_existing:
		# The Wikidata description doesn't match enwp, update it using wikidata
		print('enwp: ' + enwiki_description)
		print('wikidata: ' + wikidata_description)
		if debug:
			test = input('Change description?')
		else:
			test = 'y'
		# To improve code to find existing short descriptions
		target_text = '{{Short description|' + wikidata_description + '}}' + target_text

		mydescriptions = {u'en': enwiki_description}
		if test == 'y':
			page.text = target_text
			savemessage = 'Matching short description from Wikidata'
			page.save(savemessage,minor=False)
			nummodified += 1

	if nummodified > maxnum:
		break

print('Done! Edited ' + str(nummodified) + ' entries')
		
# EOF