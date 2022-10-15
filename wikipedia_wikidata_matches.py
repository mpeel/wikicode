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

for arg in args:
	t=arg.split('=')
	if len(t)>1: k,v=arg.split('='); GET[k]=v

wikidata_site = pywikibot.Site("wikidata", "wikidata")
repo = wikidata_site.data_repository()  # this is a DataSite object
enwiki = pywikibot.Site('en', 'wikipedia')
simplewiki = pywikibot.Site('simple', 'wikipedia')
ptwiki = pywikibot.Site('pt', 'wikipedia')
dewiki = pywikibot.Site('de', 'wikipedia')
eswiki = pywikibot.Site('es', 'wikipedia')
frwiki = pywikibot.Site('fr', 'wikipedia')
itwiki = pywikibot.Site('it', 'wikipedia')
nlwiki = pywikibot.Site('nl', 'wikipedia')
plwiki = pywikibot.Site('pl', 'wikipedia')
svwiki = pywikibot.Site('sv', 'wikipedia')
eowiki = pywikibot.Site('eo', 'wikipedia')

mydb = mysql.connector.connect(
  host=database_host,
  user=database_user,
  passwd=database_password,
  database=database_database
)
mycursor = mydb.cursor()
action = GET.get('action')
callback = GET.get('callback')
if not callback:
	callback = ''
num = GET.get('num')
if not num:
	num = 1
if int(num) > 5:
	num = 5
lang = GET.get('lang')
if action == 'desc':
	# print 'desc'
	print "Content-type: application/json\n\n"
	print callback + " ( " + json.dumps({'label': {'en':'New Wikipedia article and category matches'}, 'description': {'en':'Match new Wikipedia articles and categories with Wikidata items, and add the sitelink to Wikidata.'}, 'instructions': {'en':'Pi bot is thinking about creating new items for these articles, but first it wants your help to match them to existing items.<br />If the match is right, please add the link to Wikidata using "Match". If it is clearly wrong, select "No". If you are not sure, press "Skip".<br />Bug reports and feedback should be sent to User:Mike_Peel.'}, 'icon': 'https://upload.wikimedia.org/wikipedia/en/thumb/8/80/Wikipedia-logo-v2.svg/120px-Wikipedia-logo-v2.svg.png', 'options': [{'name':'Entry type', 'key':'type', 'values': {'all':'Any', 'en':'English', 'simple':'Simple','pt':'Português','de':'Deutsch','es':'Español','fr':'Français','it':'Italiano','nl':'Nederlands','pl':'Polski','sv':'Svenska','eo':'Esperanto'}}]}) + " )\n"

