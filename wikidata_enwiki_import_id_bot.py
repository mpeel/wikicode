#!/usr/bin/python
# -*- coding: utf-8  -*-
# Import IDs from enwp
# 18 Jan 2022	Mike Peel	Started

import pywikibot
from pywikibot import pagegenerators
lang = 'en'
wiki = pywikibot.Site(lang, 'wikipedia')
repo = wiki.data_repository()
debug = True
whitelist = ['Category:Australian Statistical Geography Standard 2011 ID not in Wikidata']
def editwikidata(wd_item, propertyid, value):
	qid = wd_item.title()
	print('http://www.wikidata.org/wiki/'+qid)
	print(propertyid + ' = ' + value)
	item_dict = wd_item.get()

	newclaim = pywikibot.Claim(repo, propertyid)
	newclaim.setTarget(value)

	# print(newclaim)
	text = input("Save? ")
	if text == 'y':
		wd_item.addClaim(newclaim, summary=u'Importing ' + str(propertyid) + ' from enwiki')

	return 0


cat = pywikibot.Category(wiki, 'Category:Wikipedia categories tracking data not in Wikidata')
for subcat in pagegenerators.SubCategoriesPageGenerator(cat, recurse=False):
	runthis = False
	for test in whitelist:
		if test in subcat.title():
			runthis = True
	if not runthis:
		continue
	if debug:
		print('# ' + str(subcat.title()))
	propid = ''
	templatename = ''
	for template in subcat.templatesWithParams():
		if 'Wikidata tracking category' in template[0].title():
			if debug:
				print('# ' + str(template))
			for val in template[1]:
				if 'property' in val:
					propid = val.split('=')[1].strip()
				if 'template' in val:
					templatename = val.split('=')[1].strip()
	if debug:
		print('#' + propid)
		print('#' + templatename)

	# If we haven't got a propid or template, then skip this category
	if propid == '' or template == '':
		continue

	for page in pagegenerators.CategorizedPageGenerator(subcat, recurse=False):
		if debug:
			print('# ' + str(page))
		localid = ''
		for template in page.templatesWithParams():
			# if debug:
				# print(template[0].title())
			if templatename in template[0].title():
				for val in template[1]:
					# if debug:
						# print(val)
					if '=' not in val and localid == '':
						localid = val
					if 'id=' in val and localid == '':
						localid = val.split('=')[1].strip()
		if debug:
			print('#' + str(localid))
		if localid != '':
			# We have a local ID, check for a Wikidata value
			try:
				wd_item = pywikibot.ItemPage.fromPage(page)
				item_dict = wd_item.get()
			except:
				# print("No Wikidata sitelink found")
				continue
			wikidataval = ''
			snakid = ''
			try:
				wikidataval = item_dict['claims'][propid]
			except:
				null = 0
			if wikidataval == '':
				# Save to Wikidata?
				test = editwikidata(wd_item, propid, localid)
				page.touch()
