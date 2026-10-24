#!/usr/bin/python3
# -*- coding: utf-8  -*-
import os
import json
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
    'simple': 'Simple',
    'pt': 'Português',
    'de': 'Deutsch',
    'es': 'Español',
    'fr': 'Français',
    'it': 'Italiano',
    'nl': 'Nederlands',
    'pl': 'Polski',
    'sv': 'Svenska',
    'eo': 'Esperanto',
    'dag': 'Dagbanli',
    'ml': 'Malayalam',
    'af': 'Afrikaans',
    'cy': 'Welsh',
    'et': 'Estonian',
}

additional_wikis = """
ab ace ady ak als alt ami am ang ann anp an arc ar ary arz ast
as atj avk av awa ay azb az ban bar bat_smg ba bbc bcl bdr
be_x_old be bew bg bh bi bjn blk bm bn bol bo bpy br bs btm
bug bxr ca cbk_zam cdo ceb ce cho chr ch chy ckb co crh csb
cs cu cv da dga din diq dsb dtp dty dv dz ee el eml eu ext
fat fa ff fiu_vro fi fj fon fo frp frr fur fy gag gan ga gcr
gd glk gl gn gom gor got gpe guc gur gu guw gv hak ha haw he
hif hi ho hr hsb ht hu hy hyw ia iba id ie igl ig ik ilo inh
io isv is iu jam ja jbo jv kaa kab kai kaj ka kbd kbp kcg
kge kg ki kk km knc kn koi ko krc ksh ks kus ku kv kw ky lad
la lb lez lfn lg lij li lld lmo ln lo ltg lt lv mad mag mai
map_bms mdf mg mhr min mi mk mni mn mnw mos mo mrj mr ms mt
mwl myv my mzn nah nap nds_nl nds ne new ng nia nn nov no
nqo nrm nr nso nup nv ny oc olo om or os pag pam pap pa pcd
pcm pdc pfl pi pms pnb pnt ppl ps pwn qu rki rm rmy rn
roa_rup roa_tara ro rsk rue ru rw sah sat sa scn sco sc sd
se sg shi shn sh si skr sk sl smn sm sn so sq srn sr ss stq
st su sw syl szl szy ta tay tcy tdd tet te tg th tig ti tk
tl tly tn tok to tpi trv tr ts tt tum tw tyv ty udm ug uk
ur uz vec vep ve vi vls vo war wa wo wuu xal xh xmf yi yo
za zea zgh zh_classical zh_min_nan zh_yue zh zu
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
	print("Content-type: application/json\n\n")
	wiki_options = {'all': 'Any', **wikis}
	print(callback + " ( " + json.dumps({'label': {'en':'New Wikipedia article and category matches'}, 'description': {'en':'Match new Wikipedia articles and categories with Wikidata items, and add the sitelink to Wikidata.'}, 'instructions': {'en':'Pi bot is thinking about creating new items for these articles, but first it wants your help to match them to existing items.<br />If the match is right, please add the link to Wikidata using "Match". If it is clearly wrong, select "No". If you are not sure, press "Skip".<br />Bug reports and feedback should be sent to User:Mike_Peel.'}, 'icon': 'https://upload.wikimedia.org/wikipedia/en/thumb/8/80/Wikipedia-logo-v2.svg/120px-Wikipedia-logo-v2.svg.png','options': [{'name': 'Entry type','key': 'type','values': wiki_options}]}) + " )\n")
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
				'SELECT * FROM newarticles '
				'WHERE done = 0 AND site IN (' + placeholders + ') '
				'ORDER BY RAND() LIMIT 1'
			)
			params = tuple(wikis)
		else:
			sql = (
				'SELECT * FROM newarticles '
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
			sites[wiki] = pywikibot.Site(wiki, 'wikipedia')
			sites[wiki].login()

		site = sites[wiki]

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

		sitelink = ''
		try:
			sitelink = candidate_item_dict['sitelinks'][myresult[3]+'wiki']
		except:
			sitelink = ''

		if sitelink != '':
			print(myresult)
			print('Has sitelink')
			exit()
			
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
		sql = 'UPDATE newarticles SET done = 1, user = "'+user+'", decision = 2 WHERE cid = "' + tile + '"'
		# print(sql)
		mycursor.execute(sql)
		mydb.commit()
		# print("no")
	elif decision == "yes":
		sql = 'SELECT * FROM newarticles WHERE cid = "' + tile + '" LIMIT 1'
		# print(sql)
		mycursor.execute(sql)
		myresult = mycursor.fetchone()
		# print(myresult)
		sql = 'UPDATE newarticles SET done = 1, user = "'+user+'", decision = 1 WHERE qid = "'+myresult[1]+'" AND done = 0'
		mycursor.execute(sql)
		mydb.commit()
		sql = 'UPDATE newarticles SET done = 1, user = "'+user+'", decision = 1 WHERE candidate = "'+myresult[2]+'" AND site = "'+myresult[3]+'" AND done = 0'
		mycursor.execute(sql)
		mydb.commit()
		sql = 'UPDATE newarticles SET done = 1, user = "'+user+'", decision = 3 WHERE cid = "' + tile + '"'
		mycursor.execute(sql)
		mydb.commit()
		# print("yes")
else:
	print("Content-type: text/html\n\n")
	print('Incorrect action!')
	print(args)

# mycursor.close()
# mydb.close()
