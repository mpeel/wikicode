#!/usr/bin/python
# -*- coding: utf-8  -*-
# Tidy up calls to Wikidata infoboxes on Commons
# Started 19 June 2018 by Mike Peel
from __future__ import unicode_literals

import pywikibot
import numpy as np
import time
import string
from pywikibot import pagegenerators
from pywikibot.data import api
import urllib
from pibot_functions import *
import re

maxnum = 10000
nummodified = 0

commons = pywikibot.Site('commons', 'commons')
repo = commons.data_repository()  # this is a DataSite object
manual = False
templates = ['Wikidata box', 'Інфабокс','Wdbox','Wikidata infobox', 'Infobox Wikidata', 'Infobox wikidata', 'WI', 'Wdbox', 'Wikidatainfobox']
others = ['mainw','Mainw', 'Interwiki from Wikidata', 'interwiki from Wikidata', 'label', 'Label', 'object location', 'Object location', "Interwiki from Wikidata", "interwiki from Wikidata", "Interwiki from wikidata", "interwiki from wikidata", "PeopleByName", "peopleByName", "Authority control", "authority control", "On Wikidata", "on Wikidata", "In Wikidata", "in Wikidata", "Wikidata", "wikidata", "en", 'Individual aircraft', 'individual aircraft', 'Wikidata place','wikidata place', 'Articles via Wikidata', 'Articles via Wikidata |P301=']
enwp = ['mainw', 'Mainw', 'on Wikipedia|en=', 'On Wikipedia|en=']
savemessage="Tidy Wikidata Infobox call"
wikidatainfobox = ["Wikidata Infobox", "Wikidata infobox", "wikidata infobox", "wikidata Infobox", "Infobox Wikidata", "infobox Wikidata", "infobox wikidata", "Infobox wikidata", "Wikidata  infobox", "wikidata  infobox", "Wikidata  Infobox", "wikidata  Infobox", "Wdbox", "wdbox", 'WI', 'wikidatainfobox', 'Інфабокс', 'інфабокс', 'Wikidata box', 'wikidata box', 'Wikidatainfobox', 'wikidatainfobox']

def search_entities(site, itemtitle,limit=100,offset=0):
     params = { 'action' :'query',
                'list': 'search',
                'format' : 'json',
                'srlimit': limit,
                'sroffset': offset,
                'srnamespace': 14,
                'srsearch': itemtitle}
     request = api.Request(site=site, parameters=params)
     return request.submit()

