#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Touch categories on Commons
# Mike Peel     23-Sep-2018      v1 - start

# Import modules
import pywikibot
from pywikibot import pagegenerators

# Connect to commons
# commons = pywikibot.Site('commons', 'commons')
# commons = pywikibot.Site('simple', 'wikipedia')
commons = pywikibot.Site('en', 'wikipedia')

# catname = 'Category:Bonisoli (surname)'
#catname = 'Category:Uses of Wikidata Infobox with no family name'
#catname = 'Category:Uses of Wikidata Infobox with no given name'
# catname = 'Category:Commons category link is on Wikidata using P373'
# catname = 'Category:Photos by Mike Peel using an iPhone SE'
# catname = 'Category:Commons category link is the pagename'
catname = 'Category:Commons category link is defined as the pagename'
# catname = 'Category:Commons category link is locally defined'
# catname = 'Category:Pages with script errors'
# catname = 'Category:Articles without Wikidata item'
# catname = 'Category:Uncategorized categories'
# catname = 'Category:Uses of MonumentID with no picture on Wikidata'
# catname = 'Category:Short description with empty Wikidata description'
# catname = 'Category:Articles with missing Wikidata information'
# catname=  'Category:Inconsistent wikidata for Commons category'
# catname = 'Category:Photos by Mike Peel'
cat = pywikibot.Category(commons,catname)
print(cat)
i = 0
trip = 1
first = ''
for result in pagegenerators.CategorizedPageGenerator(cat, recurse=False):
# for result in pagegenerators.SubCategoriesPageGenerator(cat, recurse=False):
	print(result.title())
	# if first == '':
	# 	first = result.title()[0]
	# if first != result.title()[0]:
	# 	input('Continue?')
	# 	first = result.title()[0]
	if trip == 0:
		if 'Cahuilla' in result.title():
			trip = 1
		else:
			continue
	# try:
	result.touch()
	# except:
	# 	null = 1
	i += 1
	print (i)

