#!/usr/bin/python
# -*- coding: utf-8  -*-
# Import coordinates from enwp
# 23 Dec 2020	Mike Peel	Started

import pywikibot
from pywikibot import pagegenerators

def get_precision(val):
	# print(val)
	if '.' in str(val):
		val = val.split('.')[1]
		length = len(val)
	else:
		length = 0
	if length >= 5:
		length = 5
	# print(len(val))
	return 10**-length

def calc_coord(params):
	print(params)
	lat = False
	lon = False
	precision = False
	if len(params) >= 8:
		if 'S' in params[3] or 'N' in params[3]:
			lat = float(params[0]) + (float(params[1])/60.0)+(float(params[2])/(60.0*60.0))
			if 'S' in params[3]:
				lat = -lat
			lon = float(params[4]) + (float(params[5])/60.0)+(float(params[6])/(60.0*60.0))
			if 'W' in params[7] or 'O' in params[7]:
				lon = -lon
			precision = get_precision(params[2])/(60.0*60.0)
	if lat == False and len(params) > 2:
		if ('S' in params[2] or 'N' in params[2]) and len(params) >= 5:
			lat = float(params[0]) + (float(params[1])/60.0)
			if 'S' in params[2]:
				lat = -lat
			lon = float(params[3]) + (float(params[4])/60.0)
			if 'W' in params[5] or 'O' in params[5]:
				lon = -lon
			precision = get_precision(params[1])/(60.0)
		elif (params[1] == 'N' or params[1] == 'S') and len(params) >= 3:
			lat = float(params[0])
			lon = float(params[2])
			precision = get_precision(params[0])
			if params[1] == 'S':
				lat = -lat
			if params[3] == 'W' or params[3] == 'O':
				lon = -lon
		elif '.' in params[0] and '.' in params[1]:
			lat = float(params[0])
			lon = float(params[1])
			precision = get_precision(params[0])
		else:
			print(params)
			print('Something odd in calc_coord (1)')
			# return False, False, False
	elif '.' in params[0] and '.' in params[1]:
		lat = float(params[0])
		lon = float(params[1])
		precision = get_precision(params[0])

	if lat == False:
		print(params)
		print('Something odd in calc_coord (2)')
		# return False, False, False
	# print(lon)
	# print(lat)
	# print(precision)
	return lat, lon, precision


# lang = 'pt'
lang = 'en'
wiki = pywikibot.Site(lang, 'wikipedia')
repo = wiki.data_repository()
globe_item = pywikibot.ItemPage(repo, 'Q2')
debug = False
numedited = 0
maxnumedited = 10000

cat = pywikibot.Category(wiki, 'Category:Coordinates not on Wikidata')
# cat = pywikibot.Category(wiki, 'Categoria:!Artigos com coordenadas por transcrever a Wikidata')
# cat = pywikibot.Category(wiki, 'Categoria:!Artigos com coordenadas locais')
coord_templates = ['Coord']

pages = pagegenerators.CategorizedPageGenerator(cat, recurse=False);
for page in pages:
	# if page.title()[0] != 'C':
	# 	continue
	print('https://'+lang+'.wikipedia.org/wiki/'+page.title().replace(" ","_"))
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
	if P625 != '':
		page.touch()
		continue

	ishuman = False
	P31 = ''
	try:
		P31 = item_dict['claims']['P31']
	except:
		null = 0
	if P31 != '':
		for clm in P31:
			# print(clm)
			# print(clm.getTarget().title())
			if clm.getTarget().title() == 'Q5' or clm.getTarget().title() == 'Q4830453' or clm.getTarget().title() == 'Q783794' or clm.getTarget().title() == 'Q22667' or clm.getTarget().title() == 'Q13406463':
				ishuman = True
	if ishuman:
		print('Not importing coordinate for a human, business, company, railway or list')
		continue
	P159 = ''
	try:
		P159 = item_dict['claims']['P159']
	except:
		null = 0
	if P159 != '':
		# print(P159)
		print('Has a HQ, skipping')
		continue

	count = 0
	for template in page.templatesWithParams():
		for tpl in coord_templates:
			if tpl in template[0].title():
				count += 1
	print(count)
	if count > 2:
		print('Wrong number of coordinate templates (' + str(count) + '), skipping')
		# input('Check')
		continue

	done = False
	trip = False
	for template in page.templatesWithParams():
		if trip == True:
			break
		for tpl in coord_templates:
			if trip == True:
				break
			# print(tpl)
			if not done:
				if tpl in template[0].title() and 'missing' not in template[0].title():
					# print(template)
					print(template[0].title())
					print(template[1])
					try:
						lat, lon, precision = calc_coord(template[1])
					except:
						trip = True
					if trip == True:
						# input('Check2')
						break
					if lat == False:
						# input('Cherk3')
						break
					if not coordinate and precision > 0.0:
						coordinateclaim  = pywikibot.Claim(repo, u'P625')
						coordinate = pywikibot.Coordinate(lat=lat, lon=lon, precision=precision, site=wiki,globe_item=globe_item)
						coordinateclaim.setTarget(coordinate)
						test = 'y'
						if debug:
							print(coordinate)
							test = input('Save coordinate?')
						if test == 'y':
							wd_item.addClaim(coordinateclaim, summary=u'Importing coordinate from '+lang+'wp')
							done = True
							numedited += 1
							page.touch()

	if numedited >= maxnumedited:
		print(numedited)
		exit()
