#!/usr/bin/python
# -*- coding: utf-8  -*-
# Fill in database with categories needing images
# Mike Peel     09-Nov-2018      v1

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
import mysql.connector

maxnum = 10
usetemplate = 0
usecategory = 1
wikidata_site = pywikibot.Site("wikidata", "wikidata")
repo = wikidata_site.data_repository()  # this is a DataSite object
commons = pywikibot.Site('commons', 'commons')

mydb = mysql.connector.connect(
  host="mysql.mikepeel.net",
  user="mikepeel_commons",
  passwd="c0mm0nscandidates",
  database="mikepeel_commonscat2"
)
mycursor = mydb.cursor()

def runimport(targetcat):
    print targetcat.title()
    # Make sure we have a Wikidata entry
    try:
        wd_item = pywikibot.ItemPage.fromPage(targetcat)
        item_dict = wd_item.get()
        print wd_item.title()
    except:
        print 'No existing link'
        return 0

    # Check for P910
    try:
        existing_id = item_dict['claims']['P301']
        print 'P301 exists, following that.'
        for clm2 in existing_id:
            wd_item = clm2.getTarget()
            item_dict = wd_item.get()
    except:
        null = 0

    # Make sure we don't already have an image
    skip = 0
    try:
        p18 = item_dict['claims']['P18']
        return 0
    except:
        null = 0

    # No existing image, add it to the database as a possibility
    mycursor.execute('SELECT * FROM image_candidates WHERE category = "' + targetcat.title() + '"')
    myresult = mycursor.fetchone()
    print myresult
    if not myresult:
        sql = 'INSERT INTO image_candidates (category, done, decision) VALUES ("' + targetcat.title() + '", 0, 0)'
        mycursor.execute(sql)
        mydb.commit()
        return 0
    return 0

nummodified = 0
if usetemplate:
    templates = ['South African Heritage Site']
    template = pywikibot.Page(commons, 'Template:'+templates[0])
    targetcats = template.embeddedin(namespaces='14')

    for targetcat in targetcats:
        print targetcat.title()
        runimport(targetcat)
elif usecategory:
    targetcats = ['Category:Uses of Wikidata Infobox with no image']
    numchecked = 0
    catschecked = 0
    i = 0
    seen   = set(targetcats)
    active = set(targetcats)

    while active:
        i+=1
        next_active = set()
        for item in active:
            cat = pywikibot.Category(commons,item)
            nummodified += runimport(cat)
            numchecked += 1
            print str(nummodified) + " - " + str(numchecked) + "/" + str(len(seen)) + "/" + str(len(active)) + "/" + str(len(next_active))

            if i == 1:
                for result in pagegenerators.SubCategoriesPageGenerator(cat, recurse=False):
                    if result.title() not in seen:
                        seen.add(result.title())
                        next_active.add(result.title())

        active = next_active
        if nummodified >= maxnum:
            print 'Reached the maximum of ' + str(maxnum) + ' entries modified, quitting!'
            break
else:
    # Pick random categories
    while nummodified < maxnum:
        targets = pagegenerators.RandomPageGenerator(total=100, site=commons, namespaces='14')
        for target in targets:
            print target.title()
            nummodified += runimport(target)
            
            if nummodified >= maxnum:
                print 'Reached the maximum of ' + str(maxnum) + ' entries modified, quitting!'
                break

# EOF