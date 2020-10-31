#!/usr/bin/python
# -*- coding: utf-8  -*-
# Import commons sitelinks for the infobox QIDs
# Mike Peel     10-Jun-2018      v1
# Mike Peel     31-Oct-2020      v2, tidy

from __future__ import unicode_literals

import pywikibot
from pywikibot.data import api
import numpy as np
import time
import string
from pywikibot import pagegenerators
import urllib
import pprint
import csv

templates = ["individual aircraft", "Individual aircraft","Wikidata person", "wikidata person", "On Wikidata", "on Wikidata", "In Wikidata", "in Wikidata", "Wikidata", "wikidata", "Authority control", "authority control", "Ac", "ac", "Wikidata Infobox", "Wikidata infobox", "wikidata infobox", "wikidata Infobox", "Infobox Wikidata", "infobox Wikidata", "Infobox wikidata", "infobox wikidata", 'Wikidata place', 'wikidata place', 'Object location', 'object location']

def prettyPrint(variable):
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(variable)

wikidata_site = pywikibot.Site("wikidata", "wikidata")
repo = wikidata_site.data_repository()  # this is a DataSite object
commons = pywikibot.Site('commons', 'commons')

database = 0
existing_uses = {}
if database:
    print('Loading database...')
    with open('commons_wikidata_infobox_uses.csv', mode='r') as infile:
        reader = csv.reader(infile)
        existing_uses = {rows[0] for rows in reader}
    print('Database loaded!')


category = 'Category:Uses of Wikidata Infobox with manual qid'
cat = pywikibot.Category(commons,category)
targetcats = pagegenerators.SubCategoriesPageGenerator(cat, recurse=False);


for targetcat in targetcats:
    if targetcat.title() in existing_uses:
        print('In database')
        continue

    print(targetcat.title())
    target_text = targetcat.get()

    try:
        wd_item = pywikibot.ItemPage.fromPage(targetcat)
        print('Category has Wikidata item attached already')
        continue
    except:
        # print "No Wikidata sitelink found"
        null = 0

    id_val = 0
    value = 0

    for i in range(0,len(templates)):
        try:
            value = (target_text.split("{{"+templates[i]+"|Wikidata="))[1].split("}}")[0]
            try:
                value = value.split('|')[0]
            except:
                null = 1
            if value != 0 and id_val == 0:
                id_val = value
        except:
            null = 1
            # print '1'
        try:
            value = (target_text.split("{{"+templates[i]+"|wikidata="))[1].split("}}")[0]
            try:
                value = value.split('|')[0]
            except:
                null = 1
            if value != 0 and id_val == 0:
                id_val = value
        except:
            null = 1
            # print '1'
        try:
            value = (target_text.split("{{"+templates[i]+"|qid="))[1].split("}}")[0]
            try:
                value = value.split('|')[0]
            except:
                null = 1
            if value != 0 and id_val == 0:
                id_val = value
        except:
            null = 1
        try:
            value = (target_text.split("{{"+templates[i]+"| qid ="))[1].split("}}")[0]
            try:
                value = value.split('|')[0]
            except:
                null = 1
            if value != 0 and id_val == 0:
                id_val = value
        except:
            null = 1
        try:
            value = (target_text.split("{{"+templates[i]+"|qid ="))[1].split("}}")[0]
            try:
                value = value.split('|')[0]
            except:
                null = 1
            if value != 0 and id_val == 0:
                id_val = value
        except:
            null = 1
        try:
            value = (target_text.split("{{"+templates[i]+"| qid="))[1].split("}}")[0]
            try:
                value = value.split('|')[0]
            except:
                null = 1
            if value != 0 and id_val == 0:
                id_val = value
        except:
            null = 1
        try:
            value = (target_text.split("{{"+templates[i]+" |qid="))[1].split("}}")[0]
            try:
                value = value.split('|')[0]
            except:
                null = 1
            if value != 0 and id_val == 0:
                id_val = value
        except:
            null = 1
        try:
            value = (target_text.split("{{"+templates[i]+" | qid ="))[1].split("}}")[0]
            try:
                value = value.split('|')[0]
            except:
                null = 1
            if value != 0 and id_val == 0:
                id_val = value
        except:
            null = 1
        try:
            value = (target_text.split("{{"+templates[i]+" |qid ="))[1].split("}}")[0]
            try:
                value = value.split('|')[0]
            except:
                null = 1
            if value != 0 and id_val == 0:
                id_val = value
        except:
            null = 1
        try:
            value = (target_text.split("{{"+templates[i]+" | qid="))[1].split("}}")[0]
            try:
                value = value.split('|')[0]
            except:
                null = 1
            if value != 0 and id_val == 0:
                id_val = value
        except:
            null = 1
        try:
            value = (target_text.split("{{"+templates[i]+" |1="))[1].split("}}")[0]
            try:
                value = value.split('|')[0]
            except:
                null = 1
            if value != 0 and id_val == 0:
                id_val = value
        except:
            null = 2
            # print '2'
        try:
            value = (target_text.split("{{"+templates[i]+"|1="))[1].split("}}")[0]
            try:
                value = value.split('|')[0]
            except:
                null = 1
            if value != 0 and id_val == 0:
                id_val = value
        except:
            null = 3
            # print '3'
        try:
            value = (target_text.split("{{"+templates[i]+"|"))[1].split("}}")[0]
            try:
                value = value.split('|')[0]
            except:
                null = 1
            if value != 0 and id_val == 0:
                id_val = value
        except:
            null = 1
    print(id_val)
    if id_val != 0 and "defaultsort" not in id_val:
        id_val = id_val.strip()
        try:
            candidate_item = pywikibot.ItemPage(repo, id_val)
            candidate_item_dict = candidate_item.get()
        except:
            print('Huh - no page found')
            continue

        try:
            existing_id = candidate_item_dict['claims']['P910']
            print('P910 exists, following that.')
            for clm2 in existing_id:
                candidate_item = clm2.getTarget()
                candidate_item_dict = candidate_item.get()
                print(candidate_item.title())
        except:
            null = 0
        try:
            sitelink = candidate_item_dict['sitelinks']['commonswiki']
        except:
            # No existing sitelink found, add the new one
            data = {'sitelinks': [{'site': 'commonswiki', 'title': targetcat.title()}]}
            try:
                print("\n\n")
                print(id_val)
                prettyPrint(candidate_item_dict)
                print(data)
                candidate_item.editEntity(data, summary=u'Add commons sitelink based on QID on Commons')
            except:
                print('Edit failed')

