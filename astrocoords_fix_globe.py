#!/usr/bin/python
# -*- coding: utf-8  -*-
# Correct globes for non-Earth bodies
# Started 4 August 2022 by Mike Peel
import pywikibot
import numpy as np
import time
import string
from pywikibot import pagegenerators
import urllib

globe_names = ['Earth', 'Mars', 'Moon', 'Ceres', 'Mercury', 'Venus', 'phobos', 'deimos', 'ganymede', 'callisto', 'io', 'europa', 'mimas', 'enceladus', 'tethys', 'dione', 'rhea', 'titan', 'hyperion', 'iapetus', 'phoebe', 'miranda', 'ariel', 'umbriel', 'titania', 'oberon', 'triton', 'pluto']
globes = ['Q2', 'Q111', 'Q405', 'Q596', 'Q308', 'Q313', 'Q7547', 'Q7548', 'Q3169', 'Q3134', 'Q3123', 'Q3143', 'Q15034', 'Q3303', 'Q15047', 'Q15040', 'Q15050', 'Q2565', 'Q15037', 'Q17958', 'Q17975', 'Q3352', 'Q3343', 'Q3338', 'Q3322', 'Q3332', 'Q3359', 'Q339']

commons = pywikibot.Site('commons', 'commons')
repo = commons.data_repository()

for i in range(0,len(globes)):
	globe_item = pywikibot.ItemPage(repo, globes[i])
	for j in range(0,len(globes)):
		if i != j:
			print('Finding cases of coordinates on ' + str(globe_names[j]) + ' that should be on ' + str(globe_names[i]))
			query = 'SELECT DISTINCT ?item'\
			'{'\
			'   ?item wdt:P376 wd:'+str(globes[i])+' ;'\
			'         p:P625 ['\
			'           psv:P625 ['\
			'             wikibase:geoGlobe ?globe ;'\
			'           ] ;'\
			'           ps:P625 ?coord'\
			'         ]'\
			'  FILTER ( ?globe = wd:'+str(globes[j])+' )'\
			'}'
			generator = pagegenerators.WikidataSPARQLPageGenerator(query, site=repo)
			for wd_item in generator:
				item_dict = wd_item.get()
				print(wd_item.title())
				try:
					P625 = item_dict['claims']['P625']
				except:
					continue
				for clm in P625:
					coordinate = clm.getTarget()
					new_coordinate = pywikibot.Coordinate(lat=coordinate.lat, lon=coordinate.lon, precision=coordinate.precision, globe_item=globe_item,site=repo)
					# print(coordinate)
					# print(new_coordinate)
					clm.changeTarget(new_coordinate,summary='Correct globe to '+str(globe_names[i]) + ' based on P376 value')
