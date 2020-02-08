#!/usr/bin/python3
# -*- coding: utf-8  -*-
# Remove bad ship categories links
# Mike Peel     05-Feb-2020      v1 - start

import pywikibot
import numpy as np
from pywikibot import pagegenerators

wikidata_site = pywikibot.Site("wikidata", "wikidata")
repo = wikidata_site.data_repository()

query = "SELECT ?item ?itemlabel ?CFSN ?sitelinks {{  ?item wdt:P7782 ?CFSN .            MINUS {{ ?item wdt:P458 [] }} .  ?item wikibase:sitelinks ?sitelinks .  ?item rdfs:label ?itemlabel . FILTER(lang(?itemlabel)='en')  FILTER REGEX (?itemlabel, 'IMO')}} ORDER BY ?itemlabel"

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
    label = item_dict['labels']['en']
    print(label)

    # Make sure it's not actually a category item
    try:
        p301 = item_dict['claims']['P301']
        continue
    except:
        print('No P301')

    imo = label.replace('Category:IMO','').strip()
    print(imo)

    # Look for an item with a matching IMO number
    query2 = 'SELECT ?item WHERE { ?item wdt:P458 ?id . FILTER (?id = "'+str(imo)+'") . }'
    print(query2)
    generator2 = pagegenerators.WikidataSPARQLPageGenerator(query2, site=repo)
    count = 0
    for testpage in generator2:
        page2 = testpage
        count+=1
    print(count)
    if count != 1:
        continue
    else:
        item_dict2 = page2.get()
        qid2 = page2.title()
        print("http://www.wikidata.org/wiki/" + qid2)

    # Check for sitelinks
    try:
        sitelink = item_dict['sitelinks']['commonswiki']
    except:
        sitelink = ''
    try:
        sitelink2 = item_dict2['sitelinks']['commonswiki']
    except:
        sitelink2 = ''

    print(sitelink)
    print(sitelink2)

    # If we have two sitelinks, remove one of them
    if sitelink != '' and sitelink2 != '':
        if 'IMO' not in sitelink:
            print('Would remove the first sitelink')
        elif 'IMO' not in sitelink2:
            print('Would remove the second sitelink')
        else:
            print('Something odd here')

    run = 0
    if int(qid.replace('Q','')) < int(qid2.replace('Q','')):
        print('Would merge into item 1')
        run = 1
    else:
        print('Would merge into item 2')

    if run != 1:
        test = input('Continue?')
    else:
        test = 'y'
    if test != 'n':
        # Remove 'Category' from the first item
        new_labels = item_dict['labels']
        new_labels['en'] = new_labels['en'].replace('Category:','')
        # test = input('Remove category from label?')
        # if test != 'n':
        page.editLabels(labels=new_labels, summary="Remove misplaced 'Category' in label")

        # If we have two sitelinks, remove one of them
        if sitelink != '' and sitelink2 != '':
            if 'IMO' not in sitelink:
                # test = input('Remove first sitelink?')
                # if test != 'n':
                page.removeSitelink('commonswiki',summary=u'removing commons sitelink in preparation for merge.')
            elif 'IMO' not in sitelink2:
                # test = input('Remove second sitelink?')
                # if test != 'n':
                page2.removeSitelink('commonswiki',summary=u'removing commons sitelink in preparation for merge.')

        # Merge an item into the one with the lowest qid
        if int(qid.replace('Q','')) < int(qid2.replace('Q','')):
            # test = input('Merge into item 1?')
            # if test != 'n':
            page2.mergeInto(page,summary='Merging duplicate ship items')
        else:
            # test = input('Merge into item 2?')
            # if test != 'n':
            page.mergeInto(page2,summary='Merging duplicate ship items')

# EOF
