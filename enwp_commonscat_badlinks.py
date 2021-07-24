#!/usr/bin/python
# -*- coding: utf-8  -*-
# Change locally defined commons category links to the Wikidata one
# Mike Peel     10-Sep-2019      v1 - start

from __future__ import unicode_literals

import pywikibot
import numpy as np
import time
import string
from pywikibot import pagegenerators
import urllib
from pibot_functions import *
import random
# import mysql.connector
# from database_login import *

# mydb = mysql.connector.connect(
#   host=database_host,
#   user=database_user,
#   passwd=database_password,
#   database=database_database
# )
# mycursor = mydb.cursor()

maxnum = 100000
nummodified = 0

wikidata_site = pywikibot.Site("wikidata", "wikidata")
repo = wikidata_site.data_repository()  # this is a DataSite object
commons = pywikibot.Site('commons', 'commons')
enwp = pywikibot.Site('en', 'wikipedia')
enwp_site = 'enwiki'
prefix = 'en'
# enwp = pywikibot.Site('simple', 'wikipedia')
# enwp_site = 'simplewiki'
# prefix = 'simple'
debug = 1
trip = 1
trip_next = 0
only_replacements = False
check_sitelink = True
templates = ['commonscat', 'Commonscat', 'commonscategory', 'Commonscategory', 'commons category', 'Commons category', 'commons cat', 'Commons cat', 'Commons category-inline', 'commons category-inline', 'Commons cat-inline', 'commons cat-inline', 'commonscat-inline', 'Commonscat-inline', 'Commons category inline', 'commons category inline', 'commons-cat-inline', 'Commons-cat-inline', 'Commons cat inline', 'commons cat inline', 'commonscat inline', 'Commonscat inline', 'Commons Category', 'commons Category','commonscatinline', 'Commonscatinline']

catredirect_templates = ["category redirect", "Category redirect", "seecat", "Seecat", "see cat", "See cat", "categoryredirect", "Categoryredirect", "catredirect", "Catredirect", "cat redirect", "Cat redirect", "catredir", "Catredir", "redirect category", "Redirect category", "cat-red", "Cat-red", "redirect cat", "Redirect cat", "category Redirect", "Category Redirect", "cat-redirect", "Cat-redirect"]

targetcats = ['Category:Commons category link is defined as the pagename','Commons category link is locally defined','Category:Commons category link is on Wikidata using P373']
# targetcats = ['Commons category link is locally defined']

