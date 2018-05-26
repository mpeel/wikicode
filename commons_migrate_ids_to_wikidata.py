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

maxnum = 1000
nummodified = 0

commons = pywikibot.Site('commons', 'commons')
repo = commons.data_repository()  # this is a DataSite object
debug = True
manual = False
category = 'Category:HPIP with known IDs' #'Category:Listed buildings in England with known IDs'
templates = ['HPIP']#['Listed building England', 'listed building England']
properties = ['P5094']#['P1216', 'P1216']

# category = 'Category:Listed buildings in England with known IDs'
# templates = ['Listed building England', 'listed building England']
# properties = ['P1216', 'P1216']
others = ['mainw','Mainw', 'Interwiki from Wikidata', 'interwiki from Wikidata', 'label', 'Label']
enwp = ['mainw', 'Mainw', 'on Wikipedia|en=', 'On Wikipedia|en=']
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
    for i in range(0,len(properties)):
        try:
            ID = item_dict['claims'][properties[i]]
            for clm in ID:
                if count == 0:
                    target_text = target_text.replace("{{" + templates[i] + "|" + clm.getTarget() + "}}", "")
                count += 1
        except:
            continue

    # Remove other templates
    for i in range(0,len(others)):
        target_text = target_text.replace("{{"+others[i]+"}}", "")
        target_text = target_text.replace("{{" + others[i] + "|" + wd_item.title() + "}}", "")

    try:
        enwp_link = item_dict['sitelinks']['enwiki']
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
        target_text = target_text.replace('\n\n{{Wikidata infobox','\n{{Wikidata infobox')
        target_text = target_text.replace('\n\n{{wikidata infobox','\n{{wikidata infobox')
        target_text = target_text.replace('\n\n{{Wikidata Infobox','\n{{Wikidata Infobox')
        target_text = target_text.replace('\n\n{{wikidata Infobox','\n{{wikidata Infobox')
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