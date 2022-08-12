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

globes = ['Q111', 'Q193', 'Q308', 'Q313', 'Q319', 'Q324', 'Q339', 'Q405', 'Q596', 'Q2565', 'Q3030', 'Q3123', 'Q3134', 'Q3143', 'Q3169', 'Q3257', 'Q3303', 'Q3322', 'Q3332', 'Q3338', 'Q3343', 'Q3352', 'Q3359', 'Q6604', 'Q7547', 'Q7548', 'Q11558', 'Q15034', 'Q15037', 'Q15040', 'Q15047', 'Q15050', 'Q15662', 'Q16081', 'Q16711', 'Q16765', 'Q17751', 'Q17754', 'Q17958', 'Q17975', 'Q107556', 'Q149012', 'Q149374', 'Q149417', 'Q150249', 'Q158244', 'Q510728', 'Q844672', 'Q1385178']
commons = pywikibot.Site('commons', 'commons')
repo = commons.data_repository()

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
			wd_item.addClaim(newclaim, summary=u'Adding P376 value to match coordinate globe')
