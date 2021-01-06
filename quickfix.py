#!/usr/bin/python
# -*- coding: utf-8  -*-
# Find cases where the sitelink move was attempted but failed
# Mike Peel     24-May-2019      v1

from __future__ import unicode_literals

import pywikibot
from pywikibot.data import api
import numpy as np
import time
import string
from pywikibot import pagegenerators
import urllib
import pprint
import csv
import json
from pibot_functions import *

seen = []

wikidata_site = pywikibot.Site("wikidata", "wikidata")
repo = wikidata_site.data_repository()  # this is a DataSite object
commons = pywikibot.Site('commons', 'commons')

user = pywikibot.User(commons,'Ton1~commonswiki')
targets = user.contributions(total=5000);
trip = 1
for target in targets:
	# target_item = pywikibot.ItemPage(commons, target[0])
	pagetext = target[0].get()
	print(target[0].title())
	if 'File' in target[0].title() and 'Information' not in pagetext and 'information' not in pagetext:
		print(pagetext)
		pagetext = pagetext.replace('[[Category:Media missing infobox template]]','')
		pagetext = pagetext.replace('{{No source since|month=May|day=25|year=2019}}','')
		intro = pagetext.split('{{GFDL')[0]
		pagetext = "=={{int:filedesc}}==\n\
{{Information\n\
|Description = "+intro.strip()+"\n\
|Source      = {{own}}\n\
|Date        = \n\
|Author      = {{u|Ton1~commonswiki}}\n\
}}\n\n\
=={{int:license-header}}==\n" + pagetext.replace(intro,'')
		pagetext = pagetext.replace('}[','}\n\n[')
		pagetext = pagetext.replace('][',']\n[')
		pagetext = pagetext.replace(']\n\n[',']\n[')
		target[0].text = pagetext
		print(pagetext)
		text = 'n'
		print(target[0].title())
		text = input("Save? ")
		if text != "n":
			target[0].save('Adding information template')
	

# 	if "Moving commons category sitelink" in targetcat[3]:
# 		if "Moving commons category sitelink from main item" in targetcat[3] or "fix incomplete move due to lag" in targetcat[3]:
# 			qid = targetcat[3].split('(')[1].split(')')[0]
# 			print(qid)
# 			print(targetcat[0].title())
# 			seen.append(targetcat[0].title())
# 		elif "Moving commons category sitelink to category item" in targetcat[3]:
# 			qid = targetcat[3].split('(')[1].split(')')[0]
# 			print(qid)
# 			if qid not in seen:
# 				print('There is a problem')
# 				print(targetcat[0].title())
# 				target_item = pywikibot.ItemPage(repo, targetcat[0].title())
# 				target_dict = target_item.get()

# 				# Check to see if it's already been fixed
# 				sitelink = ''
# 				target_item2 = pywikibot.ItemPage(repo, qid)
# 				target_dict2 = target_item2.get()
# 				try:
# 					sitelink = get_sitelink_title(target_dict2['sitelinks']['commonswiki'])
# 				except:
# 					print('No sitelink')
# 				if sitelink != '':
# 					seen.append(qid)
# 				else:
# 					targetedits = target_item.revisions()
# 					for revision in targetedits:
# 						print(revision)
# 						revision_page = json.loads(target_item.getOldVersion(revision.revid))
# 						print(revision_page)
# 						try:
# 							print(revision_page['sitelinks']['commonswiki']['title'])
# 						except:
# 							print('nope')
# 						try:
# 							sitelink = revision_page['sitelinks']['commonswiki']['title']
# 							break
# 						except:
# 							continue
# 					data = {'sitelinks': [{'site': 'commonswiki', 'title': sitelink}]}
# 					print(data)
# 					cat_item = pywikibot.ItemPage(repo, qid)
# 					# text = input("Save? ")
# 					# if text == 'y':
# 					print('Saving!')
# 					try:
# 						cat_item.editEntity(data, summary=u'Moving commons category sitelink from main item item (' + str(targetcat[0].title()) + ') - fix incomplete move due to lag')
# 					except:
# 						print('Problem with ' + str(qid) + ' from ' + str(targetcat[0].title()))
# 						exit()
						

# # EOF