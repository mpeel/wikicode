#!/usr/bin/python
# -*- coding: utf-8  -*-
# Check for consistency in commons category usage
# Mike Peel     01-Mar-2018      v1 - start

from __future__ import unicode_literals

import pywikibot
import numpy as np
import time
import string
from pywikibot import pagegenerators
import urllib

maxnum = 50
nummodified = 0
stepsize =  10000
maximum = 2000000
numsteps = int(maximum / stepsize)

wikidata_site = pywikibot.Site("wikidata", "wikidata")
repo = wikidata_site.data_repository()  # this is a DataSite object
commons = pywikibot.Site('commons', 'commons')
debug = 1
for i in range(0,numsteps):
    print 'Starting at ' + str(i*stepsize)

    # '  }  LIMIT ' + str(stepsize) + ' OFFSET ' + str(i*stepsize) + '\n'\
    query = 'SELECT ?item\n'\
    'WITH {\n'\
    '   SELECT ?item ?commonscat WHERE {\n'\
    '       ?item wdt:P373 ?commonscat .\n'\
    '  }  LIMIT 15 OFFSET ' + str(i*stepsize) + '\n'\
    '} AS %cats \n'\
    'WHERE {\n'\
    '    hint:Query hint:optimizer "None".\n'\
    '    INCLUDE %cats .\n'\
    '    BIND(STRLANG(CONCAT("Category:", ?commonscat),"en") AS ?c1) .\n'\
    '    OPTIONAL {\n'\
    '         ?commonspage schema:name ?c1 .\n'\
    '         ?commonspage schema:isPartOf <https://commons.wikimedia.org/> .\n'\
    '         ?commonspage schema:about [] .\n'\
    '    }\n'\
    '    FILTER (!bound(?commonspage)) \n'\
    '    MINUS {?item wdt:P31 wd:Q4167836}\n'\
    '    MINUS {?item wdt:P31 wd:Q4167410}\n'\
    '    OPTIONAL {\n'\
    '        ?item2 wdt:P373 ?commonscat .\n'\
    '        ?item2 wdt:P31 wd:Q4167836\n'\
    '    }\n'\
    '    FILTER NOT EXISTS {\n'\
    '        ?item3 wdt:P373 ?commonscat .\n'\
    '        FILTER (?item3 != ?item) .\n'\
    '        FILTER (!(bound(?item2) && ?item3 = ?item2))\n'\
    '    }\n'\
    '    MINUS {?commonslink schema:about ?item . ?commonslink schema:isPartOf <https://commons.wikimedia.org/> . } \n'\
    '    MINUS {?item wdt:P910 [] }\n'\
    '}'

    print query

    generator = pagegenerators.WikidataSPARQLPageGenerator(query, site=wikidata_site)
    for page in generator:
        item_dict = page.get()
        qid = page.title()
        print "\n" + qid
        print page.labels
        p373 = item_dict['claims']['P373']
        p373_check = 0
        for clm in p373:
            p373_check += 1
        try:
            sitelink = item_dict['sitelinks']['commonswiki']
            sitelink_check = 1
        except:
            sitelink_check = 0
        # Only attempt to do this if there is only one value for P373 and no existing sitelink
        if p373_check == 1 and sitelink_check == 0:
            for clm in p373:
                val = clm.getTarget()
                commonscat = u"Category:" + val
                # The commons category must already exist
                try:
                    sitelink_page = pywikibot.Page(commons, commonscat)
                except:
                    print 'Found a bad sitelink'
                    # clm.changeTarget("", summary=u"Remove non-functional value of P373")
                else:
                    # Check the category to see if it already has a Wikidata item
                    commonscat_page = pywikibot.Page(commons, commonscat)
                    try:
                        wd_item = pywikibot.ItemPage.fromPage(commonscat_page)
                        wd_item.get()
                    except:
                        # That didn't work, add it to the Wikidata entry
                        data = {'sitelinks': [{'site': 'commonswiki', 'title': u"Category:" + val}]}
                        try:
                            # print val
                            # text = raw_input("Save? ")
                            # if text == 'y':
                            page.editEntity(data, summary=u'Copy from P373 to commons sitelink')
                            nummodified += 1
                        except:
                            print 'Edit failed'

                if nummodified >= maxnum:
                    print 'Reached the maximum of ' + str(maxnum) + ' entries modified, quitting!'
                    exit()

print 'Done! Edited ' + str(nummodified) + ' entries'
            
# EOF