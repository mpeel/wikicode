#!/usr/bin/python
# -*- coding: utf-8  -*-
# Try to auto-populate family names
# Mike Peel     09-Jun-2018      v1 - start

from __future__ import unicode_literals

import pywikibot
import numpy as np
import time
import string
from pywikibot import pagegenerators
import urllib
import csv

maxnum = 1000000
nummodified = 0
stepsize =  10000
maximum = 10000000
numsteps = int(maximum / stepsize)

wikidata_site = pywikibot.Site("wikidata", "wikidata")
repo = wikidata_site.data_repository()  # this is a DataSite object
commons = pywikibot.Site('commons', 'commons')
debug = 1

# Read in the family names database
with open('populate_family_names_cache.csv', mode='r') as infile:
    reader = csv.reader(infile)
    with open('coors_new.csv', mode='w') as outfile:
        writer = csv.writer(outfile)
        names = {rows[1]:rows[0] for rows in reader}
# print names

for i in range(0,numsteps):
    print 'Starting at ' + str(i*stepsize)

    # query = 'SELECT ?item WHERE {\n'\
    # '  ?item wdt:P31 wd:Q5 .\n'\
    # '  ?item wdt:P735 ?givenname .\n'\
    # '  MINUS {?item wdt:P734 ?familyname.}\n'\
    # '}  LIMIT ' + str(stepsize) + ' OFFSET ' + str(i*stepsize)

    query = 'SELECT ?item\n'\
    'WITH {\n'\
    '   SELECT ?item WHERE {\n'\
    '       ?item wdt:P31 wd:Q5 .\n'\
    '  }  LIMIT ' + str(stepsize) + ' OFFSET ' + str(i*stepsize) + '\n'\
    '} AS %humans \n'\
    'WHERE {\n'\
    '    INCLUDE %humans .\n'\
    '    FILTER EXISTS {?item wdt:P735 ?givenname.}.\n'\
    '    MINUS {?item wdt:P734 ?familyname.}\n'\
    '}'
    print query
    exit()
    generator = pagegenerators.WikidataSPARQLPageGenerator(query, site=wikidata_site)
    for page in generator:
        try:
            item_dict = page.get()
            qid = page.title()
        except:
            print 'Huh - no page found'
            continue
        print "\n" + qid
        try:
            name = page.labels['en']
        except:
            print 'Name not found!'
            continue

        try:
            givenname_item = item_dict['claims']['P735']
            count = 0
            for clm in givenname_item:
                if count == 0:
                    val = clm.getTarget()
                    print val
                    name_dict = val.get()
                    givenname = name_dict['labels']['en']
                    count += 1
        except:
            print 'Given name not found!'
            continue

        try:
            familyname_item = item_dict['claims']['P734']
            print "Hmm, that shouldn't have worked!"
            continue
        except:
            null = 0

        print name
        print givenname
        if givenname in name:
            familyname_attempt = name.replace(givenname, "").strip()
            if familyname_attempt != "" and familyname_attempt == familyname_attempt.replace(" ", ""):
                print familyname_attempt
                try:
                    new_qid = names[familyname_attempt]
                except:
                    print 'Family name not found!'
                    continue
                if len(familyname_attempt) < 4:
                    print 'Name too short - not attempting this one!'
                    continue
                if "Saint" in familyname_attempt:
                    print "Avoiding Saint"
                    continue

                print new_qid
                stringclaim = pywikibot.Claim(repo, 'P734')
                stringclaim.setTarget(pywikibot.ItemPage(repo, new_qid))
                print stringclaim
                # text = raw_input("Save? ")
                # if text == 'y':
                try:
                    page.addClaim(stringclaim, summary=u'Adding family name based on the label minus P735')
                except:
                    print "That didn't work!"
                nummodified += 1
                print nummodified
            else:
                continue
        else:
            print 'Given name is not in family name! Continuing...'
            continue

        if nummodified >= maxnum:
            print 'Reached the maximum of ' + str(maxnum) + ' entries modified, quitting!'
            exit()

print 'Done! Edited ' + str(nummodified) + ' entries'
            
# EOF
