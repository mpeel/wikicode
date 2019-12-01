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
templates = ['commonscat', 'Commonscat', 'commonscategory', 'Commonscategory', 'commons category', 'Commons category', 'commons cat', 'Commons cat', 'Commons category-inline', 'commons category-inline', 'Commons cat-inline', 'commons cat-inline', 'commonscat-inline', 'Commonscat-inline', 'Commons category inline', 'commons category inline', 'commons-cat-inline', 'Commons-cat-inline', 'Commons cat inline', 'commons cat inline', 'commonscat inline', 'Commonscat inline', 'Commons Category', 'commons Category','commonscatinline', 'Commonscatinline']

catredirect_templates = ["category redirect", "Category redirect", "seecat", "Seecat", "see cat", "See cat", "categoryredirect", "Categoryredirect", "catredirect", "Catredirect", "cat redirect", "Cat redirect", "catredir", "Catredir", "redirect category", "Redirect category", "cat-red", "Cat-red", "redirect cat", "Redirect cat", "category Redirect", "Category Redirect", "cat-redirect", "Cat-redirect"]

targetcats = ['Category:Commons category link is on Wikidata using P373','Category:Commons category link is locally defined‎','Category:Commons category link is defined as the pagename']

for categories in range(0,2):
	for targetcat in targetcats:
		cat = pywikibot.Category(enwp, targetcat)
		if categories == 0:
			pages = pagegenerators.SubCategoriesPageGenerator(cat, recurse=False);
		else:
			pages = pagegenerators.CategorizedPageGenerator(cat, recurse=False);
		for page in pages:

			# Optional skip-ahead to resume broken runs
			if trip == 0:
				if "AC Nagano Parceiro" in page.title():
					trip = 1
				else:
					print(page.title())
					continue

			# Cut-off at a maximum number of edits	
			print("")
			print("")
			print("")
			print("")
			print("")
			print(nummodified)
			if nummodified >= maxnum:
				print('Reached the maximum of ' + str(maxnum) + ' entries modified, quitting!')
				exit()

			print("\nhttp://"+prefix+".wikipedia.org/wiki/" + page.title().replace(' ','_'))

			# Get the Wikidata item
			try:
				wd_item = pywikibot.ItemPage.fromPage(page)
				item_dict = wd_item.get()
				qid = wd_item.title()
				print(qid)
			except:
				# If that didn't work, go no further
				print(page.title() + ' - no page found')
				wd_item = 0
				item_dict = 0
				qid = 0
				sitelink_check = 0
				# continue

			# If we have a P910 value, switch to using that Wikidata item
			if qid != 0:
				try:
					existing_id = item_dict['claims']['P910']
					print('P910 exists, following that.')
					for clm2 in existing_id:
						wd_item = clm2.getTarget()
						item_dict = wd_item.get()
						qid = wd_item.title()
						print(wd_item.title())
				except:
					null = 0

				# Double-check that there is a sitelink on Wikidata
				try:
					sitelink = item_dict['sitelinks']['commonswiki']
					sitelink_check = 1
				except:
					sitelink_check = 0
				print("sitelink: " + str(sitelink_check))

			if sitelink_check == 1:
				continue

			print("\nhttp://"+prefix+".wikipedia.org/wiki/" + page.title().replace(' ','_'))

			try:
				p373 = item_dict['claims']['P373']
				for clm in p373:
					val = clm.getTarget()
					p373cat = u"Category:" + val
					print('Remove P373?')
					print(' http://www.wikidata.org/wiki/'+qid)
					print(' ' + str(p373cat))
					test = 'y'
					savemessage = 'Remove incorrect P373 value'
					if debug == 1:
						print(savemessage)
						test = input("Continue? ")
					if test == 'y':
						wd_item.removeClaims(clm,summary=savemessage)
			except:
				null = 0


			# Get the candidate commonscat link
			try:
				target_text = page.get()
			except:
				continue

			# Count the number of occurances
			numtemplates = 0
			target_text_temp = target_text
			for i in range(0,len(templates)):
				numtemplates = numtemplates + target_text_temp.count(templates[i])
				target_text_temp = target_text_temp.replace(templates[i],'')

			id_val = 0
			abort = 0
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
				# for i in range(0,len(templates)):
					# if '{{'+templates[i]+'}}' in target_text:

				continue

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

			print('Current category is:')
			print(' http://commons.wikimedia.org/wiki/Category:'+id_val.replace(' ','_'))
			print('Remove from enwp?')

			target_text = target_text.replace(commonscat_string2a + commonscat_string2+'}}\n', '')
			page.text = target_text
			test = 'y'
			if numtemplates != 1:
				print('Number of commons links: ' + str(numtemplates))
			savemessage = "Removing Commons category link that doesn't match this "
			if categories == 0:
				savemessage = savemessage + "category"
			else:
				savemessage = savemessage + "article"
			if debug == 1:
				# print(target_text)
				# print(id_val)
				print(savemessage)
				test = input("Continue? ")
			if test == 'y':
				nummodified += 1
				page.save(savemessage)
				continue


print('Done! Edited ' + str(nummodified) + ' entries')
		
# EOF