#!/usr/bin/python
# -*- coding: utf-8  -*-
# Migrate data from Commons to Wikidata
# Started 11 May 2018 by Mike Peel
from __future__ import unicode_literals

import pywikibot
import numpy as np
import time
import string
from pywikibot import pagegenerators
import urllib
from pibot_functions import *

maxnum = 1000
nummodified = 0

commons = pywikibot.Site('commons', 'commons')
repo = commons.data_repository()  # this is a DataSite object
debug = True
manual = True
category = 'Category:Molly Quinn'
templates = ['PeopleByName', 'peopleByName']
savemessage="Trim information provided through the Wikidata Infobox"
wikidatainfobox = ["Wikidata Infobox", "Wikidata infobox", "wikidata infobox", "wikidata Infobox", "Infobox Wikidata", "infobox Wikidata", "infobox wikidata", "Infobox wikidata"]

def migratecat(targetcat):
    print targetcat
    target_text = targetcat.get()
    print target_text
    # Check that we have a Wikidata infobox here
    if not any(option in target_text for option in wikidatainfobox):
        print 'No infobox'
        return 0

    # Fetch the info from Wikidata
    try:
        wd_item = pywikibot.ItemPage.fromPage(targetcat)
        item_dict = wd_item.get()
        print wd_item.title()
    except:
        print 'No Wikidata ID'
        return 0

    # Look for replacements
    count = 0
    for i in range(0,len(templates)):
        # try:
        # template = '{{'+templates[i]+"|"+item_dict['claims']['P734']+"|"+item_dict['claims']['P735']
        print item_dict['claims']['P21']
        exit()
            # if item_dict['claims']['P21'] = 'Female':
                # target_text = target_text.replace("{{" + templates[i] + "|" + clm.getTarget() + "}}", "")
                # count += 1
        # except:
        #     continue

    # Remove other templates
    for i in range(0,len(others)):
        target_text = target_text.replace(others[i], "")

    try:
        enwp_link = get_sitelink_title(item_dict['sitelinks']['enwiki'])
        enwp_link2 = enwp_link[0].lower() + enwp_link[1:]
        for i in range(0,len(enwp)):
            target_text = target_text.replace("{{"+enwp[i]+"|"+enwp_link+"}}", "")
            target_text = target_text.replace("{{"+enwp[i]+"|"+enwp_link2+"}}", "")
    except:
        null = 1

    # We should now not be able to find the original template here - but if we can, don't edit it.
    if any(option in target_text for option in templates):
        return 0

    # Only remove whitespace if we're making another change
    if (target_text != targetcat.get()):
        target_text = target_text.replace('\n\n\n','\n')
        target_text = target_text.replace('\n\n\n','\n')
        # target_text = target_text.replace('\n\n','\n')

    # Time to save it
    if (target_text != targetcat.get()):
        targetcat.text = target_text.strip()
        print targetcat.text
        if manual:
            text = raw_input("Save on Commons? ")
            if text == 'y':
                try:
                    targetcat.save(savemessage)
                    return 1
                except:
                    print "That didn't work!"
                    return 0
            else:
                return 0
        else:
            try:
                targetcat.save(savemessage)
                return 1
            except:
                print "That didn't work!"
                return 0
    else:
        return 0

# Start the category walker
cat = pywikibot.Category(commons,category)
nummodified += migratecat(cat)
targetcats = pagegenerators.SubCategoriesPageGenerator(cat, recurse=False);

for targetcat in targetcats:
    print targetcat
    print "\n" + targetcat.title()
    # print target.text
    nummodified += migratecat(targetcat)

    if nummodified >= maxnum:
        print 'Reached the maximum of ' + str(maxnum) + ' entries modified, quitting!'
        exit()

print 'Done! Edited ' + str(nummodified) + ' entries'
                
# EOF