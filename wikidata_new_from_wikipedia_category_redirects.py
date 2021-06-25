#!/usr/bin/python
# -*- coding: utf-8  -*-
# Get a list of wikidata infobox uses from Commons
# Mike Peel     26-Jun-2018     v1 - initial version
import pywikibot
import numpy as np
import time
import string
from pywikibot import pagegenerators
import codecs

languages = ['simple','de','en', 'pt', ]
catitems = ['Q4616723','Q8379318','Q4048908']
for lang in languages:
	site = pywikibot.Site(lang, 'wikipedia')
	repo = site.data_repository()  # this is a DataSite object

	skipping_cats = set()
	for item in catitems:
		print(item)
		cat = site.page_from_repository(item)
		if cat is None:
			continue
		skipping_cats.add(cat)
		# also add redirect templates
		skipping_cats.update(cat.getReferences(follow_redirects=False, with_template_inclusion=False, filter_redirects=True, namespaces=site.namespaces.CATEGORY))
	print(skipping_cats)
	outputfile = codecs.open(lang+'wp_category_redirects.csv', "w", "utf-8")
	for cat in skipping_cats:
		uses = cat.members(recurse=False);
		for use in uses:
			outputfile.write(use.title()+"\n")
	outputfile.close()