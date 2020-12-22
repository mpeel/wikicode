# !/usr/bin/python
# -*- coding: utf-8  -*-
# Check for consistency in commons category usage
# Mike Peel     01-Mar-2018      v1 - start

from __future__ import unicode_literals

import pywikibot
import numpy as np
import time
import string
from pywikibot import pagegenerators
import urllib
from pibot_functions import *
import time

maxnum = 10000
nummodified = 0

wikidata_site = pywikibot.Site("wikidata", "wikidata")
repo = wikidata_site.data_repository()  # this is a DataSite object
commons = pywikibot.Site('commons', 'commons')
langcode = 'en'
enwp = pywikibot.Site(langcode, 'wikipedia')
debug = 0
trip = 1
templates = ['commonscat', 'Commonscat', 'commonscategory', 'Commonscategory', 'commons category', 'Commons category', 'commons cat', 'Commons cat', 'commons_category', 'Commons_category', 'commons_cat', 'Commons_cat', 'Commons category-inline', 'commons category-inline', 'Commons cat-inline', 'commons cat-inline', 'commonscat-inline', 'Commonscat-inline', 'Commons category inline', 'commons category inline', 'commons-cat-inline', 'Commons-cat-inline', 'Commons cat inline', 'commons cat inline', 'commonscat inline', 'Commonscat inline', 'Commons Category', 'commons Category','commonscatinline', 'Commonscatinline','Autres projets','Ccat','ccat','Cc','cc']
targetcats = ['Category:Commons category link is the pagename', 'Category:Commons category link is defined as the pagename']
include_cat = True

for targetcat in targetcats:
	for category in np.arange(0,2):
		cat = pywikibot.Category(enwp, targetcat)
		if category == 0:
			pages = pagegenerators.SubCategoriesPageGenerator(cat, recurse=False);
		else:
			pages = pagegenerators.CategorizedPageGenerator(cat, recurse=False);
		for page in pages:
			if trip == 0:
				if "Varanasi" in page.title():
					trip = 1
				else:
					print(page.title())
					continue
			try:
				wd_item = pywikibot.ItemPage.fromPage(page)
				item_dict = wd_item.get()
				qid = wd_item.title()
			except:
				print('Huh - no page found')
				continue

			print("\n" + qid)
			print('https://'+langcode+'.wikipedia.org/wiki/'+page.title().replace(' ','_'))

			# Get the candidate page
			target_text = page.get()
			id_val = 0
			abort = 0
			null = 0
			for i in range(0,len(templates)):
				if id_val == 0:
					try:
						value = (target_text.split("{{"+templates[i]+"|"))[1].split("}}")[0].strip()
						values = (value.split("|"))
						if 'position' in values[0]:
							value = values[1]
						else:
							value = values[0]
						print('0')
						null = 0
						print(value)
						if value and id_val == 0:
							id_val = value
					except:
						null = 1
						try:
							value = (target_text.split("{{"+templates[i]+" |1="))[1].split("}}")[0].strip()
							print('1')
							null = 1
							print(value)
							if value and id_val == 0:
								id_val = value
							elif id_val != 0:
								print('Found multiple IDs')
						except:
							null = 2
							try:
								value = (target_text.split("{{"+templates[i])[1]).strip()
								# print(value)
								value = value.split("}}")[0].strip()
								print(value)
								values = (value.split("|"))
								print(values)
								if 'position' in values[1] or 'wiktionary' in values[1]:
									value = values[2]
								else:
									value = values[1]
								null = 2
								print('2')
								print(value)
								if value and id_val == 0:
									id_val = value
							except:
								null = 3
			print(null)
			# exit()
			if id_val == 0:
				try:
					p373 = item_dict['claims']['P373']
					print('P373 exists, following using.')
					for clm in p373:
						id_val = clm.getTarget()
				except:
					id_val = page.title().replace('Category:','')
			if id_val == 0:
				id_val = page.title().replace('Category:','')

			# Do some tidying of the link
			if id_val != 0:
				if "|" in id_val:
					if 'position' in id_val.split("|")[0] or 'bullet' in id_val.split("|")[0]:
						if 'position' in id_val.split("|")[1] or 'bullet' in id_val.split("|")[1]:
							id_val = id_val.split("|")[2]
						else:
							id_val = id_val.split("|")[1]
					else:
						id_val = id_val.split("|")[0]
				try:
					id_val = id_val.strip()
				except:
					null = 1

				if "{{PAGENAME" in id_val:
					id_val = page.title().replace('Category:','')

				try:
					id_val = id_val.strip()
				except:
					null = 1
				try:
					id_val = id_val.replace('Commons=', '').replace('Commons =','').replace('commons=', '').replace('commons =','').replace('Category:','').replace('category:','')
					if '|' in id_val:
						id_val = id_val.split('|')[0]
				except:
					null = 1
				try:
					id_val = id_val.strip()
				except:
					null = 1

				# Check for bad characters
				if "{" in id_val or "<" in id_val or "]" in id_val or "[" in id_val:
					continue
			else:
				id_val = page.title()

			id_val = id_val.replace('::',':')
			print(id_val)

			# If we have a P910 value, switch to using that item
			if include_cat:
				have_followed_p910 = False
				try:
					existing_id = item_dict['claims']['P910']
					print('P910 exists, following that.')
					for clm2 in existing_id:
						wd_item = clm2.getTarget()
						item_dict = wd_item.get()
						print(wd_item.title())
					have_followed_p910 = True
				except:
					null = 0

			# Double-check that we don't already have a sitelink
			try:
				sitelink = item_dict['sitelinks']['commonswiki']
				sitelink_check = 1
			except:
				sitelink_check = 0
			# Only attempt to do this if there is only one value for P373 and no existing sitelink
			if id_val != 0 and sitelink_check == 0:
				if include_cat:
					commonscat = u"Category:" + id_val
				else:
					commonscat = id_val
				commonscat = commonscat.replace('::',':')
				if commonscat[0] == ':':
					commonscat = commonscat[1:]

				# The commons category must already exist
				test = 'n'
				check = 0
				try:
					sitelink_page = pywikibot.Page(commons, commonscat)
					check = 1
				except:
					print('Found a bad sitelink')
				if check == 1:
					# Check the category to see if it already has a Wikidata item
					commonscat_sitelink_exists = 0
					try:
						commonscat_page = pywikibot.Page(commons, commonscat)
						commonscat_item = pywikibot.ItemPage.fromPage(commonscat_page)
						commonscat_item_dict = commonscat_item.get()
						commonscat_sitelink_exists = 1
					except:
						try:
							text = commonscat_page.get()
						except:
							print('Commons category does not exist - fix that?')
							# last_check = check_if_category_has_contents(id_val,site=commons)
							# if last_check:
							continue

						if '{{Disambig' not in text and '{{disambig' not in text and '{{Category redirect' not in text and '{{category redirect' not in text:

							# That didn't work, add it to the Wikidata entry
							data = {'sitelinks': [{'site': 'commonswiki', 'title': commonscat}]}
							print('http://www.wikidata.org/wiki/'+qid)
							print('http://commons.wikimedia.org/wiki/'+commonscat.replace(' ','_'))
							text = input("Save? ")
							if text != 'n':
								try:
									wd_item.editEntity(data, summary=u'Add commons sitelink')
								except:
									time.sleep(1)
									wd_item.editEntity(data, summary=u'Add commons sitelink')
								nummodified += 1

							print(nummodified)
							if nummodified >= maxnum:
								print('Reached the maximum of ' + str(maxnum) + ' entries modified, quitting!')
								exit()


print('Done! Edited ' + str(nummodified) + ' entries')
		
# EOF