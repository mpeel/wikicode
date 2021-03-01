#!/usr/bin/python
# -*- coding: utf-8  -*-
# Create new Wikidata items for enwp articles and categories
# Mike Peel     03-Jan-2021      v1 - start
# Mike Peel		05-Jan-2021		 v2 - expand based on newitem.py
# Mike Peel     14-Jan-2021      v3 - expand biographies
# MIke Peel     30-Jan-2021      v4 - fully automate

import pywikibot
from pywikibot import pagegenerators
from pywikibot.data import api
import datetime
import requests
import csv
from wir_newpages import *
from ftplib import FTP
from ftplogin import *

def parsequarry(quarryfile):
	with open(quarryfile, mode='r') as infile:
		targets = infile.read()
		targets = targets.splitlines()
		targets = targets[1:]
	return targets

def parseduplicity(url,lang='en'):
	try:
		r = requests.get(url)
		websitetext = r.text
	except:
		print('Problem fetching page!')
		return 0
	# print websitetext
	split = websitetext.split("<tr><td nowrap style='text-align:right;font-family:Courier;'>")
	i = 0
	returnlist = []
	for item in split:
		i+=1
		# Skip the top part
		if i > 2:
			# print(item)
			returnlist.append(item.split("<a href='https://"+lang+".wikipedia.org/wiki/")[1].split("' target='_blank'")[0])
			# print 'Title: ' + item.split('</h1>')[0].strip() + '\n'
			# print 'Museum: ' + item.split("strong>Museu:</strong><span itemprop='publisher'>")[1].split("</span>")[0].strip() + "\n"
	return returnlist

wikidata_site = pywikibot.Site("wikidata", "wikidata")
repo = wikidata_site.data_repository()  # this is a DataSite object

wikipedias = ['de','en']
templates_to_skip = ['Q4847311','Q6687153','Q21528265','Q26004972','Q6838010','Q14446424','Q7926719','Q5849910','Q6535522','Q12857463','Q14397354','Q18198962','Q13107809','Q6916118','Q15630429','Q6868608','Q6868546','Q5931187','Q26021926','Q21684530','Q20310993','Q25970270','Q57620750','Q4844001','Q97159332','Q20765099','Q17586361','Q17588240','Q13420881','Q17589095','Q17586294','Q13421187','Q97709865','Q17586502','Q5828850','Q15631954','Q5902043', 'Q14456068','Q105097863','Q105102320','Q105132080','Q5618182','Q11032822']
maxnum = 50000
nummodified = 0
days_since_last_edit = 1.0
days_since_last_edit_but_search = 7.0
days_since_creation = 14.0

debug = False

def search_entities(site, itemtitle,lang='en'):
	 params = { 'action' :'wbsearchentities', 
				'format' : 'json',
				'language' : lang,
				'type' : 'item',
				'search': itemtitle}
	 request = api.Request(site=site, parameters=params)
	 return request.submit()

def get_unconnected(site, offset,number):
	 params = { 'action' :'query', 
				'format' : 'json',
				'list' : 'querypage',
				'qppage' : 'UnconnectedPages',
				'qpoffset' : offset,
				'qplimit': number}
	 request = api.Request(site=site, parameters=params)
	 return request.submit()

