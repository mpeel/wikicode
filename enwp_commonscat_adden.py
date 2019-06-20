#!/usr/bin/python
# -*- coding: utf-8  -*-
# Add enwp sitelinks based on commons categories
# Mike Peel     15-Jun-2019      v1 - start

from __future__ import unicode_literals

import pywikibot
import numpy as np
import time
import string
from pywikibot import pagegenerators
import urllib
from pibot_functions import *
import mysql.connector
from database_login import *

mydb = mysql.connector.connect(
  host=database_host,
  user=database_user,
  passwd=database_password,
  database=database_database
)
mycursor = mydb.cursor()

maxnum = 100000
nummodified = 0

wikidata_site = pywikibot.Site("wikidata", "wikidata")
repo = wikidata_site.data_repository()  # this is a DataSite object
commons = pywikibot.Site('commons', 'commons')
enwp = pywikibot.Site('en', 'wikipedia')
debug = 1
trip = 1
templates = ['commonscat', 'Commonscat', 'commonscategory', 'Commonscategory', 'commons category', 'Commons category', 'commons cat', 'Commons cat', 'Commons category-inline', 'commons category-inline', 'Commons cat-inline', 'commons cat-inline', 'commonscat-inline', 'Commonscat-inline', 'Commons category inline', 'commons category inline', 'commons-cat-inline', 'Commons-cat-inline', 'Commons cat inline', 'commons cat inline', 'commonscat inline', 'Commonscat inline', 'Commons Category', 'commons Category','commonscatinline', 'Commonscatinline']

catredirect_templates = ["category redirect", "Category redirect", "seecat", "Seecat", "see cat", "See cat", "categoryredirect", "Categoryredirect", "catredirect", "Catredirect", "cat redirect", "Cat redirect", "catredir", "Catredir", "redirect category", "Redirect category", "cat-red", "Cat-red", "redirect cat", "Redirect cat", "category Redirect", "Category Redirect", "cat-redirect", "Cat-redirect"]

targetcats = ['Commons category link is the pagename‎', 'Commons category link is defined as the pagename‎', 'Commons category link is locally defined‎']

for categories in range(0,2):
	for targetcat in targetcats:
		cat = pywikibot.Category(enwp, targetcat)
		if categories == 1:
			pages = pagegenerators.SubCategoriesPageGenerator(cat, recurse=False);
		else:
			pages = pagegenerators.CategorizedPageGenerator(cat, recurse=False);
		for page in pages:

			# Optional skip-ahead to resume broken runs
			if trip == 0:
				if "Exposition Internationale des Arts" in page.title():
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

			print("\n" + page.title())

			# See if we have a Wikidata item already
			try:
				wd_item = pywikibot.ItemPage.fromPage(page)
				item_dict = wd_item.get()
				qid = wd_item.title()
				print("Has a sitelink already - " + qid)
				continue
			except:
				# If that didn't work, go no further
				print(page.title() + ' - no page found')
				wd_item = 0
				item_dict = 0
				qid = 0
				sitelink_check = 0
				# continue

			# If we're here, then we don't have one, see if we can add it through the commons category

			# Get the candidate commonscat link
			try:
				target_text = page.get()
			except:
				print("Something is wrong here - fix it")
				text = raw_input("Save? ")
				continue
				
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
				print 'No commonscat'
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
			if "{" in id_val or "<" in id_val or ">" in id_val or "]" in id_val or "[" in id_val or 'position=' in id_val or 'position =' in id_val:
				print('Bad character in commonscat')
				continue

			print(id_val)
			commonscat = u"Category:" + id_val

			# Try to get the Wikidata item from the Commons category
			try:
				cat = pywikibot.Category(commons, commonscat)
				wd_item = pywikibot.ItemPage.fromPage(cat)
				item_dict = wd_item.get()
				qid = wd_item.title()
				print(qid)
			except:
				# If that didn't work, go no further
				print(commonscat + ' - no page found')
				continue

			if 'Category:' not in page.title():
				# If we have a P301 value, switch to using that Wikidata item
				try:
					existing_id = item_dict['claims']['P301']
					print('P301 exists, following that.')
					for clm2 in existing_id:
						wd_item = clm2.getTarget()
						item_dict = wd_item.get()
						qid = wd_item.title()
						print(wd_item.title())
				except:
					null = 0

			# Skip if there is already a sitelink on Wikidata
			try:
				sitelink = item_dict['sitelinks']['enwiki']
				sitelink_check = 1
			except:
				sitelink_check = 0
			print("sitelink: " + str(sitelink_check))
			if sitelink_check == 1:
				print('Sitelink exists, continuing')
				continue

			# If we're here, then we can add a sitelink
			data = {'sitelinks': [{'site': 'enwiki', 'title': page.title()}]}
			print 'http://www.wikidata.org/wiki/'+qid
			try:
				print item_dict['labels']['en']
			except:
				print ''
			print 'http://en.wikipedia.org/wiki/' + page.title()
			print 'http://commons.wikimedia.org/wiki/'+commonscat
			text = raw_input("Save? ")
			if text != 'n':
				wd_item.editEntity(data, summary=u'Add enwp sitelink')
				nummodified += 1

# EOF