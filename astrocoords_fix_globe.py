#!/usr/bin/python
# -*- coding: utf-8  -*-
# Correct globes for non-Earth bodies
# Started 4 August 2022 by Mike Peel
# Tweaked 12 August 2022 by Mike Peel to include more globes
import pywikibot
import numpy as np
import time
import string
from pywikibot import pagegenerators
import urllib

globe_names = ['earth', 'mars', 'saturn', 'mercury', 'venus', 'jupiter', 'uranus', 'pluto', 'moon', 'ceres', 'titan', 'vesta', 'io', 'callisto', 'europa', 'ganymede', 'amalthea', 'enceladus', 'titania', 'oberon', 'umbriel', 'ariel', 'miranda', 'triton', 'charon', 'phobos', 'deimos', 'bennu', 'mimas', 'hyperion', 'dione', 'tethys', 'rhea', 'puck', 'proteus', 'eros', 'thebe', 'epimetheus', 'janus', 'iapetus', 'phoebe', 'lutetia', 'ida', 'itokawa', 'mathilde', 'steins', 'gaspra', 'ida i dactyl', 'churyumov', 'ryugu']
globes = ['Q2', 'Q111', 'Q193', 'Q308', 'Q313', 'Q319', 'Q324', 'Q339', 'Q405', 'Q596', 'Q2565', 'Q3030', 'Q3123', 'Q3134', 'Q3143', 'Q3169', 'Q3257', 'Q3303', 'Q3322', 'Q3332', 'Q3338', 'Q3343', 'Q3352', 'Q3359', 'Q6604', 'Q7547', 'Q7548', 'Q11558', 'Q15034', 'Q15037', 'Q15040', 'Q15047', 'Q15050', 'Q15662', 'Q16081', 'Q16711', 'Q16765', 'Q17751', 'Q17754', 'Q17958', 'Q17975', 'Q107556', 'Q149012', 'Q149374', 'Q149417', 'Q150249', 'Q158244', 'Q510728', 'Q844672', 'Q1385178']

commons = pywikibot.Site('commons', 'commons')
repo = commons.data_repository()

for i in range(0,len(globes)):
	globe_item = pywikibot.ItemPage(repo, globes[i])
	for j in range(0,len(globes)):
		if i != j:
			print('Finding cases of coordinates on ' + str(globe_names[j]).capitalise() + ' that should be on ' + str(globe_names[i]).capitalise())
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
					clm.changeTarget(new_coordinate,summary='Correct globe to '+str(globe_names[i]).capitalise() + ' based on P376 value')
