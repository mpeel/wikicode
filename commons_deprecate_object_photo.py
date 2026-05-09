#!/usr/bin/python
# -*- coding: utf-8  -*-
# Remove uses of Object Photo in favour of using Wikidata
# Mike Peel     23-Apr-2022      v1 - start
import pywikibot
from pywikibot import pagegenerators

commons = pywikibot.Site('commons', 'commons')
# prevname = ''
# catname = 'Category:Files using deprecated object photo template'
print('Please provide the category name')
catname = input()#'Category:Móvil (Francisco Sobrino)'
if 'Category:' not in catname:
	catname = 'Category:'+catname
cat = pywikibot.Category(commons,catname)
for page in pagegenerators.CategorizedPageGenerator(cat, recurse=False):
	# if 'File:Apollon citharède et Victoire Louvre Ma965.jpg' not in page.title():
	# 	continue
	if 'File:' not in page.title():
		continue
	if 'Mike Peel' not in page.text:
		continue
	print("https://commons.wikimedia.org/wiki/"+page.title().replace(' ','_'))
	# print(page.text)
	lines = page.text.splitlines()
	categoryname = ''
	for line in lines:
		if '|object' in line:
			# print(line)
			categoryname = line.split('=')[1].strip()
			# print(categoryname)
		else:
			categoryname = catname.replace('Category:','')
	if categoryname != '':
		# print('Hi')
		# print(prevname)
		# print(categoryname)
		# if prevname == categoryname:
		# 	continue
		# else:
		# 	prevname = categoryname
		try:
			cat = pywikibot.Category(commons,"Category:"+categoryname)
			wd_item = pywikibot.ItemPage.fromPage(cat)
			item_dict = wd_item.get()
			qid = wd_item.title()
			print(qid)
		except:
			print('Huh - no page found')
			continue

		try:
			p301_check = item_dict['claims']['P301']
			print('P301 exists, following that.')
			for clm in p301_check:
				wd_item = clm.getTarget()
				item_dict = wd_item.get()
				qid = wd_item.title()
		except:
			null = 0
		print(qid)
		page_old = page.text
		page.text = page.text.replace('Information','Art photo\n|Wikidata='+qid)
		page.text = page.text.replace('Object photo','Art photo')
		page.text = page.text.replace('|object','|wikidata')
		# page.text = page.text.replace(' ' + categoryname, ' ' + qid)
		# page.text = page.text.replace('=' + categoryname, '= ' + qid)
		page.text = page.text.replace('|author','| Photographer')
		page.text = page.text.replace('|Author','| Photographer')
		page.text = page.text.replace('| Author','| Photographer')
		page.text = page.text.replace('|date','|photo date')
		page.text = page.text.replace('| Date','| Photo date')
		page.text = page.text.replace('|Date','| Photo date')
		page.text = page.text.replace(' | Description = <!-- A description is required. -->\n','')
		if qid not in page.text:
			continue
		else:
			if page.text != page_old:
				print(page.text)
				test = input('Save?')
				if test != 'n':
					page.save('Migrating to Art photo',minor=False)
