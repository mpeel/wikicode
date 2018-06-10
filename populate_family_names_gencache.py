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
from pywikibot.data.sparql import SparqlQuery
import codecs
stepsize =  1000
maximum = 500000
numsteps = int(maximum / stepsize)
outputfile = codecs.open('populate_family_names_cache.csv', "w", "utf-8")
wikidata_site = pywikibot.Site("wikidata", "wikidata")
repo = wikidata_site.data_repository()  # this is a DataSite object
commons = pywikibot.Site('commons', 'commons')
debug = 1
for i in range(0,numsteps):
    print 'Starting at ' + str(i*stepsize)

    query = 'SELECT ?item ?itemLabel WHERE {\n'\
    '  ?item wdt:P31 wd:Q101352 .\n'\
    'SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". } . \n'\
    '}  LIMIT ' + str(stepsize) + ' OFFSET ' + str(i*stepsize)
    print query

    sq = SparqlQuery()
    queryresult = sq.query(query)
    for resultitem in queryresult['results']['bindings']:
        print resultitem['item']['value'].replace('http://www.wikidata.org/entity/','') + ', ' + resultitem['itemLabel']['value']
        outputfile.write(resultitem['item']['value'].replace('http://www.wikidata.org/entity/','') + ',' + resultitem['itemLabel']['value']+"\n")

outputfile.close()
print 'Done!'
            
# EOF