#!/usr/bin/python3
# -*- coding: utf-8  -*-
import os
import json
import re
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
wikidata_site.login()
repo = wikidata_site.data_repository()  # this is a DataSite object


wikis = {
    'en': 'English',
    'pt': 'Português',
    'de': 'Deutsch',
    'es': 'Español',
    'fr': 'Français',
    'it': 'Italiano',
    'nl': 'Nederlands',
    'pl': 'Polski',
    'sv': 'Svenska',
    'eo': 'Esperanto',
    'ml': 'Malayalam',
    'af': 'Afrikaans',
}

additional_wikis = """
ru cs et uk he fa sr tr az sk ca bs zh id ar fi sl lt bn su hy bg ig hr tl uz el nn vi li bjn hu as ja ko sah la ta hi te guw kn ro th ur gl gu be ka no cy pcm sq eu ku ms da bcl sa is gor br mr af ky
""".split()

wikis.update({
	code: code.replace('_', '-')
	for code in additional_wikis
	if code not in wikis
})

sites = {}

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
	num = 10
if int(num) > 50:
	num = 10
lang = GET.get('lang')
if action == 'desc':
	wiki_options = {'all': 'Any', **wikis}
	print("Content-type: application/json\n\n")
	print(callback + " ( " + json.dumps({'label': {'en':'New Wikiquote article and category matches'}, 'description': {'en':'Match new Wikiquote pages with Wikidata items, and add the sitelink to Wikidata.'}, 'instructions': {'en':'Pi bot is thinking about creating new items for these pages, but first it wants your help to match them to existing items.<br />If the match is right, please add the link to Wikidata using "Match". If it is clearly wrong, select "No". If you are not sure, press "Skip".<br />Bug reports and feedback should be sent to User:Mike_Peel.'}, 'icon': 'https://upload.wikimedia.org/wikipedia/commons/thumb/f/fa/Wikiquote-logo.svg/120px-Wikiquote-logo.svg.png','options': [{'name': 'Entry type','key': 'type','values': wiki_options}]}) + " )\n")

elif action == 'tiles':
	print("Content-type: application/json\n\n")
	i = 0
	finished = 0
	tiles = []

	itemtype = GET.get('type', 'all')

	if itemtype in wikis:
		torun = itemtype
	else:
		torun = 'any'

	while finished == 0:

		if torun == 'any':
			placeholders = ','.join(['%s'] * len(wikis))
			sql = (
				'SELECT * FROM newwikiquote '
				'WHERE done = 0 AND site IN (' + placeholders + ') '
				'ORDER BY RAND() LIMIT 1'
			)
			params = tuple(wikis)
		else:
			sql = (
				'SELECT * FROM newwikiquote '
				'WHERE done = 0 AND site = %s '
				'ORDER BY RAND() LIMIT 1'
			)
			params = (torun,)

		mycursor.execute(sql, params)
		myresult = mycursor.fetchone()

		if myresult is None:
			break

		wiki = myresult[3]

		if wiki not in wikis:
			continue

		if wiki not in sites:
			sites[wiki] = pywikibot.Site(wiki, 'wikiquote')
			sites[wiki].login()

		site = sites[wiki]

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
		# no need to create tile if link already exists
		try:
			siteLink = candidate_item_dict['sitelinks'][myresult[3]+'wikiquote']
		except:
			cleaned_text = target.text[0:500]
			# for template calls {{..}}
			cleaned_text = re.sub(r'\{\{[^}]*\}\}', '', cleaned_text)
			# for [category:..] or other similar cases
			cleaned_text = re.sub(r'\[\[(?:Category|Kategorie|Categoria)[^\]]*\]\]', '', cleaned_text, flags=re.IGNORECASE)
			# for [file] or other similar
			cleaned_text = re.sub(r'\[\[(?:File|Image|Datei|Fichier|Archivo|Imagem)[^\]]*\]\]', '', cleaned_text, flags=re.IGNORECASE)
			# for __NOTOC__ and similar
			cleaned_text = re.sub(r'__[A-Z]+__', '', cleaned_text)
			# [w:Page|Display] to Display (interwiki links)
			cleaned_text = re.sub(r'\[\[[wW]:[^|]+\|([^\]]+)\]\]', r'\1', cleaned_text)
			# [w:Page|Display] to Display (piped links)
			cleaned_text = re.sub(r'\[\[[^\]|]+\|([^\]]+)\]\]', r'\1', cleaned_text)
			# simple links without pipes
			cleaned_text = re.sub(r'\[\[([^\]|]+)\]\]', r'\1', cleaned_text)
			# section headers
			cleaned_text = re.sub(r'={2,}[^=]+={2,}', '', cleaned_text)
			# extra whitespace
			cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
			tile = {"id": myresult[0], "sections": [ {"type": "item", "q":myresult[1]}, {"type": "text","title": myresult[2],"url": 'https://'+myresult[3]+'.wikiquote.org/wiki/'+myresult[2].replace(' ','_'),'text':cleaned_text}], "controls": [{"type":"buttons", "entries":[{"type": "green","decision": "yes","label": "Match", "api_action": {'action': "wbsetsitelink", "id": myresult[1],"linksite": myresult[3]+'wikiquote',"linktitle": myresult[2]}}, {"type": "white", "decision": "skip", "label": "Skip"}, {"type": "blue", "decision": "no", "label": "No"}]}]}#'q:'+myresult[3]
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
