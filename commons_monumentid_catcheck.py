#!/usr/bin/python
# -*- coding: utf-8  -*-
# Check through MonumentID uses to make sure they're in categories
# Started 7 August 2023 by Mike Peel
import pywikibot
import numpy as np
import time
import string
from pywikibot import pagegenerators
import urllib
from pibot_functions import *

maxnum = 1000000
nummodified = 0

commons = pywikibot.Site('commons', 'commons')
repo = commons.data_repository()  # this is a DataSite object
debug = True
manual = True
savemessage="Add category for monument"
skipto = 'File:Igreja de São Pedro dos Clérigos Salvador Portals 2018-1824.jpg'
# Start the category walker
template = pywikibot.Page(commons, 'Template:MonumentID')
images = template.embeddedin()
hiddencats = []
normalcats = []

for image in images:
	print(image.title())
	if 'File:' not in image.title():
		print('Not a file, skipping...')
		continue
	if skipto != '':
		if image.title() != skipto:
			continue
		else:
			skipto = ''
	# Get the sitelink from Commons
	try:
		qid = image.text.split('{{MonumentID|')[1].split('}}')[0]
	except:
		qid = image.text.split('{{MonumentIDPortugal|')[1].split('}}')[0]
	wd_item = pywikibot.ItemPage(repo, qid)
	if wd_item.isRedirectPage():
		wd_item = wd_item.getRedirectTarget()
	item_dict = wd_item.get()
	try:
		existing_id = item_dict['claims']['P910']
		print('P910 exists, following that.')
		for clm2 in existing_id:
			wd_item = clm2.getTarget()
			item_dict = wd_item.get()
			print(wd_item.title())
			# print(item_dict)
	except:
		print('P910 not found')
	try:
		sitelink = get_sitelink_title(item_dict['sitelinks']['commonswiki'])
	except:
		print('No sitelink, continuing')
		continue
	print(sitelink)
	testcat = pywikibot.Category(commons, sitelink)
	subcats = []
	for subcat in testcat.subcategories(recurse=3):
		if subcat not in hiddencats:
			if subcat not in normalcats:
				if not subcat.isHiddenCategory():
					subcats.append(subcat.title())
					normalcats.append(subcat)
				else:
					hiddencats.append(subcat)
					print(hiddencats)
			else:
				subcats.append(subcat.title())
	for subcat in testcat.categories():
		if subcat not in hiddencats:
			if subcat not in normalcats:
				if not subcat.isHiddenCategory():
					subcats.append(subcat.title())
					normalcats.append(subcat)
				else:
					hiddencats.append(subcat)
					print(hiddencats)
			else:
				subcats.append(subcat.title())
	print(subcats)
	# Check through image categories, see if we have a match
	incat = False
	for cat in image.categories():
		print(cat.title())
		if sitelink == cat.title():
			incat = True
		for subcat in subcats:
			if subcat == cat.title():
				incat = True
			if subcat == sitelink:
				incat = True
	print(incat)
	if incat == False:
		image.text = image.text + "\n[["+sitelink+"]]"
		print("\n[["+sitelink+"]]")
		test = input('Save?')
		if test != 'n':
			image.save('Adding [[:' + sitelink + ']]')
# EOF