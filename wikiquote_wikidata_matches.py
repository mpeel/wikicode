#!/usr/bin/python3
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
enwiki = pywikibot.Site('en', 'wikiquote')
ptwiki = pywikibot.Site('pt', 'wikiquote')
dewiki = pywikibot.Site('de', 'wikiquote')
eswiki = pywikibot.Site('es', 'wikiquote')
frwiki = pywikibot.Site('fr', 'wikiquote')

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
	num = 5
if int(num) > 5:
	num = 5
lang = GET.get('lang')
if action == 'desc':
	print("Content-type: application/json\n\n")
	print(callback + " ( " + json.dumps({'label': {'en':'New Wikiquote article and category matches'}, 'description': {'en':'Match new Wikiquote pages with Wikidata items, and add the sitelink to Wikidata.'}, 'instructions': {'en':'Pi bot is thinking about creating new items for these pages, but first it wants your help to match them to existing items.<br />If the match is right, please add the link to Wikidata using "Match". If it is clearly wrong, select "No". If you are not sure, press "Skip".<br />Bug reports and feedback should be sent to User:Mike_Peel.'}, 'icon': 'https://upload.wikimedia.org/wikipedia/commons/thumb/f/fa/Wikiquote-logo.svg/80px-Wikiquote-logo.svg.png', 'options': [{'name':'Entry type', 'key':'type', 'values': {'all':'Any', 'en':'English', 'pt':'Português','de':'Deutsch','es':'Español','fr':'Français','it':'Italiano'}}]}) + " )\n")

elif action == 'tiles':
	print("Content-type: application/json\n\n")
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
		# elif itemtype == 'nl':
		# 	torun = 'nl'
		# elif itemtype == 'pl':
		# 	torun = 'pl'
		# elif itemtype == 'sv':
		# 	torun = 'sv'
		# elif itemtype == 'eo':
		# 	torun = 'eo'
	while finished == 0:
		if torun == 'any':
			sql = 'SELECT * FROM newwikiquote WHERE done = 0 ORDER BY RAND() LIMIT 1'
		else:
			sql = 'SELECT * FROM newwikiquote WHERE done = 0 AND site = "'+torun+'" ORDER BY RAND() LIMIT 1'
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
		# elif myresult[3] == 'it':
		# 	site = itwiki
		# elif myresult[3] == 'nl':
		# 	site = nlwiki
		# elif myresult[3] == 'pl':
		# 	site = plwiki
		# elif myresult[3] == 'sv':
		# 	site = svwiki
		# elif myresult[3] == 'eo':
		# 	site = eowiki
		else:
			continue
		# Make sure it doesn't have an ID yet
		badtile = 0
		try:
			target = pywikibot.Page(site,myresult[2])
		except:
			badtile = 1
		if badtile == 1:
			sql = 'UPDATE newwikiquote SET done = 1, user = "NA", decision = 1 WHERE cid = "'+str(myresult[0])+'" AND done = 0'
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
			sql = 'UPDATE newwikiquote SET done = 1, user = "NA", decision = 1 WHERE cid = "'+str(myresult[0])+'" AND done = 0'
			mycursor.execute(sql)
			mydb.commit()
			continue
		badtile = 0
		try:
			pagetext = target.get()
		except:
			badtile = 1
		if badtile == 1:
			sql = 'UPDATE newwikiquote SET done = 1, user = "NA", decision = 1 WHERE cid = "'+str(myresult[0])+'" AND done = 0'
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
			sql = 'UPDATE newwikiquote SET done = 1, user = "NA", decision = 1 WHERE cid = "'+str(myresult[0])+'" AND done = 0'
			mycursor.execute(sql)
			mydb.commit()
			# exit()
			continue

		skip = 0
		try:
			sitelink = candidate_item_dict['sitelinks'][myresult[3]+'wikiquote']
		except:
			#{"type": "files","files": files, "q":myresult[1],'deferred_decision':'yes'}
			tile = {"id": myresult[0], "sections": [ {"type": "item", "q":myresult[1]}, {"type": "text","title": myresult[2],"url": 'https://'+myresult[3]+'.wikiquote.org/wiki/'+myresult[2].replace(' ','_'),'text':target.text[0:500]}], "controls": [{"type":"buttons", "entries":[{"type": "green","decision": "yes","label": "Match", "api_action": {'action': "wbsetsitelink", "id": myresult[1],"linksite": myresult[3]+'wikiquote',"linktitle": myresult[2]}}, {"type": "white", "decision": "skip", "label": "Skip"}, {"type": "blue", "decision": "no", "label": "No"}]}]}#'q:'+myresult[3]
			# tile = {"id": myresult[0], "sections": [ {"type": "item", "q":myresult[1]}, {"type": "wikipage","title": myresult[2],"wiki": 'enwikiquote'}], "controls": [{"type":"buttons", "entries":[{"type": "green","decision": "yes","label": "Match", "api_action": {'action': "wbsetsitelink", "id": myresult[1],"linksite": myresult[3]+'wikiquote',"linktitle": myresult[2]}}, {"type": "white", "decision": "skip", "label": "Skip"}, {"type": "blue", "decision": "no", "label": "No"}]}]}#'q:'+myresult[3]
			tiles.append(tile)
			i += 1
			if i >= int(num):
				finished = 1
	# print(json.dumps({"tiles":tiles}))
	print(callback + " ( " + json.dumps(tiles) + ")\n")
elif action == 'log_action':
	print("Content-type: text/html\n\n")
	user = GET.get('user')
	tile = GET.get('tile')
	decision = GET.get('decision')
	print(decision)
	# decision = 0 not set, 1 irrelevant, 2 no, 3 yes
	if decision == "no":
		print(int(tile))
		print(user)
		print(decision)
		sql = 'UPDATE newwikiquote SET done = 1, user = "'+user+'", decision = 2 WHERE cid = "' + tile + '"'
		# print(sql)
		mycursor.execute(sql)
		mydb.commit()
		# print("no")
	elif decision == "yes":
		sql = 'SELECT * FROM newwikiquote WHERE cid = "' + tile + '" LIMIT 1'
		# print(sql)
		mycursor.execute(sql)
		myresult = mycursor.fetchone()
		# print(myresult)
		sql = 'UPDATE newwikiquote SET done = 1, user = "'+user+'", decision = 1 WHERE qid = "'+myresult[1]+'" AND done = 0'
		mycursor.execute(sql)
		mydb.commit()
		sql = 'UPDATE newwikiquote SET done = 1, user = "'+user+'", decision = 1 WHERE candidate = "'+myresult[2]+'" AND site = "'+myresult[3]+'" AND done = 0'
		mycursor.execute(sql)
		mydb.commit()
		sql = 'UPDATE newwikiquote SET done = 1, user = "'+user+'", decision = 3 WHERE cid = "' + tile + '"'
		mycursor.execute(sql)
		mydb.commit()
		# print("yes")
else:
	print("Content-type: text/html\n\n")
	print('Incorrect action!')
	print(args)

# mycursor.close()
# mydb.close()
