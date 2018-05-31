#!/usr/bin/python
# -*- coding: utf-8  -*-
# Migrate data from Commons to Wikidata
# Started 12 May 2018 by Mike Peel
from __future__ import unicode_literals

import pywikibot
import numpy as np
import time
import string
from pywikibot import pagegenerators
import urllib

maxnum = 1000
nummodified = 0

commons = pywikibot.Site('commons', 'commons')
repo = commons.data_repository()  # this is a DataSite object
debug = True
manual = True
category = 'Category:HPIP with known IDs' #'Category:Listed buildings in England with known IDs'
templates = ['HPIP']#['Listed building England', 'listed building England']
properties = u'P5094'#['P1216', 'P1216']

def checkid(targetcat):
    print targetcat
    target_text = targetcat.get()
    # print target_text

    try:
        wd_item = pywikibot.ItemPage.fromPage(targetcat)
        item_dict = wd_item.get()
    except:
        print "No Wikidata sitelink found"
        return 0

    id_val = 0
    for i in range(0,len(templates)):
        try:
            value = (target_text.split("{{"+templates[i]+"|"))[1].split("}}")[0]
            if value and id_val == 0:
                id_val = value
            elif id_val != 0:
                print 'Found multiple IDs, aborting'
                return 0
        except:
            null = 1
            # print '1'
        try:
            value = (target_text.split("{{"+templates[i]+" |1="))[1].split("}}")[0]
            if value and id_val == 0:
                id_val = value
            elif id_val != 0:
                print 'Found multiple IDs, aborting'
                return 0
        except:
            null = 2
            # print '2'
        try:
            value = (target_text.split("{{"+templates[i]+"|1="))[1].split("}}")[0]
            if value and id_val == 0:
                id_val = value
            elif id_val != 0:
                print 'Found multiple IDs, aborting'
                return 0
        except:
            null = 3
            # print '3'
    print id_val

    query = 'SELECT ?item WHERE { ?item wdt:'+str(properties)+' ?id . FILTER (?id = "'+str(id_val)+'") . }'
    # print query
    generator = pagegenerators.WikidataSPARQLPageGenerator(query, site=repo)
    count = 0
    for testpage in generator:
        page = testpage
        count+=1
    if count == 0 and id_val != 0:
        try:
            existing_id = item_dict['claims']['P301']
            print 'P301 exists, aborting'
            return 0
        except:
            null = 0
        try:
            existing_id = item_dict['claims'][properties]
        except:
            # No existing sitelink found, add the new one
            # try:
            print "\n\n"
            print wd_item.title()
            print id_val
            print item_dict['labels']
            stringclaim = pywikibot.Claim(repo, properties)
            stringclaim.setTarget(id_val)
            print stringclaim
            # text = raw_input("Save? ")
            # if text == 'y':
            wd_item.addClaim(stringclaim, summary=u'Copying ID value from Commons')
            return 1
            # else:
            #     return 0
            # except:
            #     print 'Edit failed'
            #     return 0

        return 0

    return 0



# Start the category walker
cat = pywikibot.Category(commons,category)
# nummodified += checkid(cat)
targetcats = pagegenerators.SubCategoriesPageGenerator(cat, recurse=False);

for targetcat in targetcats:
    # print targetcat
    # print "\n" + targetcat.title()
    # print target.text
    nummodified += checkid(targetcat)

    if nummodified >= maxnum:
        print 'Reached the maximum of ' + str(maxnum) + ' entries modified, quitting!'
        exit()

print 'Done! Edited ' + str(nummodified) + ' entries'
                
# EOF