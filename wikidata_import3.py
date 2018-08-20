#!/usr/bin/python
# -*- coding: utf-8  -*-
# Move commons category sitelinks to category items where needed
# Mike Peel     10-Jun-2018      v1

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

def prettyPrint(variable):
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(variable)

wikidata_site = pywikibot.Site("wikidata", "wikidata")
repo = wikidata_site.data_repository()  # this is a DataSite object
commons = pywikibot.Site('commons', 'commons')
enwiki = pywikibot.Site('en', 'wikipedia')

# Fetch the list
target_wiki = pywikibot.Page(commons, 'User:Rudolphous/Infobox')
target_wikitext = target_wiki.get()
target_wikitext = target_wikitext.replace('|-\n','')
target_wikitext = target_wikitext.replace('{| class="wikitable sortable"\n! Categorie !! Interwiki\n','')
target_wikitext = target_wikitext.replace('|}','')
target_wikitext = target_wikitext.replace('|','')
target_wikitext = target_wikitext.replace('  ',' ').strip()
lines = target_wikitext.splitlines()
i = 0
for row in lines:
    split = row.strip().split(']] [[:en:')
    category = split[0].replace('[[:','').strip()
    enwp = split[1].replace(']]','').strip()

    print category + " - " + enwp
    page = pywikibot.Page(enwiki, enwp)
    try:
        wd_item = pywikibot.ItemPage.fromPage(page)
        print wd_item
        item_dict = wd_item.get()
    except:
        print 'Huh - no page found'
        continue
    try:
        existing_id = item_dict['claims']['P910']
        print 'P910 exists, following that.'
        for clm2 in existing_id:
            wd_item = clm2.getTarget()
            item_dict = wd_item.get()
            print wd_item.title()
    except:
        print 'P910 not found'
    try:
        sitelink = item_dict['sitelinks']['commonswiki']
        print 'Has sitelink'
    except:
        # No existing sitelink found, add the new one
        data = {'sitelinks': [{'site': 'commonswiki', 'title': category}]}
        try:
            print "\n\n"
            prettyPrint(item_dict)
            print data
            print wd_item.title()
            # text = raw_input("Save? ")
            # if text == 'y':
            wd_item.editEntity(data, summary=u'Add commons sitelink based on interwiki on Commons')
            #     continue
            # else:
            #     continue
        except:
            print 'Edit failed'

# EOF