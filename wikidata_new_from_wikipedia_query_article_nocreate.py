#!/usr/bin/python
# -*- coding: utf-8  -*-
# Create new Wikidata items for enwp articles and categories
# Mike Peel     03-Jan-2021      v1 - start
# Mike Peel		05-Jan-2021		 v2 - expand based on newitem.py
# Mike Peel     14-Jan-2021      v3 - expand biographies
# MIke Peel     30-Jan-2021      v4 - fully automate
# Mike Peel		15-Oct-2022		 Version that only populates the database, not creating items

import pywikibot
from pywikibot import pagegenerators
from pywikibot.data import api
import datetime
import requests
import csv
from wir_newpages import *
from ftplib import FTP
from ftplogin import *
from database_login import *
import mysql.connector
from pibot_functions import *

mydb = mysql.connector.connect(
  host=database_host,
  user=database_user,
  passwd=database_password,
  database=database_database
)
mycursor = mydb.cursor()

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

wikipedias = ['ml','af','cy','et','dag','es','fr','it','nl','pl','sv','eo']
templates_to_skip = ['Q4847311','Q6687153','Q21528265','Q26004972','Q6838010','Q14446424','Q7926719','Q5849910','Q6535522','Q12857463','Q14397354','Q18198962','Q13107809','Q6916118','Q15630429','Q6868608','Q6868546','Q5931187','Q26021926','Q21684530','Q20310993','Q25970270','Q57620750','Q4844001','Q97159332','Q17586305','Q17586361','Q17588240','Q13420881','Q17589095','Q17586294','Q13421187','Q97709865','Q17586502','Q5828850','Q15631954','Q5902043', 'Q14456068','Q105097863','Q105102320','Q105132080','Q5618182','Q11032822','Q26142338']
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
			try:
				template = wikipedia.page_from_repository(item)
			except:
				continue
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
			old_page = False
			created = page.oldest_revision.timestamp
			created_time = (datetime.datetime.now() - created).total_seconds()/(60*60*24)
			print('Created: ' + str(created_time))
			if created_time < days_since_creation:
				print('Recently created ('+str(created_time)+')')
				# Continue moved to after search
			elif created_time > 90:
				old_page = True



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
			wikidataEntries = search_entities(repo, page.title(),lang=prefix)
			if wikidataEntries['search'] != []:
				print('Search results but old')
				results = wikidataEntries['search']
				numresults = len(results)
				for i in range(0,numresults):
					qid = results[i]['id']
					print(qid)
					try:
						candidate_item = pywikibot.ItemPage(repo, qid)
						candidate_item_dict = candidate_item.get()
					except:
						print('Huh - no page found')
					skip = 0
					incat = 0
					try:
						sitelink = get_sitelink_title(candidate_item_dict['sitelinks'][prefix+'wiki'])
					except:
						print('Hello')
						try:
							# No existing sitelink found, add it to the database as a possibility
							mycursor.execute('SELECT * FROM newarticles WHERE qid="'+qid+'" AND candidate = "' + page.title() + '" AND site = "'+prefix+'"')
							myresult = mycursor.fetchone()
							print(myresult)
							if not myresult:
								sql = "INSERT INTO newarticles (qid, candidate, site) VALUES (%s, %s, %s)"
								val = (qid, page.title(),prefix)
								mycursor.execute(sql, val)
								mydb.commit()
						except:
							print('Something went wrong when adding it to the database!')
				if lastedited_time < days_since_last_edit_but_search:
					print('Recently edited with search results ('+str(lastedited_time)+')')
					continue
			if prefix != 'en':
				wikidataEntries = search_entities(repo, page.title(),lang='en')
				if wikidataEntries['search'] != []:
					print('Search results but old')
					results = wikidataEntries['search']
					numresults = len(results)
					for i in range(0,numresults):
						qid = results[i]['id']
						print(qid)
						try:
							candidate_item = pywikibot.ItemPage(repo, qid)
							candidate_item_dict = candidate_item.get()
						except:
							print('Huh - no page found')
						skip = 0
						incat = 0
						try:
							sitelink = get_sitelink_title(candidate_item_dict['sitelinks'][prefix+'wiki'])
						except:
							print('Hello')
							try:
								# # No existing sitelink found, add it to the database as a possibility
								mycursor.execute('SELECT * FROM newarticles WHERE qid="'+qid+'" AND candidate = "' + page.title() + '" AND site = "'+prefix+'"')
								myresult = mycursor.fetchone()
								print(myresult)
								if not myresult:
									sql = "INSERT INTO newarticles (qid, candidate, site) VALUES (%s, %s, %s)"
									val = (qid, page.title(),prefix)
									mycursor.execute(sql, val)
									mydb.commit()
							except:
								print('Something went wrong when adding it to the database!')
					if lastedited_time < days_since_last_edit_but_search:
						print('Recently edited with search results ('+str(lastedited_time)+')')
						continue

		# ... and we're done.
	except:
		continue
# EOF
