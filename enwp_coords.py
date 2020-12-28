#!/usr/bin/python
# -*- coding: utf-8  -*-
# Import coordinates from enwp
# 23 Dec 2020	Mike Peel	Started

import pywikibot
from pywikibot import pagegenerators
import numpy as np
import astropy as ap

def get_precision(val):
	print(val)
	if '.' in str(val):
		val = val.split('.')[1]
		length = len(val)
	else:
		length = 0
	# print(len(val))
	return 10**-len(val)

def calc_coord(params):
	if len(params) >= 8:
		lat = float(params[0]) + (float(params[1])/60.0)+(float(params[2])/(60.0*60.0))
		if 'S' in params[3]:
			lat = -lat
		lon = float(params[4]) + (float(params[5])/60.0)+(float(params[6])/(60.0*60.0))
		if 'W' in params[7]:
			lon = -lon
		precision = get_precision(params[2])/(60.0*60.0)
	elif len(params) >= 2:
		lat = float(params[0])
		lon = float(params[1])
		precision = get_precision(params[0])
	# print(lon)
	# print(lat)
	# print(precision)
	return lat, lon, precision


wiki = pywikibot.Site('en', 'wikipedia')
repo = wiki.data_repository()
globe_item = pywikibot.ItemPage(repo, 'Q2')
debug = True

cat = pywikibot.Category(wiki, 'Category:Coordinates not on Wikidata')
coord_templates = ['Coord']

pages = pagegenerators.CategorizedPageGenerator(cat, recurse=False);
for page in pages:
	print('https://commons.wikimedia.org/wiki/'+page.title().replace(" ","_"))
	try:
		wd_item = pywikibot.ItemPage.fromPage(page)
		item_dict = wd_item.get()
	except:
		print("No Wikidata sitelink found")
		continue

	print('https://www.wikidata.org/wiki/'+wd_item.title())

	coordinate = False
	try:
		P625 = item_dict['claims']['P625']
	except:
		P625 = ''
	print(P625)
	if P625 != '':
		for clm in P625:
			try:
				coordinate = clm.getTarget()
				print(coordinate)
				print(coordinate.lat)
			except:
				P625 = 'Bad'
	if P625 == 'Bad':
		print('Problem with coordinates')
		continue

	ishuman = False
	try:
		P31 = item_dict['claims']['P31']
	except:
		null = 0
	print(P625)
	if P31 != '':
		for clm in P31:
			# print(clm)
			# print(clm.getTarget().title())
			if clm.getTarget().title() == 'Q5':
				ishuman = True
	if ishuman:
		print('Not importing coordinate for a human')
		continue

	# exit()

	count = 0
	for template in page.templatesWithParams():
		for tpl in coord_templates:
			if tpl in template[0].title():
				count += 1
	print(count)
	if count != 1:
		print('Wrong number of coordinate templates (' + str(count) + '), skipping')
		continue

	done = False
	for template in page.templatesWithParams():
		for tpl in coord_templates:
			# print(tpl)
			if not done:
				if tpl in template[0].title():
					# print(template)
					print(template[0].title())
					print(template[1])
					lat, lon, precision = calc_coord(template[1])
					if not coordinate:
						coordinateclaim  = pywikibot.Claim(repo, u'P625')
						coordinate = pywikibot.Coordinate(lat=lat, lon=lon, precision=precision, site=wiki,globe_item=globe_item)
						coordinateclaim.setTarget(coordinate)
						test = 'y'
						if debug:
							print(coordinate)
							test = input('Save coordinate?')
						if test == 'y':
							wd_item.addClaim(coordinateclaim, summary=u'Importing coordinate from enwp')
							done = True
