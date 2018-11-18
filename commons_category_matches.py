#!/usr/bin/python
# -*- coding: utf-8  -*-
# import pip
import os
import json
# pip.main(['list'])
import pywikibot
import mysql.connector
from pywikibot import pagegenerators
from database_login import *

GET={}
args=os.getenv("QUERY_STRING").split('&')
# print args

for arg in args: 
	t=arg.split('=')
	if len(t)>1: k,v=arg.split('='); GET[k]=v

wikidata_site = pywikibot.Site("wikidata", "wikidata")
repo = wikidata_site.data_repository()  # this is a DataSite object
commons = pywikibot.Site('commons', 'commons')

mydb = mysql.connector.connect(
  host=database_host,
  user=database_user,
  passwd=database_password,
  database=database_database
)
mycursor = mydb.cursor()

# print 'hello'
action = GET.get('action')
callback = GET.get('callback')
if not callback:
	callback = ''
num = GET.get('num')
if not num:
	num = 1
if int(num) > 100:
	num = 100
lang = GET.get('lang')
if action == 'desc':
	# print 'desc'
	print "Content-type: application/json\n\n"
	print callback + " ( " + json.dumps({'label': {'en':'Commons category matches'}, 'description': {'en':'Match Commons categories with Wikidata items, and add the commons sitelink to Wikidata.'}, 'instructions': {'en':'These matches look plausible. But are they really? Please help us to reject the bad ones by clicking "No" - and if you are sure that it is right, add the link to Wikidata using "Match". If you are not sure, press "Skip".<br />Bug reports and feedback should be sent to commons:User:Mike Peel.'}, 'icon': 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/4a/Commons-logo.svg/120px-Commons-logo.svg.png'}) + " )\n"
elif action == 'tiles':
	print "Content-type: application/json\n\n"
	i = 0
	finished = 0
	tiles = []
	while finished == 0:
		mycursor.execute('SELECT * FROM candidates WHERE done = 0 ORDER BY RAND() LIMIT 1')#%d' % (int(num),))
		myresult = mycursor.fetchone()
		# Make sure the category doesn't have an ID yet
		targetcat = pywikibot.Category(commons,myresult[2])
		badtile = 0
		try:
			wd_item = pywikibot.ItemPage.fromPage(targetcat)
			item_dict = wd_item.get()
			badtile = 1
		except:
			badtile = 0
		if badtile == 1:
			sql = 'UPDATE candidates SET done = 1, user = "NA", decision = 1 WHERE cid = "'+str(myresult[0])+'" AND done = 0'
			mycursor.execute(sql)
			mydb.commit()
			# exit()
			continue

		cattext = targetcat.get()
		split = cattext.split('[[')
		categorystring = ""
		for testitem in split:
			if 'Category' in testitem:
				if categorystring == "":
					categorystring = testitem.replace(']]','')
				else:
					categorystring = categorystring + " - " + testitem.replace(']]','')
			if 'category' in testitem:
				if categorystring == "":
					categorystring = testitem.replace(']]','')
				else:
					categorystring = categorystring + " - " + testitem.replace(']]','')
		categorystring = categorystring.replace('\n',' ')
		# gen = pagegenerators.CategorizedPageGenerator(targetcat)
		# files = []
		# k = 0
		# for page in gen:
		# 	if 'File' in page.title():
		# 		files.append(page.title().replace('File:',''))
		# 		k += 1
		# 	if k > 5:
		# 		break
		# print "Content-type: text/html\n\n"
		# print files
		candidate_item = pywikibot.ItemPage(repo, myresult[1])
		candidate_item_dict = candidate_item.get()
		skip = 0
		try:
			p31 = candidate_item_dict['claims']['P31']
			for clm in p31:
				#print clm
				if 'Q4167410' in clm.getTarget().title():
					# print 'would skip'
					skip = 1
		except:
			null = 0
		if skip == 1:
			# print 'skipping'
			continue
		try:
			sitelink = candidate_item_dict['sitelinks']['commonswiki']
		except:
			#{"type": "files","files": files, "q":myresult[1],'deferred_decision':'yes'}
			tile = {"id": myresult[0], "sections": [ {"type": "item", "q":myresult[1]}, {"type": "wikipage","title": myresult[2],"wiki": "commonswiki"}, {"type": "text","title": "Categories that this category is in:", "text":categorystring}], "controls": [{"type":"buttons", "entries":[{"type": "green","decision": "yes","label": "Match", "api_action": {'action': "wbsetsitelink", "id": myresult[1],"linksite": "commonswiki","linktitle": myresult[2]}}, {"type": "white", "decision": "skip", "label": "Skip"}, {"type": "blue", "decision": "no", "label": "No"}]}]}
			tiles.append(tile)
			i += 1
			if i >= int(num):
				finished = 1
	# print json.dumps({"tiles":tiles})
	print callback + " ( " + json.dumps(tiles) + ")\n"
elif action == 'log_action':
	print "Content-type: text/html\n\n"
	user = GET.get('user')
	tile = GET.get('tile')
	decision = GET.get('decision')
	print decision
	# decision = 0 not set, 1 irrelevant, 2 no, 3 yes
	if decision == "no":
		print int(tile)
		print user
		print decision
		sql = 'UPDATE candidates SET done = 1, user = "'+user+'", decision = 2 WHERE cid = "' + tile + '"'
		# print sql
		mycursor.execute(sql)
		mydb.commit()
		print "no"
	elif decision == "yes":
		sql = 'SELECT * FROM candidates WHERE cid = "' + tile + '" LIMIT 1'
		# print sql
		mycursor.execute(sql)
		myresult = mycursor.fetchone()
		print myresult
		sql = 'UPDATE candidates SET done = 1, user = "'+user+'", decision = 1 WHERE qid = "'+myresult[1]+'" AND done = 0'
		mycursor.execute(sql)
		mydb.commit()
		sql = 'UPDATE candidates SET done = 1, user = "'+user+'", decision = 1 WHERE category = "'+myresult[2]+'" AND done = 0'
		mycursor.execute(sql)
		mydb.commit()
		sql = 'UPDATE candidates SET done = 1, user = "'+user+'", decision = 3 WHERE cid = "' + tile + '"'
		mycursor.execute(sql)
		mydb.commit()
		print "yes"
else:
	print "Content-type: text/html\n\n"
	print 'Incorrect action!'
	print args
	
# mycursor.close()
# mydb.close()