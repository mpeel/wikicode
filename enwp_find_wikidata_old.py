#!/usr/bin/python
# -*- coding: utf-8  -*-
# Add enwp sitelinks based on commons categories
# Mike Peel     11-Jun-2020      v1 - start

from __future__ import unicode_literals

import pywikibot
import numpy as np
import time
import string
from pywikibot import pagegenerators
from pywikibot.data import api
import urllib
from pibot_functions import *
# from database_login import *
from wir_newpages import *
import os

wikidata_site = pywikibot.Site("wikidata", "wikidata")
repo = wikidata_site.data_repository()  # this is a DataSite object
commons = pywikibot.Site('commons', 'commons')
enwp = pywikibot.Site('en', 'wikipedia')
enwp_site = 'enwiki'
prefix = 'en'
# enwp = pywikibot.Site('simple', 'wikipedia')
# enwp_site = 'simplewiki'
# prefix = 'simple'
# enwp = pywikibot.Site('pt', 'wikipedia')
# enwp_site = 'ptwiki'
# prefix = 'pt'
# enwp = pywikibot.Site('de', 'wikipedia')
# enwp_site = 'dewiki'
# prefix = 'de'

doing_cats = False


templates_to_skip = ['Q4847311','Q6687153','Q21528265','Q26004972','Q6838010','Q14446424','Q7926719','Q5849910','Q6535522','Q12857463','Q14397354','Q18198962','Q13107809','Q6916118','Q15630429','Q6868608','Q6868546','Q5931187','Q26021926','Q21684530','Q20310993','Q25970270','Q57620750','Q4844001','Q97159332','Q20765099','Q17586361','Q17588240','Q13420881','Q17589095','Q17586294','Q13421187','Q97709865','Q17586502','Q5828850','Q15631954','Q5902043', 'Q14456068','Q105097863','Q11032822']

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
		candidate_item.editEntity(data, summary=u'Added [['+prefix+':'+enwp.title()+']]')


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

def parsequarry(quarryfile):
	with open(quarryfile, mode='r') as infile:
		targets = infile.read()
		targets = targets.splitlines()
		targets = targets[1:]
	return targets

def parseredirects(quarryfile):
	with open(quarryfile, mode='r') as infile:
		targets = infile.read()
		targets = targets.splitlines()
	return targets

def search_entities(site, itemtitle,lang='en'):
	 params = { 'action' :'wbsearchentities',
				'format' : 'json',
				'language' : lang,
				'type' : 'item',
				'search': itemtitle}
	 request = api.Request(site=site, parameters=params)
	 return request.submit()


maxnum = 100000
nummodified = 0

debug = 1
trip = 1
newitems = 0

targetcats = ['Category:Articles_without_Wikidata_item']
# Also see https://www.wikidata.org/wiki/Wikidata:Metrics
# targetcats = ['Category:Short description with empty Wikidata description']
lang = 'en'

skipping_templates = set()
for item in templates_to_skip:
	print(item)
	template = enwp.page_from_repository(item)
	if template is None:
		continue
	skipping_templates.add(template)
	# also add redirect templates
	skipping_templates.update(template.getReferences(follow_redirects=False, with_template_inclusion=False, filter_redirects=True, namespaces=enwp.namespaces.TEMPLATE))
	print(template.title())

