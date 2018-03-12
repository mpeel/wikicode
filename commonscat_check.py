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

maxnum = 10000
nummodified = 0

wikidata_site = pywikibot.Site("wikidata", "wikidata")
repo = wikidata_site.data_repository()  # this is a DataSite object
commons = pywikibot.Site('commons', 'commons')
debug = 1
query = 'SELECT ?item ?commonscat ?sitelink ?name WHERE {'\
'  ?item wdt:P373 ?commonscat.'\
'  ?sitelink schema:about ?item; schema:isPartOf <https://commons.wikimedia.org/>; schema:name ?name .'\
'  FILTER( CONTAINS(STR(?sitelink), \'Category:\') = true ) .'\
'  FILTER( ?commonscat != SUBSTR(STR(?name), 10) ) .'\
'}'
# if debug:
#     query = query + " LIMIT 100"

print query

catredirect_templates = ["category redirect", "Category redirect", "seecat", "Seecat", "see cat", "See cat", "categoryredirect", "Categoryredirect", "catredirect", "Catredirect", "cat redirect", "Cat redirect", "catredir", "Catredir", "redirect category", "Redirect category", "cat-red", "Cat-red", "redirect cat", "Redirect cat", "category Redirect", "Category Redirect", "cat-redirect", "Cat-redirect"]

generator = pagegenerators.PreloadingItemGenerator(pagegenerators.WikidataSPARQLPageGenerator(query, site=wikidata_site))
bad_commonscat_count = 0
bad_sitelink_count = 0
interwiki_conflicts = []
for page in generator:
    # item_dict = page.get()
    item_dict = page
    qid = page.title()
    print "\n" + qid
    sitelink = item_dict['sitelinks']['commonswiki']
    sitelink_redirect = ""
    commonscat_redirect = ""
    p373 = item_dict['claims']['P373']
    bad_sitelink = 0
    bad_commonscat = 0
    p373_check = 0
    for clm in p373:
        p373_check += 1
    # Only attempt to do this if there is only one value for P373
    if p373_check == 1:
        for clm in p373:
            val = clm.getTarget()
            commonscat = u"Category:" + val
            try:
                sitelink_page = pywikibot.Page(commons, sitelink)
            except:
                bad_sitelink = 1
                bad_sitelink_count += 1
                print 'Found a bad sitelink'
            else:
                for option in catredirect_templates:
                    if "{{" + option in sitelink_page.text:
                        try:
                            sitelink_redirect = (sitelink_page.text.split("{{" + option + "|"))[1].split("}}")[0]
                        except:
                            try:
                                sitelink_redirect = (sitelink_page.text.split("{{" + option + " |"))[1].split("}}")[0]
                            except:
                                print 'Wikitext parsing bug!'
                        sitelink_redirect = sitelink_redirect.replace(u":Category:","")
                        sitelink_redirect = sitelink_redirect.replace(u"Category:","")
            try:
                commonscat_page = pywikibot.Page(commons, commonscat)
            except:
                bad_commonscat = 1
                bad_commonscat_count += 1
                print 'Found a bad commonscat'
            else:
                for option in catredirect_templates:
                    if "{{" + option in commonscat_page.text:
                        try:
                            commonscat_redirect = (commonscat_page.text.split("{{" + option +"|"))[1].split("}}")[0]
                        except:
                            try:
                                commonscat_redirect = (commonscat_page.text.split("{{" + option +" |"))[1].split("}}")[0]
                            except:
                                print 'Wikitext parsing bug!'
                        commonscat_redirect = commonscat_redirect.replace(u":Category:","")
                        commonscat_redirect = commonscat_redirect.replace(u"Category:","")
            
            print sitelink + " - " + commonscat
            if (sitelink_redirect or commonscat_redirect):
                print " " + sitelink_redirect + " - " + commonscat_redirect

            # Sort out the case where one is a redirect to the other
            if (u"Category:" + sitelink_redirect) == commonscat:
                if debug:
                    print 'Would change commons sitelink to ' + sitelink_redirect
                data = {'sitelinks': [{'site': 'commonswiki', 'title': u"Category:" + sitelink_redirect}]}
                try:
                    page.editEntity(data, summary=u'Update commons sitelink to avoid commons category redirect')
                    nummodified += 1
                except:
                    interwiki_conflicts.append(qid)
            if (u"Category:" + commonscat_redirect) == sitelink:
                if debug:
                    print "Would change P373 to " + commonscat_redirect
                try:
                    clm.changeTarget(commonscat_redirect, summary=u"Update P373 to avoid commons category redirect")
                    nummodified += 1
                except:
                    print '... but there was a problem doing so!'
            # # Sort out the case where the commonscat has been moved, and one of the two hasn't been updated.
            # if bad_sitelink and bad_commonscat == 0:
            #     # We have a bad sitelink
            #     if commonscat_redirect != "":
            #         # ... but the commonscat is a redirect
            #         clm.changeTarget(commonscat_redirect, summary=u"Update P373 to avoid commons category redirect")
            #         data = {'sitelinks': [{'site': 'commonswiki', 'title': u"Category:" + commonscat_redirect}]}
            #         page.editEntity(data, summary=u'Update commons sitelink to avoid missing category')
            #         nummodified += 1
            #     else:
            #         # ... and the commonscat is good
            #         data = {'sitelinks': [{'site': 'commonswiki', 'title': u"Category:" + commonscat}]}
            #         page.editEntity(data, summary=u'Update commons sitelink to avoid missing category')
            #         nummodified += 1
            # if bad_commonscat and bad_sitelink == 0:
            #     # We have a bad commonscat
            #     if sitelink_redirect != "":
            #         # ... but the sitelink is a redirect
            #         clm.changeTarget(sitelink_redirect, summary=u"Update P373 to avoid missing commons category")
            #         data = {'sitelinks': [{'site': 'commonswiki', 'title': u"Category:" + sitelink_redirect}]}
            #         page.editEntity(data, summary=u'Update commons sitelink to avoid category redirect')
            #         nummodified += 1
            #     else:
            #         # ... and the sitelink is good
            #         data = {'sitelinks': [{'site': 'commonswiki', 'title': u"Category:" + sitelink}]}
            #         page.editEntity(data, summary=u'Update commons sitelink to avoid missing category')
            #         nummodified += 1

            if nummodified >= maxnum:
                print 'Reached the maximum of ' + str(maxnum) + ' entries modified, quitting!'
                print 'Bad commonscats: ' + str(bad_commonscat_count) + ", bad sitelinks:" + str(bad_sitelink_count)
                print 'Interwiki conflicts in: '
                print interwiki_conflicts
                exit()

print 'Done! Edited ' + str(nummodified) + ' entries'
print 'Bad commonscats: ' + str(bad_commonscat_count) + ', bad sitelinks: ' + str(bad_sitelink_count)
print 'Interwiki conflicts in: '
print interwiki_conflicts
            
# EOF