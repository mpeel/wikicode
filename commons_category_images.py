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
    print callback + " ( " + json.dumps({'label': {'en':'Images from Commons categories'}, 'description': {'en':'Add images from Commons categories to the linked Wikidata items.'}, 'instructions': {'en':'Please make sure that the image depicts the item! Do not add more than one file per type (e.g., image, coat of arms) per item. Once you have added all approriate files, click "Save - all candidates marked". If in doubt, press "Skip".<br />Bug reports and feedback should be sent to commons:User:Mike Peel.'}, 'icon': 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/4a/Commons-logo.svg/120px-Commons-logo.svg.png'}) + " )\n"
elif action == 'tiles':
    print "Content-type: application/json\n\n"
    i = 0
    finished = 0
    tiles = []
    while finished == 0:
        mycursor.execute('SELECT * FROM image_candidates WHERE done = 0 ORDER BY RAND() LIMIT 1')#%d' % (int(num),))
        myresult = mycursor.fetchone()
        # Make sure the category has a wikidata item
        targetcat = pywikibot.Category(commons,myresult[1])
        try:
            wd_item = pywikibot.ItemPage.fromPage(targetcat)
            item_dict = wd_item.get()
        except:
            continue

        # Check for P301
        try:
            existing_id = item_dict['claims']['P301']
            for clm2 in existing_id:
                wd_item = clm2.getTarget()
                item_dict = wd_item.get()
        except:
            null = 0

        skip = 0
        try:
            p18 = item_dict['claims']['P18']
            skip = 1
        except:
            null = 0
        if skip == 1:
            continue

        # Look through the candidates
        gen = pagegenerators.CategorizedPageGenerator(targetcat,recurse=False)
        filelist = []
        for page in gen:
            if 'File' in page.title():
                image = pywikibot.FilePage(page)
                if image.isRedirectPage():
                    image = pywikibot.FilePage(image.getRedirectTarget())
                if not image.exists():
                    continue
                priority = 0
                if image.globalusage():
                    priority = 1
                filelist.append([page.title().replace('File:',''), priority])
        k = 0
        files = []
        # Include priority images in the list
        for file in filelist:
            if k >= 10:
                break
            if file[1] == 1:
                files.append(file[0])
                file[1] = -1
            k += 1
        # And then fill up with the others
        for file in filelist:
            if k >= 10:
                break
            if file[1] == 0:
                files.append(file[0])
            k += 1
        if k != 0:
            qid = wd_item.title()
            tile = {"id": myresult[0], "sections": [ {"type": "item", "q":qid}, {"type": "wikipage","title": myresult[1],"wiki": "commonswiki"}, {"type": "files","files": files, "item":qid,'deferred_decision':'yes'}], "controls": [{"type":"buttons", "entries":[{"type": "green", "decision": "no", "label": "Save - all candidates marked"}, {"type": "white", "decision": "skip", "label": "Skip"}]}]}
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
        sql = 'UPDATE image_candidates SET done = 1, user = "'+user+'", decision = 2 WHERE iid = "' + tile + '"'
        # print sql
        mycursor.execute(sql)
        mydb.commit()
        print "no"
    elif decision == "yes":
        sql = 'UPDATE image_candidates SET done = 1, user = "'+user+'", decision = 3 WHERE iid = "' + tile + '"'
        mycursor.execute(sql)
        mydb.commit()
        print "yes"
else:
    print "Content-type: text/html\n\n"
    print 'Incorrect action!'
    print args
    
# mycursor.close()
# mydb.close()