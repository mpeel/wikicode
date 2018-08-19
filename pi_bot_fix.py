#!/usr/bin/python
# -*- coding: utf-8  -*-
# Move commons category sitelinks to category items where needed
# Mike Peel     10-Jun-2018      v1

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

editsummary = 'Add commons sitelink based on QID on Commons'
seen = []

wikidata_site = pywikibot.Site("wikidata", "wikidata")
repo = wikidata_site.data_repository()  # this is a DataSite object
commons = pywikibot.Site('commons', 'commons')

user = pywikibot.User(wikidata_site,'Pi bot')
targetcats = user.contributions(total=30000);
trip = 0
for targetcat in targetcats:
	if editsummary in targetcat[3]:
		if targetcat[0].title() not in seen:
			seen.append(targetcat[0].title())
			print targetcat[0].title()

			if trip == 0:
				if 'Q1693249' in targetcat[0].title():
					trip = 1
				else:
					continue

			target_item = pywikibot.ItemPage(repo, targetcat[0].title())
			target_dict = target_item.get()


			# Check for a P301 value
			# Or in the main topic
			wd_item_301 = 0
			title_301 = '###__###_##_#'
			try:
				p301 = target_dict['claims']['P301']
				print p301
				for clm2 in p301:
					wd_item_301 = clm2.getTarget()
					# item_dict_301 = wd_item_301.get()
					title_301 = wd_item_301.title()
			except:
				print 'No P301 found'
				null = 1

			sitelink = ''
			try:
				sitelink = target_dict['sitelinks']['commonswiki']
			except:
				print 'No sitelink'

			if sitelink != '':
				print sitelink
				sitelink_item = pywikibot.Page(commons, sitelink)
				target_text = sitelink_item.get()
				print target_text
				if targetcat[0].title() in target_text or title_301 in target_text or '{{Wikidata infobox}}' in target_text or '{{Wikidata Infobox}}' in target_text:
					print 'OK'
				else:
					print 'We have a problem'

					targetedits = target_item.revisions()
					for revision in targetedits:
						print revision.revid
						revision_page = target_item.getOldVersion(revision.revid)
						# print revision_page
						# revision_dict = revision_page.get()
						# pprint(revision_dict)
						#sitelink2 = revision_page['sitelinks']['commonswiki']
						# print revision_page
						try:
							sitelink2 = revision_page.split('"site":"commonswiki","title":"')[1]
						except:
							print 'Done finding sitelink candidates - would remove from this item.'
							print targetcat[0].title()
							print title_301
							text = raw_input("Save? ")
							if text == 'y':
								target_item.removeSitelink('commonswiki', summary=u'Fixing bot error by removing incorrect sitelink')
							break
						# print sitelink2
						sitelink2 = sitelink2.split('"')[0]	
						# sitelink2 = sitelink2.encode('utf8', 'replace')
						print sitelink2
						try:
							sitelink2_item = pywikibot.Page(commons, sitelink2)
							target_text2 = sitelink2_item.get()
						except:
							print 'Commons sitelink problem, continuing'
							continue
						# print target_text2
						if targetcat[0].title() in target_text2 or title_301 in target_text2:
							print 'This one was OK'
							print targetcat[0].title()
							print title_301
							data = {'sitelinks': [{'site': 'commonswiki', 'title': sitelink2}]}
							print data
							text = raw_input("Save? ")
							if text == 'y':
								target_item.editEntity(data, summary=u'Fixing bot error by reverting to the correct sitelink')

								try:
									p373 = target_dict['claims']['P373']
									print p373
									p373_check = 0
									for clm in p373:
										p373_check += 1
									# Only attempt to do this if there is only one value for P373
									if p373_check == 1:
										for clm2 in p373:
											# wd_item_373 = clm2.getTarget()
											clm2.changeTarget(sitelink2.replace('Category:',''), summary=u"Also fix P373 value")
									else:
										text = raw_input('Please check this one!')
								except:
									print 'No P301 found'

							break


