#!/usr/bin/python
# -*- coding: utf-8  -*-
# Check for consistency in commons category usage
# Mike Peel     22-Feb-2018      v1 - start

from __future__ import unicode_literals

import pywikibot
import numpy as np
import time
import string
from pywikibot import pagegenerators
import urllib

wikidata_site = pywikibot.Site("wikidata", "wikidata")
repo = wikidata_site.data_repository()  # this is a DataSite object
commons = pywikibot.Site('commons', 'commons')
debug = 0

# Brazil
collections = ['Q82941','Q510993','Q1954370','Q371803','Q2095209']

for coll in collections:
    query = 'SELECT ?item ?picture WHERE { ?item wdt:P195 wd:' + coll + ' . ?item wdt:P31 wd:Q3305213 . ?item wdt:P18 ?picture }'
    if debug:
        query = query + " LIMIT 10"
    print query

    generator = pagegenerators.WikidataSPARQLPageGenerator(query, site=wikidata_site)
    for page in generator:
        print page
        item_dict = page.get()
        qid = page.title()
        try:
            p18 = item_dict['claims']['P18']
        except:
            continue
        for clm in p18:
            val = clm.getTarget()
            print val.text
            if "{{Artwork" in val.text or "{{artwork" in val.text:
                if not (("wikidata=") in val.text.replace(" ", "").replace("   ", "") or ("Wikidata=") in val.text.replace(" ", "").replace("   ", "")):
                    print "Not present!"
                    val.text = val.text.replace("{{Artwork", "{{Artwork\n| wikidata = " + qid).replace("{{artwork", "{{Artwork\n| wikidata = " + qid)
                    print val.text
                    text = raw_input("Update on Commons? ")
                    if text == 'y':
                        val.save(u'Adding wikidata QID to artwork template based on usage in that item')

# EOF