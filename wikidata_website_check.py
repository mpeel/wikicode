#!/usr/bin/python
# -*- coding: utf-8  -*-
# Check if URLs exist
# Mike Peel     21-Oct-2017      v1 - start

from __future__ import unicode_literals

import pywikibot
import numpy as np
import time
import string
from pywikibot import pagegenerators
import urllib

wikidata_site = pywikibot.Site("wikidata", "wikidata")
repo = wikidata_site.data_repository()  # this is a DataSite object

query = 'select ?item ?itemLabel ?ggid where {'\
'  ?item wdt:P4141 ?ggid .'\
'  FILTER regex(?ggid, "^\\\\d+$")'\
'  SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }'\
' } order by xsd:integer(?ggid)'
print query

baseurl = 'http://www.gatehouse-gazetteer.info/'

generator = pagegenerators.WikidataSPARQLPageGenerator(query, site=wikidata_site)
for page in generator:
    print page
    item_dict = page.get()
    name = page.get()['labels']['en']
    print name
    clm_dict = item_dict["claims"]
    claim = clm_dict['P4141']
    for clm in claim:
        val = clm.getTarget()
        possible_vals = [str(val), u'Welshsites/'+str(val), u'English%20sites/'+str(val), u'Island%20sites/'+str(val)]
        for test in possible_vals:
            print urllib.urlopen(baseurl+test+'.html').getcode()
            if (urllib.urlopen(baseurl+test+'.html').getcode() == 200):
                text = urllib.urlopen(baseurl+test+'.html').read()
                print test
                print baseurl+test+'.html'
                if name in text:
                    print 'Match!'
                    print text[0:500]
                    # if (raw_input(':') == 'y'):
                    clm.changeTarget(test)
                    print clm.getTarget()
