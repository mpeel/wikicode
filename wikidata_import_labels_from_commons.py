#!/usr/bin/python
# -*- coding: utf-8  -*-
# Move commons category sitelinks to category items where needed
# Mike Peel     10-Jun-2018      v1

from __future__ import unicode_literals

import pywikibot
import numpy as np
import time
import string
from pywikibot import pagegenerators
import urllib

maxnum = 10000
nummodified = 0
stepsize =  10000
maximum = 2000000
numsteps = int(maximum / stepsize)

wikidata_site = pywikibot.Site("wikidata", "wikidata")
repo = wikidata_site.data_repository()  # this is a DataSite object
commons = pywikibot.Site('commons', 'commons')

for i in range(0,numsteps):
    print 'Starting at ' + str(i*stepsize)

    query = "SELECT ?item\n"\
    "WITH { \n"\
    "  SELECT ?item ?categoryitem WHERE {\n"\
    "    ?item wdt:P373 ?categoryitem . \n"\
    '  } LIMIT '+str(stepsize)+' OFFSET '+str(i*stepsize)+'\n'\
    "} AS %items\n"\
    "WHERE {\n"\
    "  INCLUDE %items .\n"\
    "    SERVICE wikibase:label { bd:serviceParam wikibase:language \"nl,fr,en,de,it,es,no,pt\". }\n"\
    "    FILTER(NOT EXISTS {\n"\
    "        ?item rdfs:label ?lang_label.\n"\
    "        FILTER(LANG(?lang_label) = \"en\")\n"\
    "    })\n"\
    "}"

    print query

    generator = pagegenerators.WikidataSPARQLPageGenerator(query, site=wikidata_site)
    for page in generator:
        # Get the page
        item_dict = page.get()
        qid = page.title()
        print "\n" + qid

        # Check that it hasn't already got an en label
        try:
            label = item_dict['labels']['en']
            print label
            print "That shouldn't have worked, continuing"
            continue
        except:
            print 'No English label'

        # Get the value for P373
        try:
            p373 = item_dict['claims']['P373']
        except:
            print 'No P373 value found!'
            continue
        p373_check = 0
        for clm in p373:
            p373_check += 1
        # Only attempt to do this if there is only one value for P373
        if p373_check != 1:
            print 'More than one P373 value found! Skipping...'

        # Make sure that we have a sitelink, and that it's the same as P373
        try:
            sitelink = item_dict['sitelinks']['commonswiki']
            sitelink = sitelink.replace('Category:','')
        except:
            print 'No sitelink'
            continue

        # Check to see if we're looking at a category item
        catitem = 0
        try:
            p31 = item_dict['claims']['P31']
            print p31
            for clm in p31:
                if 'Q4167836' in clm.getTarget().title():
                    catitem = 1
        except:
            print 'No P31 in target'

        for clm in p373:
            new_label = clm.getTarget()
            if sitelink != new_label:
                print "Sitelink and P373 don't match, skipping"
                continue
            if catitem:
                new_label = 'Category:' + new_label

            # if we don't have an English language label, add it.
            try:
                label = val.labels['en']
                print label
            except:
                try:
                    page.editLabels(labels={'en': new_label}, summary=u'Add en label to match Commons category name')
                    nummodified += 1
                except:
                    print 'Unable to save label edit on Wikidata!'

            if nummodified >= maxnum:
                print 'Reached the maximum of ' + str(maxnum) + ' entries modified, quitting!'
                exit()

    print 'Done! Edited ' + str(nummodified) + ' entries'
         
# EOF