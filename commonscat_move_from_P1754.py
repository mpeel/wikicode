#!/usr/bin/python
# -*- coding: utf-8  -*-
# Move commons category sitelinks to category items where needed
# Mike Peel     10-Jun-2018      v1
# Mike Peel     13-Jul-2019      v2 - use P1754/P1753 rather than P910/P301

from __future__ import unicode_literals

import pywikibot
import numpy as np
import time
import string
from pywikibot import pagegenerators
import urllib
import time

maxnum = 1000
nummodified = 0
stepsize =  10000
maximum = 2000000
numsteps = int(maximum / stepsize)

wikidata_site = pywikibot.Site("wikidata", "wikidata")
repo = wikidata_site.data_repository()  # this is a DataSite object
commons = pywikibot.Site('commons', 'commons')
debug = 1
# query = 'SELECT ?item ?categoryitem ?commonscategory WHERE { ?item wdt:P1754 ?categoryitem . ?commonscategory schema:about ?item . ?commonscategory schema:isPartOf <https://commons.wikimedia.org/> . FILTER REGEX(STR(?commonscategory), "https://commons.wikimedia.org/wiki/Category:") . }'
# if debug:
#     query = query + " LIMIT 1000"
for i in range(0,numsteps):
    print('Starting at ' + str(i*stepsize))

    query = 'SELECT ?item ?categoryitem ?commonscategory\n'\
        'WITH { \n'\
        '  SELECT ?item ?categoryitem WHERE {\n'\
        '    ?item wdt:P1754 ?categoryitem . \n'\
        '  } LIMIT '+str(stepsize)+' OFFSET '+str(i*stepsize)+'\n'\
        '} AS %items\n'\
        'WHERE {\n'\
        '  INCLUDE %items .\n'\
        '  ?commonscategory schema:about ?item . \n'\
        '  ?commonscategory schema:isPartOf <https://commons.wikimedia.org/> . \n'\
        '  FILTER (STRSTARTS(STR(?commonscategory), "https://commons.wikimedia.org/wiki/Category:")) . \n'\
        '}'

    print(query)

    generator = pagegenerators.WikidataSPARQLPageGenerator(query, site=wikidata_site)
    bad_commonscat_count = 0
    bad_sitelink_count = 0
    interwiki_conflicts = []
    for page in generator:
        # Get the page
        item_dict = page.get()
        qid = page.title()
        print("\n" + qid)
        try:
            sitelink = item_dict['sitelinks']['commonswiki']
            print(sitelink)
        except:
            print('No sitelink found in main item! Skipping!')
            continue
        # Get the value for P1754
        try:
            P1754 = item_dict['claims']['P1754']
        except:
            print('No P1754 value found!')
            continue

        P1754_check = 0
        for clm in P1754:
            P1754_check += 1
        # Only attempt to do this if there is only one value for P1754
        if P1754_check != 1:
            print('More than one P1754 value found! Skipping...')
            continue

        for clm in P1754:
            try:
                val = clm.getTarget()
                wd_id = val.title()
                target_dict = val.get()
            except:
                print('Unable to get target!')
                continue
            print(wd_id)

            try:
                p31 = target_dict['claims']['P31']
                print(p31)
            except:
                print('No P31 in target - skipping!')
                continue
            test_p31 = 0
            for clm in p31:
                if 'Q4167836' in clm.getTarget().title():
                    test_p31 = 1
            if test_p31 != 1:
                print('Target is not a category item - skipping!')
                continue
                
            try:
                sitelink = target_dict['sitelinks']['commonswiki']
                print(sitelink)
                print('We have a sitelink in the target! Skipping...')
                continue
            except:
                null = 1

            # Do we have the correct value for P1753?
            try:
                P1753 = target_dict['claims']['P1753']
            except:
                print('No P1753 value found!')
                continue
            P1753_check = 0
            retarget = 0
            for clm2 in P1753:
                P1753_check += 1
            # Only attempt to do this if there is only one value for P1754
            if P1753_check != 1:
                print('More than one P1753 value found! Skipping...')
            for clm2 in P1753:
                retarget = clm2.getTarget().title()
            print(retarget)

            if retarget != qid:
                print("P1754 and P1753 don't match! Skipping!")
                continue

            # Remove it from the current entry and add it to the new entry
            data = {'sitelinks': [{'site': 'commonswiki', 'title': sitelink}]}
            try:
                print(data)
                text = 'y'
                # text = input("Save? ")
                if text == 'y':
                    print('Saving!')
                    page.removeSitelink(site='commonswiki', summary=u'Moving commons category sitelink to category item (' + str(wd_id) + ')')
                    time.sleep(5)
                    val.editEntity(data, summary=u'Moving commons category sitelink from list item (' + str(qid) + ')')
                    nummodified += 1
            except:
                print('Edit failed!')

            # Bonus: if we don't have an English language label, add it.
            try:
                label = val.labels['en']
                print(label)
            except:
                text = 'y'
                # text = input("Save? ")
                if text == 'y':
                    try:
                        val.editLabels(labels={'en': sitelink}, summary=u'Add en label to match Commons sitelink')
                    except:
                        print('Unable to save label edit on Wikidata!')

            if nummodified >= maxnum:
                print('Reached the maximum of ' + str(maxnum) + ' entries modified, quitting!')
                exit()

    print('Done! Edited ' + str(nummodified) + ' entries')
         
    # EOF
