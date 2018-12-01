#!/usr/bin/python
# -*- coding: utf-8  -*-
# Create new Wikidata items
# Started 25 August 2018 by Mike Peel
# 3 November 2018 - focus on people for now
from __future__ import unicode_literals

import pywikibot
import numpy as np
import time
import string
from pywikibot import pagegenerators
from pywikibot.data import api
import urllib
import mysql.connector
from database_login import *

commons = pywikibot.Site('commons', 'commons')
repo = commons.data_repository()  # this is a DataSite object

statedin = pywikibot.Claim(repo, u'P143')
itis = pywikibot.ItemPage(repo, "Q565")
statedin.setTarget(itis)
retrieved = pywikibot.Claim(repo, u'P813')
date = pywikibot.WbTime(year=2018, month=12, day=1)
retrieved.setTarget(date)

maxnum = 10

mydb = mysql.connector.connect(
  host=database_host,
  user=database_user,
  passwd=database_password,
  database=database_database
)
mycursor = mydb.cursor()

def search_entities(site, itemtitle):
	 params = { 'action' :'wbsearchentities', 
				'format' : 'json',
				'language' : 'en',
				'type' : 'item',
				'search': itemtitle}
	 request = api.Request(site=site, parameters=params)
	 return request.submit()

def newitem(category, items):
	new_item = pywikibot.ItemPage(repo)
	new_item.editLabels(labels={"en":category.title().replace('Category:','')}, summary="Creating item")
	candidate_item = pywikibot.ItemPage(repo, new_item.getID())
	print candidate_item

	data = {'sitelinks': [{'site': 'commonswiki', 'title': category.title()}]}
	candidate_item.editEntity(data, summary=u'Add commons sitelink')

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
			print "That didn't work"
	return

category = 'Category:People by name'
cat = pywikibot.Category(commons,category)
i = 0
trip = 0
for targetcat in pagegenerators.SubCategoriesPageGenerator(cat, recurse=False):
	if trip == 0:
		if targetcat.title() == 'Category:Even Aas':
			trip = 1
		else:
			continue
	else:
		trip = 1

	try:
		wd_item = pywikibot.ItemPage.fromPage(targetcat)
		item_dict = wd_item.get()
		print wd_item.title()
		continue
	except:
		print targetcat.title()

	# Check the database to see if there are open matches
	mycursor.execute('SELECT * FROM candidates WHERE category = "' + targetcat.title() + '"')
	myresult = mycursor.fetchall()
	qidlist = []
	abort = 0
	for result in myresult:
		print myresult
		if result[3] == 0:
			abort = 1
		qidlist.append(result[1])
	if abort == 1:
		continue

	# Also search for other matches
	searchname = targetcat.title().replace('Category:','')
	searchname2 = searchname.split('(', 1)[0]
	if searchname2 != '':
		searchname = searchname2
	wikidataEntries = search_entities(repo, searchname)
	print wikidataEntries
	abort = 0
	if wikidataEntries['search'] != []:
		results = wikidataEntries['search']
		# prettyPrint(results)
		numresults = len(results)
		for i in range(0,numresults):
			if results[i]['id'] not in qidlist:
				abort = 1
	if abort == 1:
		continue

	# Start assembling the Wikdata entry
	target_text = targetcat.get()
	items = [['P31','Q5']]
	if "Men by name" in target_text:
		items.append(['P21','Q6581097'])
	elif "Women by name" in target_text:
		items.append(['P21','Q6581072'])
	elif "female" in target_text:
		items.append(['P21','Q6581072'])
	elif "male" in target_text:
		items.append(['P21','Q6581097'])
	if " births]]" in target_text:
		test = target_text.split(" births]]")[0]
		test = test.split('[[Category:')[-1]
		print test
		items.append(['P569',pywikibot.WbTime(site=repo, year=test, month=01, day=01,
precision='year')])
	if " deaths]]" in target_text:
		test = target_text.split(" deaths]]")[0]
		test = test.split('[[Category:')[-1]
		print test
		items.append(['P570',pywikibot.WbTime(site=repo, year=test, month=01, day=01,
precision='year')])
	print items
	test = newitem(targetcat, items)
	i += 1
	if i > maxnum:
		exit()