for prefix in wikipedias:
	try:
		wikipedia = pywikibot.Site(prefix, 'wikipedia')

		ftp = FTP('mikepeel.net',user=ftpuser,passwd=ftppass)
		ftp.cwd('wiki')
		ftp.retrbinary("RETR "+prefix+"wp_articles.csv" ,open(prefix+'wp_articles.csv', 'wb').write)
		ftp.quit()

		# Set up the list of templates to skip
		# Adapted from https://gerrit.wikimedia.org/g/pywikibot/core/+/HEAD/scripts/newitem.py
		skipping_templates = set()
		for item in templates_to_skip:
			print(item)
			template = wikipedia.page_from_repository(item)
			if template is None:
				continue
			skipping_templates.add(template)
			# also add redirect templates
			skipping_templates.update(template.getReferences(follow_redirects=False, with_template_inclusion=False, filter_redirects=True, namespaces=wikipedia.namespaces.TEMPLATE))
			print(template.title())

		# Start running through unconnected pages
		nametrip = True
		# pages = parsequarry('quarry-51946-enwp-articles-without-wikidata-run526568.csv')
		pages = parsequarry(prefix+"wp_articles.csv")
		
		count = 0
		for pagename in pages:
			pagename = str(pagename[2:-1]).encode('latin1').decode('unicode-escape').encode('latin1').decode('utf-8')
			print(pagename)
			count += 1
			if pagename[0] == '"' and pagename[-1] == '"':
				pagename = pagename[1:-1]
			print(count)
			if not nametrip:
				if 'Crytzer' not in pagename:
					continue
				else:
					nametrip = True
			# if option == 0:
			# 	page = pagename
			# else:
			try:
				page = pywikibot.Page(wikipedia, pagename)
			except:
				continue

			# page = pywikibot.Category(wikipedia, 'Category:Assessed-Class Gaul articles')
			# print("\n" + "http://"+prefix+".wikipedia.org/wiki/"+page.title().replace(' ','_'))

			## Part 1 - quick things to check

			# Articles and categories only
			if page.namespace() != wikipedia.namespaces.MAIN and page.namespace() != wikipedia.namespaces.CATEGORY:
				# print('bad namespace')
				continue
			# Exclude redirects
			if page.isRedirectPage():
				# print('is redirect')
				continue
			if page.isCategoryRedirect():
				# print('is redirect')
				continue
			if 'WikiProject' in page.title():
				print("WikiProject")
				continue
			if 'sockpuppet' in page.title():
				print('sockpuppet')
				continue

			## Part 2 - parse the page info
			print("\n" + "http://"+prefix+".wikipedia.org/wiki/"+page.title().replace(' ','_'))

			# Check if we have a Wikidata item already
			has_sitelink = False
			try:
				wd_item = pywikibot.ItemPage.fromPage(page)
				item_dict = wd_item.get()
				qid = wd_item.title()
				print("Has a sitelink already - " + qid)
				has_sitelink = True
			except:
				print(page.title() + ' - no page found')
			if has_sitelink:
				# If a biography, add biography claims
				if pageIsBiography(page,lang=prefix):
					addBiographyClaims(repo=repo, wikisite=wikipedia, item=wd_item, page=page, lang=prefix)
				try:
					page.touch()
				except:
					continue
				continue

			# Check for the last edit time
			try:
				lastedited = page.editTime()
			except:
				print('Unable to get last edited time')
				continue
			lastedited_time = (datetime.datetime.now() - lastedited).total_seconds()/(60*60*24)
			print('Last edited: ' + str(lastedited_time))
			if lastedited_time < days_since_last_edit:
				print('Recently edited ('+str(lastedited_time)+')')
				continue

			# Check for the creation time
			created = page.oldest_revision.timestamp
			created_time = (datetime.datetime.now() - created).total_seconds()/(60*60*24)
			print('Created: ' + str(created_time))
			if created_time < days_since_creation:
				print('Recently created ('+str(created_time)+')')
				continue

			# Check to see if it contains templates we want to avoid
			trip = 0
			for template, _ in page.templatesWithParams():
				if template in skipping_templates:
					trip = template.title()
			if trip != 0:
				print('Page contains ' + str(trip) + ', skipping')
				continue

			# Check for #REDIRECT
			if '#redirect' in page.text.lower():
				print("Page is a redirect but isn't marked as one")
				continue

			## Part 3 - look up more information

			# If we have a category, make sure it isn't empty
			if page.namespace() == wikipedia.namespaces.CATEGORY:
				if page.isEmptyCategory():
					# print('Is empty')
					continue
				if page.isHiddenCategory():
					# print('Is hidden')
					continue

			# See if search returns any items
			wikidataEntries = search_entities(repo, page.title())
			if wikidataEntries['search'] != []:
				print('Search results but old')
				if lastedited_time < days_since_last_edit_but_search:
					print('Recently edited with search results ('+str(lastedited_time)+')')
					continue

			## Part 4 - editing

			# Remove trailing brackets from the page title
			page_title = page.title()
			if page_title[-1] == ')':
				page_title = page_title[:page_title.rfind('(')]
			page_title = page_title.strip()
			# If we're here, then create a new item
			data = {'labels': {prefix: page_title}, 'sitelinks': [{'site': prefix+'wiki', 'title': page.title()}]}
			test = 'y'
			if debug:
				print(data)
				test = input('Continue?')
			if test == 'y':
				new_item = pywikibot.ItemPage(repo)
				new_item.editEntity(data, summary="Creating item from [[" + prefix +":"+page.title()+"]]")
				nummodified += 1
				if page.namespace() == wikipedia.namespaces.CATEGORY:
					# We have a category, also add a P31 value
					claim = pywikibot.Claim(repo,'P31')
					if page.isDisambig():
						claim.setTarget(pywikibot.ItemPage(repo, 'Q15407973')) # Wikimedia disambiguation category
					else:
						claim.setTarget(pywikibot.ItemPage(repo, 'Q4167836')) # Wikimedia category
					new_item.addClaim(claim, summary='Category item')
				else:
					if page.isDisambig():
						claim = pywikibot.Claim(repo,'P31')
						claim.setTarget(pywikibot.ItemPage(repo, 'Q4167410')) # Disambiguation page
						new_item.addClaim(claim, summary='Disambig page')
					elif 'list of' in page.title()[0:10].lower():
						# input('Is list - OK?')
						claim = pywikibot.Claim(repo,'P31')
						claim.setTarget(pywikibot.ItemPage(repo, 'Q13406463')) # List item
						new_item.addClaim(claim, summary='List item')
					elif pageIsBiography(page,lang=prefix):
						# If a biography, add biography claims
						addBiographyClaims(repo=repo, wikisite=wikipedia, item=new_item, page=page, lang=prefix)
					elif 'film)' in page.title().lower():
						# input('Is film - OK?')
						claim = pywikibot.Claim(repo,'P31')
						claim.setTarget(pywikibot.ItemPage(repo, 'Q11424')) # Film
						new_item.addClaim(claim, summary='Film')
					elif 'tv series)' in page.title().lower():
						# input('Is TV series - OK?')
						claim = pywikibot.Claim(repo,'P31')
						claim.setTarget(pywikibot.ItemPage(repo, 'Q5398426')) # Film
						new_item.addClaim(claim, summary='TV series')
					elif 'surname)' in page.title().lower():
						# input('Is surname - OK?')
						claim = pywikibot.Claim(repo,'P31')
						claim.setTarget(pywikibot.ItemPage(repo, 'Q101352')) # Surname
						new_item.addClaim(claim, summary='Surname')




			## Part 5 - tidy up

			# Touch the page to force an update
			try:
				page.touch()
			except:
				null = 0

			# Cut-off at a maximum number of edits	
			print("")
			print(nummodified)
			if nummodified >= maxnum:
				print('Reached the maximum of ' + str(maxnum) + ' entries modified, quitting!')
				exit()
	except:
		continue
# EOF