def migratecat(targetcat):
    print(targetcat)
    target_text = targetcat.get()
    print(target_text)
    # Check that we have a Wikidata infobox here
    if not any(option in target_text for option in wikidatainfobox):
        print('No infobox')
        return 0

    # Fetch the info from Wikidata
    wd_item = 0
    try:
        wd_item = pywikibot.ItemPage.fromPage(targetcat)
        item_dict = wd_item.get()
        print(wd_item.title())
    except:
        print('No Wikidata ID')
        null = 0

    # Or in the main topic
    wd_item2 = 0
    try:
        p301 = item_dict['claims']['P301']
        for clm2 in p301:
            wd_item2 = clm2.getTarget()
            item_dict = wd_item.get()
    except:
        null = 1

    # Remove other templates
    for i in range(0,len(others)):
        target_text = target_text.replace("{{"+others[i]+"}}", "")
        if wd_item != 0:
            target_text = target_text.replace("{{" + others[i] + "|" + wd_item.title() + "}}", "")
            target_text = target_text.replace("{{" + others[i] + "|" + wd_item.title() + " }}", "")
            target_text = target_text.replace("{{" + others[i] + "|Wikidata=" + wd_item.title() + "}}", "")
            target_text = target_text.replace("{{" + others[i] + "|wikidata=" + wd_item.title() + "}}", "")
            target_text = target_text.replace("{{" + others[i] + "| Wikidata=" + wd_item.title() + "}}", "")
            target_text = target_text.replace("{{" + others[i] + "| wikidata=" + wd_item.title() + "}}", "")
            target_text = target_text.replace("{{" + others[i] + wd_item.title() + "}}", "")
        if wd_item2 != 0:
            target_text = target_text.replace("{{" + others[i] + "|" + wd_item2.title() + "}}", "")
            target_text = target_text.replace("{{" + others[i] + "|" + wd_item2.title() + " }}", "")
            target_text = target_text.replace("{{" + others[i] + "|Wikidata=" + wd_item2.title() + "}}", "")
            target_text = target_text.replace("{{" + others[i] + "|wikidata=" + wd_item2.title() + "}}", "")
            target_text = target_text.replace("{{" + others[i] + "| Wikidata=" + wd_item2.title() + "}}", "")
            target_text = target_text.replace("{{" + others[i] + "| wikidata=" + wd_item2.title() + "}}", "")
            target_text = target_text.replace("{{" + others[i] + wd_item2.title() + "}}", "")
        target_text = target_text.replace("{{" + others[i] + "| }}", "")
        target_text = target_text.replace("{{" + others[i] + " | }}", "")

    try:
        enwp_link = get_sitelink_title(item_dict['sitelinks']['enwiki'])
        enwp_link2 = enwp_link[0].lower() + enwp_link[1:]
        for i in range(0,len(enwp)):
            target_text = target_text.replace("{{"+enwp[i]+"|"+enwp_link+"}}", "")
            target_text = target_text.replace("{{"+enwp[i]+"|"+enwp_link2+"}}", "")
    except:
        null = 1

    for i in range(0,len(wikidatainfobox)):
        if wd_item != 0:
            target_text = re.sub( r"\{\{\s*" + wikidatainfobox[i] + r"\s*\|\s*\|?\s*qid\s*=\s*" + wd_item.title() + r"\s*\)",  '{{Wikidata Infobox',  target_text,  re.MULTILINE)
            target_text = re.sub( r"\{\{\s*" + wikidatainfobox[i] + r"\s*\|?\s*qid\s*=\s*" + wd_item.title() + r"\s*",  '{{Wikidata Infobox',  target_text,  re.MULTILINE)
            target_text = re.sub( r"\{\{\s*" + wikidatainfobox[i] + r"\s*\|\s*\|?\s*wikidata\s*=\s*" + wd_item.title() + r"\s*\)",  '{{Wikidata Infobox',  target_text,  re.MULTILINE)
            target_text = re.sub( r"\{\{\s*" + wikidatainfobox[i] + r"\s*\|\s*\|?\s*Wikidata\s*=\s*" + wd_item.title() + r"\s*\)",  '{{Wikidata Infobox',  target_text,  re.MULTILINE)
            # target_text = target_text.replace("{{"+wikidatainfobox[i]+"|"+wd_item.title(),'{{Wikidata Infobox')
            # target_text = target_text.replace("{{"+wikidatainfobox[i]+"|qid="+wd_item.title(),'{{Wikidata Infobox')
            # target_text = target_text.replace("{{"+wikidatainfobox[i]+"|qid= "+wd_item.title(),'{{Wikidata Infobox')
            # target_text = target_text.replace("{{"+wikidatainfobox[i]+"|defaultsort=no|qid="+wd_item.title(),'{{Wikidata Infobox|defaultsort=no')
            # target_text = target_text.replace("{{"+wikidatainfobox[i]+"| qid="+wd_item.title(),'{{Wikidata Infobox')
            # target_text = target_text.replace("{{"+wikidatainfobox[i]+"| qid= "+wd_item.title(),'{{Wikidata Infobox')
            # target_text = target_text.replace("{{"+wikidatainfobox[i]+"| qid ="+wd_item.title(),'{{Wikidata Infobox')
            # target_text = target_text.replace("{{"+wikidatainfobox[i]+"| qid = "+wd_item.title(),'{{Wikidata Infobox')
            # target_text = target_text.replace("{{"+wikidatainfobox[i]+" |qid="+wd_item.title(),'{{Wikidata Infobox')
            # target_text = target_text.replace("{{"+wikidatainfobox[i]+" |qid = "+wd_item.title(),'{{Wikidata Infobox')
            # target_text = target_text.replace("{{"+wikidatainfobox[i]+" |qid ="+wd_item.title(),'{{Wikidata Infobox')
            # target_text = target_text.replace("{{"+wikidatainfobox[i]+" |qid= "+wd_item.title(),'{{Wikidata Infobox')
            # target_text = target_text.replace("{{"+wikidatainfobox[i]+" | qid="+wd_item.title(),'{{Wikidata Infobox')
            # target_text = target_text.replace("{{"+wikidatainfobox[i]+" | qid ="+wd_item.title(),'{{Wikidata Infobox')
            # target_text = target_text.replace("{{"+wikidatainfobox[i]+" | qid = "+wd_item.title(),'{{Wikidata Infobox')
            # target_text = target_text.replace("{{"+wikidatainfobox[i]+"||qid="+wd_item.title()+"\n",'{{Wikidata Infobox')
            # target_text = target_text.replace("{{"+wikidatainfobox[i]+"|\n qid="+wd_item.title()+"\n",'{{Wikidata Infobox')
            # target_text = target_text.replace("{{"+wikidatainfobox[i]+"|\nqid="+wd_item.title()+"\n",'{{Wikidata Infobox')
            # target_text = target_text.replace("{{"+wikidatainfobox[i]+"|\nqid="+wd_item.title(),'{{Wikidata Infobox')
        if wd_item2 != 0:
            target_text = re.sub( r"\{\{\s*" + wikidatainfobox[i] + r"\s*\|\s*\|?\s*qid\s*=\s*" + wd_item2.title() + r"\s*\)",  '{{Wikidata Infobox',  target_text,  re.MULTILINE)
            target_text = re.sub( r"\{\{\s*" + wikidatainfobox[i] + r"\s*\|\s*\|?\s*wikidata\s*=\s*" + wd_item2.title() + r"\s*\)",  '{{Wikidata Infobox',  target_text,  re.MULTILINE)
            target_text = re.sub( r"\{\{\s*" + wikidatainfobox[i] + r"\s*\|\s*\|?\s*Wikidata\s*=\s*" + wd_item2.title() + r"\s*\)",  '{{Wikidata Infobox',  target_text,  re.MULTILINE)
            # target_text = target_text.replace("{{"+wikidatainfobox[i]+"|"+wd_item2.title(),'{{Wikidata Infobox')
            # target_text = target_text.replace("{{"+wikidatainfobox[i]+"|qid="+wd_item2.title(),'{{Wikidata Infobox')
            # target_text = target_text.replace("{{"+wikidatainfobox[i]+"|qid= "+wd_item2.title(),'{{Wikidata Infobox')
            # target_text = target_text.replace("{{"+wikidatainfobox[i]+"| qid="+wd_item2.title(),'{{Wikidata Infobox')
            # target_text = target_text.replace("{{"+wikidatainfobox[i]+"| qid ="+wd_item2.title(),'{{Wikidata Infobox')
            # target_text = target_text.replace("{{"+wikidatainfobox[i]+"| qid = "+wd_item2.title(),'{{Wikidata Infobox')
            # target_text = target_text.replace("{{"+wikidatainfobox[i]+" |qid="+wd_item2.title(),'{{Wikidata Infobox')
            # target_text = target_text.replace("{{"+wikidatainfobox[i]+" |qid = "+wd_item2.title(),'{{Wikidata Infobox')
            # target_text = target_text.replace("{{"+wikidatainfobox[i]+" |qid ="+wd_item2.title(),'{{Wikidata Infobox')
            # target_text = target_text.replace("{{"+wikidatainfobox[i]+" |qid= "+wd_item2.title(),'{{Wikidata Infobox')
            # target_text = target_text.replace("{{"+wikidatainfobox[i]+" | qid="+wd_item2.title(),'{{Wikidata Infobox')
            # target_text = target_text.replace("{{"+wikidatainfobox[i]+" | qid ="+wd_item2.title(),'{{Wikidata Infobox')
            # target_text = target_text.replace("{{"+wikidatainfobox[i]+" | qid = "+wd_item2.title(),'{{Wikidata Infobox')
            # target_text = target_text.replace("{{"+wikidatainfobox[i]+"||qid="+wd_item2.title()+"\n",'{{Wikidata Infobox')
            # target_text = target_text.replace("{{"+wikidatainfobox[i]+"|\n qid="+wd_item2.title()+"\n",'{{Wikidata Infobox')
            # target_text = target_text.replace("{{"+wikidatainfobox[i]+"|\nqid="+wd_item2.title()+"\n",'{{Wikidata Infobox')
            # target_text = target_text.replace("{{"+wikidatainfobox[i]+"|\nqid="+wd_item2.title(),'{{Wikidata Infobox')
        target_text = target_text.replace("{{"+wikidatainfobox[i],'{{Wikidata Infobox')
        target_text = target_text.replace("{{ "+wikidatainfobox[i],'{{Wikidata Infobox')
        target_text = target_text.replace("{{"+wikidatainfobox[i].replace(" ","_"),'{{Wikidata Infobox')
        target_text = target_text.replace("{{ "+wikidatainfobox[i].replace(" ","_"),'{{Wikidata Infobox')

    lines = target_text.splitlines()
    insertline = 0
    i = 0
    j = 0
    for line in lines:
        if '{{Wikidata Infobox}}' in line:
            i += 1
            if i != 1:
                lines[j] = lines[j].replace('{{Wikidata Infobox}}', '')
        j += 1
    target_text = "\n".join(lines)

    # Only remove whitespace if we're making another change
    if (target_text != targetcat.get()):
        target_text = target_text.replace('\n\n\n','\n')
        target_text = target_text.replace('\n\n\n','\n')
        target_text = target_text.replace('\n\n{{Wikidata Infobox','\n{{Wikidata Infobox')
        # target_text = target_text.replace('\n\n','\n')

    # Time to save it
    if (target_text != targetcat.get()):
        targetcat.text = target_text.strip()
        print(targetcat.text)
        if manual:
            text = input("Save on Commons? ")
            if text == '':
                try:
                    targetcat.save(savemessage)
                    return 1
                except:
                    print("That didn't work!")
                    return 0
            else:
                return 0
        else:
            try:
                targetcat.save(savemessage)
                return 1
            except:
                print("That didn't work!")
                return 0
    else:
        return 0