# for categories in range(0,2):
for targetcat in targetcats:
	cat = pywikibot.Category(enwp, targetcat)
	# pages = pagegenerators.CategorizedPageGenerator(cat, recurse=False);
	# pages = enwp.querypage('UnconnectedPages')
	# for page in pages:
	# pages = parsequarry('quarry-51950-enwp-categories-without-wikidata-run526620.csv')
	if doing_cats:
		# redirects = parseredirects(prefix+'wp_category_redirects.csv')
		redirects = []
		pages = parsequarry(prefix+'wp_categories.csv')
	else:
		pages = parsequarry(prefix+'wp_articles.csv')
	pages.sort()
	for pagename in pages:
		pagename = str(pagename[2:-1]).encode('latin1').decode('unicode-escape').encode('latin1').decode('utf-8')
		if pagename[0] == '"' and pagename[-1] == '"':
			pagename = pagename[1:-1]
		if doing_cats:
			if prefix == 'pt':
				pagename = 'Categoria:'+pagename
				if 'Categoria:!' in pagename:
					continue
			elif prefix == 'de':
				pagename = 'Kategorie:'+pagename
			else:
				pagename = 'Category:'+pagename
			if pagename.replace('_',' ').strip() in redirects:
				print(pagename)
				print('Redirected')
				continue
			try:
				page = pywikibot.Category(enwp, pagename)
			except:
				continue
		else:
			try:
				page = pywikibot.Page(enwp, pagename)
			except:
				continue

		try:
			text = page.get()
		except:
			continue
		if 'REDIRECT' in text:
			continue
		if 'redirect' in text:
			continue
		# Optional skip-ahead to resume broken runs
		if trip == 0:
			if "Categoria:Azteca" in page.title():
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

		print("\n" + "http://"+prefix+".wikipedia.org/wiki/"+page.title().replace(' ','_'))
		if 'Articles for deletion' in page.title():
			continue
		if page.isRedirectPage():
			continue
		temp_trip = 0
		for template, _ in page.templatesWithParams():
			if template in skipping_templates:
				temp_trip = template.title()
		if temp_trip != 0:
			print('Page contains ' + str(temp_trip) + ', skipping')
			continue

		# if not pageIsBiography(page=page, lang=lang):
		# 	print('Page is not a biography')

		# if authorIsNewbie(page=page, lang=lang):
		# 	print("Newbie author, checking quality...")
		# 	if pageIsRubbish(page=page, lang=lang) or \
		# 	   (not pageCategories(page=page, lang=lang)) or \
		# 	   (not pageReferences(page=page, lang=lang)) or \
		# 	   (not len(list(page.getReferences(namespaces=[0])))):
		# 		print("Page didnt pass minimum quality")

		# pagebirthyear = calculateBirthDate(page=page, lang=lang)
		# pagebirthyear = pagebirthyear and int(pagebirthyear.split('-')[0]) or ''
		# if not pagebirthyear:
		# 	print("Page doesnt have birthdate")

		# See if we have a Wikidata item already
		try:
			wd_item = pywikibot.ItemPage.fromPage(page)
			item_dict = wd_item.get()
			qid = wd_item.title()
			print("Has a sitelink already - " + qid)
			continue
		except:
			# If that didn't work, go no further
			print(page.title() + ' - no item found')
			wd_item = 0
			item_dict = 0
			qid = 0
			sitelink_check = 0
			# continue

		# If we're here, then we don't have one, see if we can add it through the commons category
		try:
			searchtag = page.title()
			try:
				searchtag = searchtag.split('(')[0].strip()
			except:
				null = 0
			wikidataEntries = search_entities(repo, searchtag,lang=prefix)
			# print(wikidataEntries)
			data = {'sitelinks': [{'site': enwp_site, 'title': page.title()}]}
			# print(wikidataEntries['searchinfo'])
			done = 0
			if wikidataEntries['search'] != []:
				results = wikidataEntries['search']
				# prettyPrint(results)
				numresults = len(results)
				if numresults > 5:
					print('More than 5 candidates, bot would skip')
				for i in range(0,numresults):
					if done != 0:
						continue
					targetpage = pywikibot.ItemPage(wikidata_site, results[i]['id'])
					try:
						item_dict = targetpage.get()
					except:
						continue
					# print(item_dict)
					sitelink = ''
					try:
						sitelink = get_sitelink_title(item_dict['sitelinks'][enwp_site])
					except:
						null = 0
					if sitelink == '':
						print('http://www.wikidata.org/wiki/'+results[i]['id'])
						if prefix != 'en':
							try:
								print(item_dict['labels']['en'])
							except:
								print('')
							try:
								print(item_dict['descriptions']['en'])
							except:
								print('')

						try:
							print(item_dict['labels'][prefix])
						except:
							print('')
						try:
							print(item_dict['descriptions'][prefix])
						except:
							print('')
						print('http://'+prefix+'.wikipedia.org/wiki/' + page.title().replace(' ','_'))
						text = input("Save? ")
						if text != 'n':
							targetpage.editEntity(data, summary=u'Added [['+prefix+':'+page.title()+']]')
							done = 1

			if prefix != 'en' and prefix != 'simple' and not done and ':' in pagename:
				# Also try translating and doing a search in English
				# command = 'trans '+prefix+': -brief "'+pagename.replace('"',"'").replace("_"," ")+'" -engine bing'
				# print(command)
				# stream = os.popen(command)
				# output = stream.read().strip()
				# output = output.replace(': ', ':')
				# print(output)
				output = pagename.replace('Kategorie:','Category:')
				output = pagename.replace('Categoria:','Category:')
				wikidataEntries = search_entities(repo, output,lang='en')
				# print(wikidataEntries)
				data = {'sitelinks': [{'site': enwp_site, 'title': page.title()}]}
				# print(wikidataEntries['searchinfo'])
				done = 0
				if wikidataEntries['search'] != []:
					results = wikidataEntries['search']
					# prettyPrint(results)
					numresults = len(results)
					if numresults > 5:
						print('More than 5 candidates, bot would skip')
					for i in range(0,numresults):
						if done != 0:
							continue
						targetpage = pywikibot.ItemPage(wikidata_site, results[i]['id'])
						try:
							item_dict = targetpage.get()
						except:
							continue
						# print(item_dict)
						sitelink = ''
						try:
							sitelink = get_sitelink_title(item_dict['sitelinks'][enwp_site])
						except:
							null = 0
						if sitelink == '':
							print('http://www.wikidata.org/wiki/'+results[i]['id'])
							if prefix != 'en':
								try:
									print(item_dict['labels']['en'])
								except:
									print('')
								try:
									print(item_dict['descriptions']['en'])
								except:
									print('')
							try:
								print(item_dict['labels'][prefix])
							except:
								print('')
							try:
								print(item_dict['descriptions'][prefix])
							except:
								print('')
							print('http://'+prefix+'.wikipedia.org/wiki/' + page.title().replace(' ','_'))
							text = input("Save? ")
							if text != 'n':
								targetpage.editEntity(data, summary=u'Added [['+prefix+':'+page.title()+']]')
								done = 1
		except:
			continue

		if done == 0 and newitems == 1:
			text = input('Create a new item?')
			if text != 'n':
				# Start assembling the Wikdata entry
				items = []
				new_item = pywikibot.ItemPage(repo)
				new_item.editLabels(labels={"en":page.title()}, summary="Creating item")
				itemfound = pywikibot.ItemPage(repo, new_item.getID())
				data = {'sitelinks': [{'site': enwp_site, 'title': page.title()}]}
				itemfound.editEntity(data, summary=u'Added [['+prefix+':'+page.title()+']]')
				text = input('Is it a bio?')
				if text != 'n':
					addBiographyClaims(repo=repo, wikisite=enwp, item=itemfound, page=page, lang=lang)


# EOF
