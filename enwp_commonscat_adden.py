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
from pywikibot.data import api
import urllib
from pibot_functions import *
from database_login import *

wikidata_site = pywikibot.Site("wikidata", "wikidata")
repo = wikidata_site.data_repository()  # this is a DataSite object
commons = pywikibot.Site('commons', 'commons')
enwp = pywikibot.Site('en', 'wikipedia')
enwp_site = 'enwiki'
prefix = 'en'
# enwp = pywikibot.Site('simple', 'wikipedia')
# enwp_site = 'simplewiki'
# prefix = 'simple'
def newitem(category, enwp, items,commonscat_has_item=False):
	new_item = pywikibot.ItemPage(repo)
	new_item.editLabels(labels={"en":enwp.title()}, summary="Creating item")
	candidate_item = pywikibot.ItemPage(repo, new_item.getID())
	print(candidate_item)

	if commonscat_has_item:
		data = {'sitelinks': [{'site': 'commonswiki', 'title': category.title()}, {'site': enwp_site, 'title': enwp.title()}]}
		candidate_item.editEntity(data, summary=u'Add commons and '+enwp_site+' sitelink')
	else:
		data = {'sitelinks': [{'site': enwp_site, 'title': enwp.title()}]}
		candidate_item.editEntity(data, summary=u'Add '+enwp_site+' sitelink')


	for item in items:
		claim = pywikibot.Claim(repo, item[0])
		if item[0] == 'P569' or item[0] == 'P570':
			claim.setTarget(item[1])
		else:
			claim.setTarget(pywikibot.ItemPage(repo, item[1]))
		try:
			candidate_item.addClaim(claim, summary=u'Setting '+item[0]+' value')
			claim.addSources([statedin, retrieved], summary=u'Add source.')
		except:
			print("That didn't work")
	return

def search_entities(site, itemtitle):
	 params = { 'action' :'wbsearchentities', 
				'format' : 'json',
				'language' : 'en',
				'type' : 'item',
				'search': itemtitle}
	 request = api.Request(site=site, parameters=params)
	 return request.submit()

maxnum = 100000
nummodified = 0

debug = 1
trip = 1
templates = ['commonscat', 'Commonscat', 'commonscategory', 'Commonscategory', 'commons category', 'Commons category', 'commons cat', 'Commons cat', 'Commons category-inline', 'commons category-inline', 'Commons cat-inline', 'commons cat-inline', 'commonscat-inline', 'Commonscat-inline', 'Commons category inline', 'commons category inline', 'commons-cat-inline', 'Commons-cat-inline', 'Commons cat inline', 'commons cat inline', 'commonscat inline', 'Commonscat inline', 'Commons Category', 'commons Category','commonscatinline', 'Commonscatinline']

catredirect_templates = ["category redirect", "Category redirect", "seecat", "Seecat", "see cat", "See cat", "categoryredirect", "Categoryredirect", "catredirect", "Catredirect", "cat redirect", "Cat redirect", "catredir", "Catredir", "redirect category", "Redirect category", "cat-red", "Cat-red", "redirect cat", "Redirect cat", "category Redirect", "Category Redirect", "cat-redirect", "Cat-redirect"]

targetcats = ['Commons category link is the pagename‎', 'Commons category link is defined as the pagename‎', 'Commons category link is locally defined‎']

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
				text = input("Save? ")
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
				id_val = page.title()
				# print('No commonscat')
				# continue

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
			commonscat_has_item = False
			try:
				commonscat_item = pywikibot.Category(commons, commonscat)
			except:
				# Not much more we can do here if the commonscat doesn't exist
				continue
			try:
				wd_item = pywikibot.ItemPage.fromPage(commonscat_item)
				item_dict = wd_item.get()
				qid = wd_item.title()
				print(qid)
				commonscat_has_item = True
			except:
				# If that didn't work, go no further
				print(commonscat + ' - no wikidata item found')

			if commonscat_has_item:
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
					sitelink = item_dict['sitelinks'][enwp_site]
					sitelink_check = 1
				except:
					sitelink_check = 0
				print("sitelink: " + str(sitelink_check))
				if sitelink_check == 1:
					print('Sitelink exists, continuing')
					continue

				# If we're here, then we can add a sitelink
				data = {'sitelinks': [{'site': enwp_site, 'title': page.title()}]}
				print('http://www.wikidata.org/wiki/'+qid)
				try:
					print(item_dict['labels']['en'])
				except:
					print('')
				print('http://'+prefix+'.wikipedia.org/wiki/' + page.title().replace(' ','_'))
				print('http://commons.wikimedia.org/wiki/'+commonscat.replace(' ','_'))
				text = input("Save? ")
				if text != 'n':
					wd_item.editEntity(data, summary=u'Add '+enwp_site+' sitelink')
					nummodified += 1
			else:
				print('Searching for a match...')
				wikidataEntries = search_entities(repo, page.title())
				print(wikidataEntries)
				data = {'sitelinks': [{'site': enwp_site, 'title': page.title()}]}
				print(wikidataEntries['searchinfo'])
				done = 0
				if wikidataEntries['search'] != []:
					results = wikidataEntries['search']
					# prettyPrint(results)
					numresults = len(results)
					for i in range(0,numresults):
						if done != 0:
							continue
						targetpage = pywikibot.ItemPage(wikidata_site, results[i]['id'])
						item_dict = targetpage.get()
						print('http://www.wikidata.org/wiki/'+results[i]['id'])
						try:
							print(item_dict['labels']['en'])
						except:
							print('')
						print('http://'+prefix+'.wikipedia.org/wiki/' + page.title().replace(' ','_'))
						print('http://commons.wikimedia.org/wiki/'+commonscat.replace(' ','_'))
						text = input("Save? ")
						if text != 'n':
							targetpage.editEntity(data, summary=u'Add enwp sitelink')
							done = 1
							try:
								data2 = {'sitelinks': [{'site': 'commonswiki', 'title': commonscat_item.title()}]}
								text = input('Also add commons link?')
								if text != 'n':
									targetpage.editEntity(data2, summary=u'Add commons sitelink')
							except:
								null = 0

				if done == 0:
					try:
						text = commonscat_item.title()
						print(text)
						print('Create a new item?')
						text = input('Save?')
						if text != 'n':
							# Start assembling the Wikdata entry
							items = []
							if 'Category' in page.title():
								items.append(['P31','Q4167836'])
							test = newitem(commonscat_item, page, items,True)
					except:
						continue


# EOF