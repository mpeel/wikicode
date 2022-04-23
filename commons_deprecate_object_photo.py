#!/usr/bin/python
# -*- coding: utf-8  -*-
# Remove uses of Object Photo in favour of using Wikidata
# Mike Peel     23-Apr-2022      v1 - start
import pywikibot
from pywikibot import pagegenerators

commons = pywikibot.Site('commons', 'commons')

cat = pywikibot.Category(commons,"Category:Files using deprecated object photo template")
for page in pagegenerators.CategorizedPageGenerator(cat, recurse=False):
	if 'File:' not in page.title():
		continue
	print(page.title())
	# print(page.text)
	lines = page.text.splitlines()
	categoryname = ''
	for line in lines:
		if '|object' in line:
			print(line)
			categoryname = line.split('=')[1].strip()
			print(categoryname)
	if categoryname != '':
		try:
			cat = pywikibot.Category(commons,"Category:"+categoryname)
			wd_item = pywikibot.ItemPage.fromPage(cat)
			item_dict = wd_item.get()
			qid = wd_item.title()
			print(qid)
		except:
			print('Huh - no page found')
			continue

		page.text = page.text.replace('Object photo','Art photo')
		page.text = page.text.replace('|object','|wikidata')
		page.text = page.text.replace(' ' + categoryname, ' ' + qid)
		page.text = page.text.replace('|author','|photographer')
		page.text = page.text.replace('|date','|photo date')
		print(page.text)
		test = input('Save?')
		if test == 'y':
			page.save('Migrating from Object photo to Art photo',minor=False)
