#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Move categories to a subcategory
# Mike Peel     11-Apr-2020      v1 - start
from __future__ import unicode_literals

import pywikibot
import numpy as np
import time
import string
from pywikibot import pagegenerators
from pywikibot import textlib

commons = pywikibot.Site('commons', 'commons')
repo = commons.data_repository()  # this is a DataSite object

while(True):

	categoryname = input('Category name?')
	categoryname = categoryname.strip()
	subcategoryname = input('Subcategory name?')
	subcategoryname = subcategoryname.strip()
	exclude = 'run'
	toexclude = []
	while exclude != '':
		exclude = input('Text to exclude?')
		exclude = exclude.strip()
		if exclude != '':
			toexclude.append(exclude)
	print(toexclude)
	input('Continue?')

	try:
		commonscat_page = pywikibot.Category(commons, categoryname)
		text = commonscat_page.get()
	except:
		try:
			commonscat_page = pywikibot.Category(commons, categoryname[-1])
			text = commonscat_page.get()
		except:
			print("Couldn't find the category, try again?")
			continue

	try:
		subcommonscat_page = pywikibot.Category(commons, subcategoryname)
		text = subcommonscat_page.get()
	except:
		try:
			subcommonscat_page = pywikibot.Category(commons, subcategoryname[-1])
			text = subcommonscat_page.get()
		except:
			print("Couldn't find the subcategory, try again?")
			continue

	# See if there are subcategories that we want to check in the future
	subcats = pagegenerators.SubCategoriesPageGenerator(commonscat_page, recurse=False);

	for subcat in subcats:
		print('\n')
		print(subcat.title())
		topass = False
		if subcat.title() == commonscat_page.title() or subcat.title() == subcommonscat_page.title():
			topass = True
		if toexclude != ['']:
			for exclude in toexclude:
				if exclude in subcat.title():
					topass = True
		if topass:
			continue
		
		try:
			target_text = subcat.get()
		except:
			print('Error, subcat not found!')
			continue
		target_text = target_text.replace("[["+commonscat_page.title(),"[["+subcommonscat_page.title())
		print(target_text)
		savemessage = 'Moving from "' + commonscat_page.title() + '" to "' + subcommonscat_page.title() + '"'
		# input('Continue?')
		subcat.text = target_text.strip()
		subcat.save(savemessage)



#EOF