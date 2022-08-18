#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pywikibot
from pywikibot import pagegenerators
from pywikibot.data import api

enwiki = pywikibot.Site('en', 'wikipedia')
enwiki_repo = enwiki.data_repository()

targetcat = 'Category:Violence against women in the United States'
cat = pywikibot.Category(enwiki, targetcat)

pages = pagegenerators.CategorizedPageGenerator(cat, recurse=False);
for page in pages:
	try:
		wd_item = pywikibot.ItemPage.fromPage(page)
		item_dict = wd_item.get()
	except:
		# print("No Wikidata sitelink found")
		# continue
		pass

	try:
		P21 = item_dict['claims']['P21']
	except:
		P21 = ''
	# print(P21)
	gender = ''
	for clm in P21:
		try:
			gender = clm.getTarget()
		except:
			gender = ''
	if gender == '':
		gender = '-'
	elif gender.title() == 'Q6581072':
		gender = 'Female'
	elif gender.title() == 'Q6581097':
		gender = 'M'
	else:
		gender = gender.title()
	print('|-')
	print('| [[' + page.title() + ']] || ' + gender)
	# if P21 != '':
	# 	exit()
