#!/usr/bin/python
# -*- coding: utf-8  -*-
# Remove bad P373 links
# Mike Peel     17-Jun-2019      v1 - start

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

wikidata_site = pywikibot.Site("wikidata", "wikidata")
repo = wikidata_site.data_repository()  # this is a DataSite object
commons = pywikibot.Site('commons', 'commons')
debug = 1
attempts = 0
count = 0

usereport = True
candidates = []
if usereport:
    reportpage = pywikibot.Page(repo, 'Wikidata:Database reports/Constraint violations/P373')
    text = reportpage.get()
    text = text.split('== "Commons link" violations ==')[1].split('== "Conflicts with {{P|31}}" violations ==')[0]
    lines = text.splitlines()
    for line in lines:
        try:
            qid = line.split('* [[')[1].split(']]')[0]
            # print(qid)
            candidates.append(qid)
        except:
            continue
else:
    query = 'SELECT DISTINCT ?item ?itemLabel WHERE {'\
    '    ?statement wikibase:hasViolationForConstraint wds:P373-3C23B442-AC15-4E46-B58C-705E563DD015 .'\
    '    ?item ?p ?statement .'\
    '    FILTER( ?item NOT IN ( wd:Q4115189, wd:Q13406268, wd:Q15397819 ) ) .'\
    '    SERVICE wikibase:label { bd:serviceParam wikibase:language "en" } .'\
    '}'
    if debug:
        query = query + " LIMIT 10"

    print(query)

    generator = pagegenerators.WikidataSPARQLPageGenerator(query, site=wikidata_site)


# for page in generator:
for pageid in candidates:
    page = pywikibot.ItemPage(repo, pageid)
    item_dict = page.get()
    qid = page.title()
    print("\nhttp://www.wikidata.org/wiki/" + qid)
    # print(item_dict)
    try:
        p373 = item_dict['claims']['P373']
    except:
        print('No P373')
        continue
    for clm in p373:
        val = clm.getTarget()
        commonscat = u"Category:" + val
        print(commonscat)
        original = commonscat
        # First let's see if we can correct the P373 value
        commonscat = commonscat.replace('Category::','Category:')
        commonscat = commonscat.replace('Category:Category:','Category:')
        try:
            commonscat_page = pywikibot.Page(commons, commonscat)
            text = commonscat_page.get()
            if commonscat != original:
                test = 'y'
                if debug == 1:
                    print(original)
                    print(commonscat)
                    test = input("Continue? ")
                if test == 'y':
                    clm.changeTarget(commonscat.replace('Category:',''), summary=u"Correct P373")
                    nummodified += 1
                    continue
        except:
            null = 1
        print('hi1')
        try:
            tocheck = commonscat
            if 'Category:' not in tocheck:
                tocheck = 'Category:'+tocheck
            commonscat_page = pywikibot.Page(commons, tocheck)
            text = commonscat_page.get()
            print('Category exists')
            continue
        except:
            null = 0

        print('hi2')
        try:
            last_check = check_if_category_has_contents(commonscat,site=commons)
        except:
            null = 1
        if last_check == False:
            print('hi3')
            # See if we have a sitelink we can copy from
            try:
                sitelink = item_dict['sitelinks']['commonswiki']
            except:
                sitelink = ''
            if sitelink != '' and 'Category:' in sitelink:
                test = 'y'
                if debug == 1:
                    print(clm)
                    print(sitelink)
                    test = raw_input("Continue? ")
                if test == 'y':
                    clm.changeTarget(sitelink.replace('Category:',''), summary=u"Update (non-existant) P373 to match the sitelink")
                    nummodified += 1
            else:
                test = 'y'
                if debug == 1:
                    print(clm)
                    test = raw_input("Continue? ")
                if test == 'y':
                    page.removeClaims(clm, summary=u"Remove P373 to a non-existent Commons category")
                    nummodified += 1
        else: # last_check == True
            if debug == 1:
                print('Category has content')
                print('http://commons.wikimedia.org/wiki/'+commonscat.replace(" ",'_'))
                test = input("Continue? ")
                continue

        if nummodified >= maxnum:
            print('Reached the maximum of ' + str(maxnum) + ' entries modified, quitting!')
            exit()


print('Done! Edited ' + str(nummodified) + ' entries')
        
# EOF
