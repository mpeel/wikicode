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

# globe_names = ['Earth', 'Mars', 'Moon', 'Ceres', 'Mercury', 'Venus', 'phobos', 'deimos', 'ganymede', 'callisto', 'io', 'europa', 'mimas', 'enceladus', 'tethys', 'dione', 'rhea', 'titan', 'hyperion', 'iapetus', 'phoebe', 'miranda', 'ariel', 'umbriel', 'titania', 'oberon', 'triton', 'pluto']
globes = ['Q111', 'Q405', 'Q596', 'Q308', 'Q313', 'Q7547', 'Q7548', 'Q3169', 'Q3134', 'Q3123', 'Q3143', 'Q15034', 'Q3303', 'Q15047', 'Q15040', 'Q15050', 'Q2565', 'Q15037', 'Q17958', 'Q17975', 'Q3352', 'Q3343', 'Q3338', 'Q3322', 'Q3332', 'Q3359', 'Q339'] # 'Q2',

commons = pywikibot.Site('commons', 'commons')
repo = commons.data_repository()
debug = False

for i in range(0,len(globes)):
	globe_item = pywikibot.ItemPage(repo, globes[i])
	query = 'SELECT DISTINCT ?item'\
	'{'\
	'   ?item p:P625 ['\
	'           psv:P625 ['\
	'             wikibase:geoGlobe ?globe ;'\
	'           ] ;'\
	'           ps:P625 ?coord'\
	'         ]'\
	'  FILTER ( ?globe = wd:'+str(globes[i])+' )'\
	'  FILTER NOT EXISTS {?item wdt:P376 ?o}'\
	'}'
	print(query)
	generator = pagegenerators.WikidataSPARQLPageGenerator(query, site=repo)
	for wd_item in generator:
		item_dict = wd_item.get()
		print(wd_item.title())
		try:
			P376 = item_dict['claims']['P376']
		except:
			P376 = ''
		if P376 == '':
			newclaim = pywikibot.Claim(repo, 'P376')
			newclaim.setTarget(globe_item)
			if debug:
				text = input("Save link? ")
			else:
				text = 'y'
			if text != 'n':
				wd_item.addClaim(newclaim, summary=u'Adding P376 value to match coordinate globe')
