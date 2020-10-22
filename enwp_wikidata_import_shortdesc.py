# !/usr/bin/python
# -*- coding: utf-8  -*-
# Synchronise enwp short description and wikidata en descriptions
# Mike Peel     03-Aug-2020     v1 - start
# Mike Peel     12-Sep-2020     v2 - reconfigure just for empty Wikidata descriptions.

import pywikibot
from pywikibot import pagegenerators
from pywikibot.data import api
import random

def get_pageinfo(site, itemtitle):
	 params = { 'action' :'query', 
				'format' : 'json',
				'prop' : 'pageprops',
				'titles': itemtitle}
	 request = api.Request(site=site, parameters=params)
	 return request.submit()

maxnum = 1000
nummodified = 0
debug = False
trip = True
# replace_existing = False
maxwords = 10

targetcat = 'Category:Short description with empty Wikidata description'

# Set up the wikimedia site links
wikidata_site = pywikibot.Site("wikidata", "wikidata")
repo = wikidata_site.data_repository()  # this is a DataSite object
commons = pywikibot.Site('commons', 'commons')
wikipedia = pywikibot.Site('en', 'wikipedia')

# Fetch the exclusion list for lower case for the first letter
page = pywikibot.Page(repo, 'User:Pi bot/lowercase_exceptions')
items = page.text
lowercase_exceptions = items.split()

# Fetch the exclusion list for bad enwp short descriptions
page = pywikibot.Page(repo, 'User:Pi bot/shortdesc_exclusions')
items = page.text
shortdesc_exclusions = items.split('\n')
print(shortdesc_exclusions)

# List of words to add to the double-check report
page = pywikibot.Page(repo, 'User:Pi bot/doublecheck_words')
items = page.text
doublecheck_words = items.split('\n')
print(doublecheck_words)

# List of starting words to add to the double-check report
page = pywikibot.Page(repo, 'User:Pi bot/doublecheck_start_words')
items = page.text
doublecheck_start_words = items.split('\n')
print(doublecheck_start_words)

cat = pywikibot.Category(wikipedia, targetcat)
pages = pagegenerators.CategorizedPageGenerator(cat, recurse=False);
# todo = []
# count = 0
# maxcount = 50000
# for page in pages:
# 	todo.append(page.title())
# 	count += 1
	# if count >= maxcount:
		# break

# random.shuffle(todo)
# for item in sorted(todo,reverse=True):
# for item in todo:
for page in pages:
	# if count > 0:
		# page = pywikibot.Page(wikipedia,item)
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
	try:
		test = get_pageinfo(wikipedia,page)
		for item in test['query']['pages']:
			enwiki_description = test['query']['pages'][item]['pageprops']['wikibase-shortdesc']
	except:
		enwiki_description = ''

	if len(enwiki_description) == 0:
		print('No enwiki description found')
		continue
	print(enwiki_description)

	# Check that the short description isn't in the exclusion list
	if enwiki_description.strip() in shortdesc_exclusions:
		print('enwiki description is in the exclusion list, skipping')
		continue

	# Check the length of the short description
	if len(enwiki_description.split()) > maxwords:
		print('enwiki description is too long, skipping')
		continue

	# Change the first letter to lower case unless it's an exception
	if enwiki_description.split()[0] not in lowercase_exceptions:
		# ... and if the second letter isn't also upper case.
		if enwiki_description[1].lower() == enwiki_description[1] and 'football season' not in enwiki_description and 'basketball season' not in enwiki_description:
			enwiki_description = enwiki_description[0].lower() + enwiki_description[1:]
	if enwiki_description[-1] == '.':
		enwiki_description = enwiki_description[0:-1]
	if enwiki_description[0:2] == 'a ':
		enwiki_description = enwiki_description[2:]

	# Get the description from Wikidata
	try:
		wikidata_description = item_dict['descriptions']['en']
	except:
		null = 0

	# Save it to Wikidata
	if wikidata_description == '':
		# We have no en description on Wikidata, so we can add the enwp one
		print(enwiki_description)
		# See if we want to add this to the list to double-check
		doublecheck = False
		wordfound = ''
		for word in doublecheck_words:
			if word in enwiki_description:
				doublecheck = True
				wordfound = word
		for word in doublecheck_start_words:
			if (enwiki_description.strip())[:len(word)+1] == word+" ":
				doublecheck = True
				wordfound = word
		if debug:
			test = input('No description, import it?')
		else:
			test = 'y'
		mydescriptions = {u'en': enwiki_description}
		if test == 'y':
			try:
				wd_item.editDescriptions(mydescriptions, summary=u'Importing description from enwiki: ' + enwiki_description)
				nummodified += 1
			except:
				print('Save went wrong')
				continue
		if doublecheck:
			page = pywikibot.Page(repo, 'User:Pi bot/doublecheck')
			page.text = page.text + "\n* {{Q|" + str(qid) + "}} - " + enwiki_description + " ('"+wordfound+"')"
			page.save("Adding " + str(qid))
	# elif wikidata_description.lower() != enwiki_description.lower() and replace_existing:
	# 	# The Wikidata description doesn't match enwp, update it using enwp
	# 	print('enwp: ' + enwiki_description)
	# 	print('wikidata: ' + wikidata_description)
	# 	if debug:
	# 		test = input('Change description?')
	# 	else:
	# 		test = 'y'
	# 	mydescriptions = {u'en': enwiki_description}
	# 	if test == 'y':
	# 		wd_item.editDescriptions(mydescriptions, summary=u'Matching short description from the English Wikipedia')
	# 		nummodified += 1

	if nummodified >= maxnum:
		break

print('Done! Edited ' + str(nummodified) + ' entries')
		
# EOF