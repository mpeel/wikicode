#!/usr/bin/python
# -*- coding: utf-8  -*-
# Remove locally defined commons category links when bad or pointing to a redirect
# Mike Peel     22-May-2020      v1 - start

import pywikibot
import numpy as np
import time
import string
from pywikibot import pagegenerators
import urllib
from pibot_functions import *

nummodified = 0

wikidata_site = pywikibot.Site("wikidata", "wikidata")
repo = wikidata_site.data_repository()  # this is a DataSite object
enwp = pywikibot.Site('en', 'wikipedia')
debug = 1
trip = 1
maxnum = 10000
usecats = False
targetitem = 'Q3621491'
otheritems = ['Q56842676','Q15983985','Q25915497','Q1350189','Q52231239']
banner = ['WikiProject Archaeology','WP Archaeology','WP Archeology']
tags = ['women=yes','women=y','women=Yes']
cats = ['Category:Women archaeologists','Category:British women archaeologists','Category:Indian women archaeologists']
if usecats == True:
	targetcats = cats
else:
	targetcats = [targetitem] + otheritems
for targetcat in targetcats:
	print(targetcat)
	if usecats == True:
		cat = pywikibot.Category(enwp, targetcat)
		pages = pagegenerators.CategorizedPageGenerator(cat, recurse=False);
	else:
		query = 'SELECT ?item WHERE {'\
		'?item wdt:P106 wd:'+targetcat+' .'\
		'?item wdt:P21 wd:Q6581072 .'\
		'FILTER EXISTS {'\
		'	?wen schema:about ?item .'\
		'	?wen schema:isPartOf <https://en.wikipedia.org/> .'\
		'}'\
		'}'
		print(query)
		pages = pagegenerators.WikidataSPARQLPageGenerator(query, site=repo)

	for page in pages:
		# Optional skip-ahead to resume broken runs
		if trip == 0:
			if "Bonneau" in page.title():
				trip = 1
			else:
				print(page.title())
				continue

		# Cut-off at a maximum number of edits	
		print("")
		print(nummodified)
		if nummodified >= maxnum:
			print('Reached the maximum of ' + str(maxnum) + ' entries modified, quitting!')
			exit()

		if usecats == True:
			# Get the Wikidata item
			try:
				wd_item = pywikibot.ItemPage.fromPage(page)
				item_dict = wd_item.get()
				qid = wd_item.title()
				print("http://www.wikidata.org/wiki/"+qid)
			except:
				# If that didn't work, go no further
				print(page.title() + ' - no page found')
				wd_item = 0
				item_dict = 0
				qid = 0
				sitelink_check = 0
				# continue
		else:
			wd_item = page
			item_dict = wd_item.get()
			qid = wd_item.title()
			page = pywikibot.Page(enwp, item_dict['sitelinks']['enwiki'])
			print("\nhttp://en.wikipedia.org/wiki/" + page.title().replace(' ','_'))


		check_human = False
		try:
			p31 = item_dict['claims']['P31']
			for clm in p31:
				if 'Q5' in clm.getTarget().title():
					check_human = True
		except:
			input('No P31, check?')
		if check_human == False:
			input('Not human, check?')
			continue
		check_woman = False
		try:
			p21 = item_dict['claims']['P21']
			for clm in p21:
				if 'Q6581072' in clm.getTarget().title():
					check_woman = True
		except:
			input('No P21, check?')
		if check_woman == False:
			input('Not female, check?')
			continue

		check_occupation = False
		try:
			p106 = item_dict['claims']['P106']
			for clm in p106:
				if targetitem in clm.getTarget().title():
					check_occupation = True
				else:
					for alt in otheritems:
						if alt in clm.getTarget().title():
							check_occupation = True
		except:
			null = 1
		if check_occupation == False:
			add_occupation = input('Not archaeologist, add it?')
			if add_occupation == 'y':
				newclaim = pywikibot.Claim(repo, 'P106')
				newclaim.setTarget(pywikibot.ItemPage(repo, targetitem))
				print(newclaim)
				wd_item.addClaim(newclaim, summary=u'Setting P106 value')
			else:
				continue

		talk = pywikibot.Page(enwp, 'Talk:'+page.title())
		hastalk = False
		hasbanner = False
		hastag = False
		try:
			talk_text = talk.get()
			hastalk = True
		except:
			maketalk = input('No talk page, start it?')
			if maketalk == 'y':
				talk.text = "{{"+banner[0]+"|"+tags[0]+"}}"
				talk.save("Starting talk page, adding " + banner[0])
				talk_text = talk.get()
		if hastalk:
			for b in banner:
				talk_text = talk_text.replace(b,banner[0])
			test = talk_text.split(banner[0])
			if len(test) > 1:
				hasbanner = True
				test2 = test[1].split('}}')
				for tag in tags:
					if tag in test2[0]:
						hastag = True
		if not hastag:
			print('http://en.wikipedia.org/wiki/Talk:'+page.title().replace(' ','_'))
			if hasbanner:
				talk_text = talk_text.replace(banner[0],banner[0]+'|'+tags[0])
				if talk_text != talk.get():
					print(talk_text)
					savemessage = 'Add '+tags[0]+' parameter to '+banner[0]
					print(savemessage)
					savetalk = input('Save talk page?')
					if savetalk == 'y':
						talk.text = talk_text
						talk.save(savemessage,minor=False)
				else:
					input('Not able to add tag, check?')

			else:
				input('No banner found, add it manually?')


		# Get the page
		haspage = False
		try:
			target_text = page.get()
			haspage = True
		except:
			input('No page, how did that happen?')
		hascat = False
		if haspage:
			print(cats)
			for testcat in cats:
				if testcat in target_text:
					hascat = True
		if not hascat:
			pos = target_text.rfind(']')

			target_text = target_text[:pos+1] + '\n[['+cats[0]+']]'+target_text[pos+1:]
			if target_text != page.get():
				print(target_text)
				savemessage = 'Add [['+cats[0]+']]'
				print(savemessage)
				savepage = input('Save article?')
				if savepage == 'y':
					page.text = target_text
					page.save(savemessage,minor=False)
			else:
				input('Not able to add category, check?')


print('Done! Edited ' + str(nummodified) + ' entries')
	
# EOF