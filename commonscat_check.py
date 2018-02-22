#!/usr/bin/python
# -*- coding: utf-8  -*-
# Check for consistency in commons category usage
# Mike Peel     08-Feb-2018      v1 - start

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
query = 'SELECT ?item ?commonscat ?sitelink ?name WHERE {'\
'  ?item wdt:P373 ?commonscat.'\
'  ?sitelink schema:about ?item; schema:isPartOf <https://commons.wikimedia.org/>; schema:name ?name .'\
'  FILTER( CONTAINS(STR(?sitelink), \'Category:\') = true ) .'\
'  FILTER( ?commonscat != SUBSTR(STR(?name), 10) ) .'\
'}'
if debug:
    query = query + " LIMIT 10"
print query

catredirect_templates = ["category redirect", "Category redirect", "seecat", "Seecat", "see cat", "See cat", "categoryredirect", "Categoryredirect", "catredirect", "Catredirect", "cat redirect", "Cat redirect", "catredir", "Catredir", "redirect category", "Redirect category", "cat-red", "Cat-red", "redirect cat", "Redirect cat", "category Redirect", "Category Redirect", "cat-redirect", "Cat-redirect"]

generator = pagegenerators.WikidataSPARQLPageGenerator(query, site=wikidata_site)
for page in generator:
    item_dict = page.get()
    sitelink = item_dict['sitelinks']['commonswiki']
    sitelink_redirect = ""
    commonscat_redirect = ""
    p373 = item_dict['claims']['P373']
    for clm in p373:
        val = clm.getTarget()
        commonscat = u"Category:" + val
        sitelink_page = pywikibot.Page(commons, sitelink)
        for option in catredirect_templates:
            if "{{" + option in sitelink_page.text:
                sitelink_redirect = (sitelink_page.text.split("{{" + option + "|"))[1].split("}}")[0]
                sitelink_redirect = sitelink_redirect.replace(u":Category:","")
                sitelink_redirect = sitelink_redirect.replace(u"Category:","")
        commonscat_page = pywikibot.Page(commons, commonscat)
        for option in catredirect_templates:
            if "{{" + option in commonscat_page.text:
                commonscat_redirect = (commonscat_page.text.split("{{" + option +"|"))[1].split("}}")[0]
                commonscat_redirect = commonscat_redirect.replace(u":Category:","")
                commonscat_redirect = commonscat_redirect.replace(u"Category:","")

        if debug:
            print sitelink + " - " + commonscat
        if debug and (sitelink_redirect or commonscat_redirect):
            print " " + sitelink_redirect + " - " + commonscat_redirect
        if (u"Category:" + sitelink_redirect) == commonscat:
            if debug:
                print 'Would change commons sitelink to ' + sitelink_redirect
            data = {'sitelinks': [{'site': 'commonswiki', 'title': u"Category:" + sitelink_redirect}]}
            page.editEntity(data, summary=u'Update commons sitelink to avoid commons category redirect')
        if (u"Category:" + commonscat_redirect) == sitelink:
            if debug:
                print "Would change P373 to " + commonscat_redirect
            clm.changeTarget(commonscat_redirect, summary=u"Update P373 to avoid commons category redirect")
        
# EOF