elif action == 'tiles':
	print "Content-type: application/json\n\n"
	i = 0
	finished = 0
	tiles = []

	itemtype = 'Any'
	try:
		itemtype = GET.get('type')
	except:
		itemtype = 'Any'
	torun = 'any'
	if itemtype != 'Any':
		if itemtype == 'en':
			torun = 'en'
		elif itemtype == 'simple':
			torun = 'simple'
		elif itemtype == 'de':
			torun = 'de'
		elif itemtype == 'pt':
			torun = 'pt'
		elif itemtype == 'es':
			torun = 'es'
		elif itemtype == 'fr':
			torun = 'fr'
		elif itemtype == 'it':
			torun = 'it'
		elif itemtype == 'nl':
			torun = 'nl'
		elif itemtype == 'pl':
			torun = 'pl'
		elif itemtype == 'sv':
			torun = 'sv'
		elif itemtype == 'eo':
			torun = 'eo'
	while finished == 0:
		if torun == 'any':
			sql = 'SELECT * FROM newarticles WHERE done = 0 ORDER BY RAND() LIMIT 1'
		else:
			sql = 'SELECT * FROM newarticles WHERE done = 0 AND site = "'+torun+'" ORDER BY RAND() LIMIT 1'
		mycursor.execute(sql)
		myresult = mycursor.fetchone()
		if myresult[3] == 'en':
			site = enwiki
		elif myresult[3] == 'simple':
			site = simplewiki
		elif myresult[3] == 'de':
			site = dewiki
		elif myresult[3] == 'pt':
			site = ptwiki
		elif myresult[3] == 'es':
			site = eswiki
		elif myresult[3] == 'fr':
			site = frwiki
		elif myresult[3] == 'it':
			site = itwiki
		elif myresult[3] == 'nl':
			site = nlwiki
		elif myresult[3] == 'pl':
			site = plwiki
		elif myresult[3] == 'sv':
			site = svwiki
		elif myresult[3] == 'eo':
			site = eowiki
		else:
			continue
		# Make sure it doesn't have an ID yet
		badtile = 0
		try:
			target = pywikibot.Page(site,myresult[2])
		except:
			badtile = 1
		if badtile == 1:
			sql = 'UPDATE newarticles SET done = 1, user = "NA", decision = 1 WHERE cid = "'+str(myresult[0])+'" AND done = 0'
			mycursor.execute(sql)
			mydb.commit()
			continue
		badtile = 0
		try:
			wd_item = pywikibot.ItemPage.fromPage(target)
			item_dict = wd_item.get()
			badtile = 1
		except:
			badtile = 0
		if badtile == 1:
			sql = 'UPDATE newarticles SET done = 1, user = "NA", decision = 1 WHERE cid = "'+str(myresult[0])+'" AND done = 0'
			mycursor.execute(sql)
			mydb.commit()
			continue
		badtile = 0
		try:
			pagetext = target.get()
		except:
			badtile = 1
		if badtile == 1:
			sql = 'UPDATE newarticles SET done = 1, user = "NA", decision = 1 WHERE cid = "'+str(myresult[0])+'" AND done = 0'
			mycursor.execute(sql)
			mydb.commit()
			# exit()
			continue
		badtile = 0
		try:
			candidate_item = pywikibot.ItemPage(repo, myresult[1])
			candidate_item_dict = candidate_item.get()
		except:
			badtile = 1
		if badtile == 1:
			sql = 'UPDATE newarticles SET done = 1, user = "NA", decision = 1 WHERE cid = "'+str(myresult[0])+'" AND done = 0'
			mycursor.execute(sql)
			mydb.commit()
			# exit()
			continue

		skip = 0
		try:
			sitelink = candidate_item_dict['sitelinks'][myresult[3]+'wiki']
		except:
			#{"type": "files","files": files, "q":myresult[1],'deferred_decision':'yes'}
			tile = {"id": myresult[0], "sections": [ {"type": "item", "q":myresult[1]}, {"type": "wikipage","title": myresult[2],"wiki": myresult[3]+"wiki"}], "controls": [{"type":"buttons", "entries":[{"type": "green","decision": "yes","label": "Match", "api_action": {'action': "wbsetsitelink", "id": myresult[1],"linksite": myresult[3]+"wiki","linktitle": myresult[2]}}, {"type": "white", "decision": "skip", "label": "Skip"}, {"type": "blue", "decision": "no", "label": "No"}]}]}
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
		sql = 'UPDATE newarticles SET done = 1, user = "'+user+'", decision = 2 WHERE cid = "' + tile + '"'
		# print sql
		mycursor.execute(sql)
		mydb.commit()
		print "no"
	elif decision == "yes":
		sql = 'SELECT * FROM newarticles WHERE cid = "' + tile + '" LIMIT 1'
		# print sql
		mycursor.execute(sql)
		myresult = mycursor.fetchone()
		print myresult
		sql = 'UPDATE newarticles SET done = 1, user = "'+user+'", decision = 1 WHERE qid = "'+myresult[1]+'" AND done = 0'
		mycursor.execute(sql)
		mydb.commit()
		sql = 'UPDATE newarticles SET done = 1, user = "'+user+'", decision = 1 WHERE candidate = "'+myresult[2]+'" AND site = "'+myresult[3]+'" AND done = 0'
		mycursor.execute(sql)
		mydb.commit()
		sql = 'UPDATE newarticles SET done = 1, user = "'+user+'", decision = 3 WHERE cid = "' + tile + '"'
		mycursor.execute(sql)
		mydb.commit()
		print "yes"
else:
	print "Content-type: text/html\n\n"
	print 'Incorrect action!'
	print args

# mycursor.close()
# mydb.close()
