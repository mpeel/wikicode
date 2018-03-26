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

maxnum = 10
nummodified = 0

wikidata_site = pywikibot.Site("wikidata", "wikidata")
repo = wikidata_site.data_repository()  # this is a DataSite object
commons = pywikibot.Site('commons', 'commons')
debug = 1
query = 'SELECT ?item ?commonscat ?commonspage\n'\
'WITH {\n'\
'   SELECT ?item ?commonscat WHERE {\n'\
'       ?item wdt:P373 ?commonscat .\n'\
'  } LIMIT 10000\n'\
'} AS %cats \n'\
'WHERE {'\
'    hint:Query hint:optimizer "None".'\
'    INCLUDE %cats .'\
'    BIND(STRLANG(CONCAT("Category:", ?commonscat),"en") AS ?c1) .'\
'    OPTIONAL {'\
'         ?commonspage schema:name ?c1 .'\
'         ?commonspage schema:isPartOf <https://commons.wikimedia.org/> .'\
'         ?commonspage schema:about [] .'\
'    }'\
'    FILTER (!bound(?commonspage)) '\
'    FILTER NOT EXISTS {?item wdt:P31 wd:Q4167836}'\
'    OPTIONAL {'\
'        ?item2 wdt:P373 ?commonscat .'\
'        ?item2 wdt:P31 wd:Q4167836'\
'    }'\
'    FILTER NOT EXISTS {'\
'        ?item3 wdt:P373 ?commonscat .'\
'        FILTER (?item3 != ?item) .'\
'        FILTER (!(bound(?item2) && ?item3 = ?item2))'\
'    }'\
'}'
#'LIMIT 10000'

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
                        print val
                        text = raw_input("Save? ")
                        if text == 'y':
                            page.editEntity(data, summary=u'Copy from P373 to commons sitelink')
                            nummodified += 1
                    except:
                        print 'Edit failed'

            if nummodified >= maxnum:
                print 'Reached the maximum of ' + str(maxnum) + ' entries modified, quitting!'
                exit()

print 'Done! Edited ' + str(nummodified) + ' entries'
            
# EOF