for targetcat in targetcats:
	for category in np.arange(0,2):
		cat = pywikibot.Category(enwp, targetcat)
		if category == 0:
			pages = pagegenerators.SubCategoriesPageGenerator(cat, recurse=False);
		else:
			pages = pagegenerators.CategorizedPageGenerator(cat, recurse=False);
		for page in pages:
			print('')
			print('https://en.wikipedia.org/wiki/'+page.title().replace(' ','_'))
			skip_rest = False
			if trip_next:
				trip = 1
				trip_next = 0
			# Optional skip-ahead to resume broken runs
			if trip == 0:
				if "List of New Jersey state parks" in page.title():
					trip_next = 1
					continue
				else:
					print(page.title())
					continue
			# Get the Wikidata item
			has_item = True
			try:
				wd_item = pywikibot.ItemPage.fromPage(page)
				item_dict = wd_item.get()
				qid = wd_item.title()
				print(qid)
			except:
				# If that didn't work, go no further
				print(page.title() + ' - no page found')
				has_item = False
			if not has_item:
				print('No item')
				continue

			print('b')
			sitelink = False
			try:
				sitelink = get_sitelink_title(item_dict['sitelinks']['commonswiki'])
			except:
				null = 0
			# Switch to category item?
			p910_followed = False
			try:
				existing_id = item_dict['claims']['P910']
				print('P910 exists, following that.')
				for clm2 in existing_id:
					wd_item = clm2.getTarget()
					item_dict = wd_item.get()
					qid = wd_item.title()
					print(wd_item.title())
					p910_followed = True
			except:
				null = 0
			if sitelink and p910_followed:
				if 'Category' in sitelink:
					input('Has sitelink in main item, check?')
			try:
				sitelink = get_sitelink_title(item_dict['sitelinks']['commonswiki'])
			except:
				sitelink = False
				null = 0

			if sitelink and 'Category:' not in sitelink:
				input('Check, sitelink is not to a category')
				continue
			if not sitelink:
				print('No sitelink')
			else:
				print('Has sitelink')

			# continue
			print("\nhttp://"+prefix+".wikipedia.org/wiki/" + page.title().replace(' ','_'))
			# Get the candidate commonscat link
			try:
				target_text = page.get()
			except:
				continue
			found=True
			count = 0

			while found == True:
				count += 1
				id_val = 0
				commonscat_string = ""
				for i in range(0,len(templates)):
					try:
						value = (target_text.split("{{"+templates[i]+"|"))[1].split("}}")[0]
						if value and id_val == 0:
							id_val = value
							commonscat_string = "{{"+templates[i]+"|"+id_val+"}}"
							commonscat_string2 = "|"+id_val
							commonscat_string2a = "{{"+templates[i]
					except:
						null = 1
						try:
							value = (target_text.split("{{"+templates[i]+" |1="))[1].split("}}")[0]
							if value and id_val == 0:
								id_val = value
								commonscat_string = "{{"+templates[i]+"|1="+id_val+"}}"
								commonscat_string2 = "|1="+id_val
								commonscat_string2a = "{{"+templates[i]
						except:
							null = 2
				if id_val == 0:
					# We didn't find the commons category link, skip this one.
					found = False
					for i in range(0,len(templates)):
						if '{{'+templates[i]+'}}' in target_text:
							commonscat_string2a = '{{'+templates[i]
							commonscat_string2 = ''
							id_val = ''
							found = True
				else:
					# Do some tidying of the link
					if "|" in id_val:
						try:
							if 'position' in id_val.split("|")[0] or 'bullet' in id_val.split("|")[0]:
								if 'position' in id_val.split("|")[1] or 'bullet' in id_val.split("|")[1]:
									id_val = id_val.split("|")[2]
								else:
									id_val = id_val.split("|")[1]
							else:
								id_val = id_val.split("|")[0]
						except:
							continue
					try:
						id_val = id_val.strip()
					except:
						null = 1

					# Check for bad characters
					if "{" in id_val or "<" in id_val or ">" in id_val or "]" in id_val or "[" in id_val or 'position=' in id_val or 'position =' in id_val or 'bullet=' in id_val or 'bullet =' in id_val:
						continue

					print(id_val)
					commonscat = u"Category:" + id_val

					target_text = target_text.replace("* " + commonscat_string2a + commonscat_string2+'}}\n', '')
					target_text = target_text.replace("* " + commonscat_string2a + commonscat_string2+'}}', '')
					target_text = target_text.replace("*" + commonscat_string2a + commonscat_string2+'}}\n', '')
					target_text = target_text.replace("*" + commonscat_string2a + commonscat_string2+'}}', '')
					target_text = target_text.replace(commonscat_string2a + commonscat_string2+'}}\n', '')
					target_text = target_text.replace(commonscat_string2a + commonscat_string2+'}}', '')

					commonscat = u"Category:" + id_val
					try:
						last_check = check_if_category_has_contents(commonscat,site=commons)
					except:
						input('Something went wrong here, check it.')
						last_check == True
					if last_check == False:
						text = page.text
						text = text.replace("* " + commonscat_string2a + commonscat_string2+'}}\n', '')
						text = text.replace("* " + commonscat_string2a + commonscat_string2+'}}', '')
						text = text.replace("*" + commonscat_string2a + commonscat_string2+'}}\n', '')
						text = text.replace("*" + commonscat_string2a + commonscat_string2+'}}', '')
						text = text.replace(commonscat_string2a + commonscat_string2+'}}\n', '')
						text = text.replace(commonscat_string2a + commonscat_string2+'}}', '')
						test = 'y'
						savemessage = "Removing Commons category ("+commonscat+") as it does not exist"
						print(id_val)
						print(savemessage)
						test = input("Continue? ")
						if test == 'y':
							nummodified += 1
							page.text = text
							page.save(savemessage,minor=False)
							continue
					if sitelink and check_sitelink and not skip_rest:
						if id_val.strip() != sitelink.replace('Category:','').strip():
							print('Hi')
							text = page.text
							text = text.replace("* " + commonscat_string2a + commonscat_string2+'}}\n', '')
							text = text.replace("* " + commonscat_string2a + commonscat_string2+'}}', '')
							text = text.replace("*" + commonscat_string2a + commonscat_string2+'}}\n', '')
							text = text.replace("*" + commonscat_string2a + commonscat_string2+'}}', '')
							text = text.replace(commonscat_string2a + commonscat_string2+'}}\n', '')
							text = text.replace(commonscat_string2a + commonscat_string2+'}}', '')
							test = 'y'
							savemessage = "Removing Commons category ("+commonscat+") that does not match this article"
							print(id_val)
							print(sitelink)
							print(savemessage)
							test = input("Continue? ")
							if test == 'y':
								nummodified += 1
								page.text = text
								page.save(savemessage,minor=False)
								continue
							if test == 'c':
								skip_rest = True
							

				if count > 20:
					print("There was a problem here")
					found = False




print('Done! Edited ' + str(nummodified) + ' entries')
		
# EOF