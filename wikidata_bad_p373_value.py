#!/usr/bin/python3
# -*- coding: utf-8  -*-
# Remove P373 values
# Mike Peel     05-Feb-2020      v1 - start

import pywikibot
import numpy as np
from pywikibot import pagegenerators

wikidata_site = pywikibot.Site("wikidata", "wikidata")
repo = wikidata_site.data_repository()

query = "SELECT DISTINCT ?item ?itemLabel WHERE {{     ?statement wikibase:hasViolationForConstraint wds:P373-B6CB2058-B6B7-4E4D-98D3-ED2C4F3D7184 .     ?item ?p ?statement .     FILTER( ?item NOT IN ( wd:Q4115189, wd:Q13406268, wd:Q15397819 ) ) . }}"

print(query)

generator = pagegenerators.WikidataSPARQLPageGenerator(query, site=wikidata_site)

for page in generator:

    # Get the target item
    print('\n\n')
    try:
        item_dict = page.get()
    except:
        continue
    qid = page.title()
    print("\nhttp://www.wikidata.org/wiki/" + qid)

    try:
        sitelink = item_dict['sitelinks']['commonswiki']
        print('http://commons.wikimedia.org/wiki/'+sitelink)
    except:
        print('No sitelink')
        continue

    p373 = item_dict['claims']['P373']
    for clm in p373:
        val = clm.getTarget()
        p373cat = u"Category:" + val
        if p373cat != sitelink:
            print('Remove P373?')
            print(' http://www.wikidata.org/wiki/'+qid)
            print('http://commons.wikimedia.org/wiki/' + str(p373cat))
            savemessage = "Remove P373 value that doesn't match the sitelink"
            # print(savemessage)
            page.removeClaims(clm,summary=savemessage)

# EOF