# Check for Wikidata= uses
candidates = []
try:
    candidates = search_entities(commons, "insource:/\{Wikidata Infobox\|Wikidata/",limit=500)
except:
    null = 0
for candidate in candidates['query']['search']:
    targetcat = pywikibot.Page(commons, str(candidate['title']))
    print(targetcat)
    print("\n" + targetcat.title())
    nummodified += migratecat(targetcat)
    # targetcat.touch()
    if nummodified >= maxnum:
        print('Reached the maximum of ' + str(maxnum) + ' entries modified, quitting!')
        exit()

# Check for wikidata= uses
candidates = []
try:
    candidates = search_entities(commons, "insource:/\{Wikidata Infobox\|wikidata/",limit=500)
except:
    null = 0
for candidate in candidates['query']['search']:
    targetcat = pywikibot.Page(commons, str(candidate['title']))
    print(targetcat)
    print("\n" + targetcat.title())
    nummodified += migratecat(targetcat)
    # targetcat.touch()
    if nummodified >= maxnum:
        print('Reached the maximum of ' + str(maxnum) + ' entries modified, quitting!')
        exit()

# Check through the manual ID category
category = 'Category:Uses of Wikidata Infobox with manual qid'
cat = pywikibot.Category(commons,category)

# Categories
targetcats = pagegenerators.SubCategoriesPageGenerator(cat, recurse=False);
for targetcat in targetcats:
    print(targetcat)
    print("\n" + targetcat.title())
    nummodified += migratecat(targetcat)

    if nummodified >= maxnum:
        print('Reached the maximum of ' + str(maxnum) + ' entries modified, quitting!')
        exit()

# Galleries
targetcats = pagegenerators.CategorizedPageGenerator(cat, recurse=False,namespaces=0);
for targetcat in targetcats:
    print(targetcat)
    print("\n" + targetcat.title())
    nummodified += migratecat(targetcat)

    if nummodified >= maxnum:
        print('Reached the maximum of ' + str(maxnum) + ' entries modified, quitting!')
        exit()

# Check for uses of the Wikidata Infobox redirects
for i in range(0,len(templates)):
    template = pywikibot.Page(commons, 'Template:'+templates[i])
    targetcats = template.embeddedin()#namespaces='14')
    for targetcat in targetcats:
        print(targetcat)
        print("\n" + targetcat.title())
        nummodified += migratecat(targetcat)

        if nummodified >= maxnum:
            print('Reached the maximum of ' + str(maxnum) + ' entries modified, quitting!')
            exit()



print('Done! Edited ' + str(nummodified) + ' entries')

# EOF
