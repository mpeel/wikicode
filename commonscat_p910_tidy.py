#!/usr/bin/python
# -*- coding: utf-8  -*-
# Check for cases where there is a commons sitelink and a P910 value also with a sitelink,
# to see if one redirects to the other
# Mike Peel     18-May-2019      v1 - start

from __future__ import unicode_literals

import pywikibot
import numpy as np
import time
import string
from pywikibot import pagegenerators
import urllib

maxnum = 10000
nummodified = 0
debug = False

catredirect_templates = ["category redirect", "Category redirect", "seecat", "Seecat", "see cat", "See cat", "categoryredirect", "Categoryredirect", "catredirect", "Catredirect", "cat redirect", "Cat redirect", "catredir", "Catredir", "redirect category", "Redirect category", "cat-red", "Cat-red", "redirect cat", "Redirect cat", "category Redirect", "Category Redirect", "cat-redirect", "Cat-redirect"]

wikidata_site = pywikibot.Site("wikidata", "wikidata")
repo = wikidata_site.data_repository()  # this is a DataSite object
commons = pywikibot.Site('commons', 'commons')

def get_commons_redirect_target(category):
    redirect = ""
    try:
        sitelink_page = pywikibot.Page(commons, category)
    except:
        return redirect

    for option in catredirect_templates:
        if "{{" + option in sitelink_page.text:
            try:
                redirect = (sitelink_page.text.split("{{" + option + "|"))[1].split("}}")[0]
            except:
                try:
                    redirect = (sitelink_page.text.split("{{" + option + " |"))[1].split("}}")[0]
                except:
                    print 'Wikitext parsing bug!'
            redirect = redirect.replace(u":Category:","")
            redirect = redirect.replace(u"Category:","")
    return redirect


maxnum = 10000
step = 100
num = maxnum/step
for i in range(0,num):
    query = 'SELECT ?item ?categoryitem ?commonscategory WHERE {'\
    '  ?item wdt:P910 ?categoryitem .'\
    '  ?commonscategory schema:about ?item .'\
    '  ?commonscategory schema:isPartOf <https://commons.wikimedia.org/> .'\
    '  FILTER REGEX(STR(?commonscategory), "https://commons.wikimedia.org/wiki/Category:") .'\
    '  } LIMIT ' + str(step) + ' OFFSET ' + str(i*step)
    print query

    generator = pagegenerators.WikidataSPARQLPageGenerator(query, site=wikidata_site)
    bad_commonscat_count = 0
    bad_sitelink_count = 0
    interwiki_conflicts = []
    for page in generator:
        # Get the info about the topic item
        item_dict = page.get()
        qid = page.title()
        print "\n" + qid
        try:
            sitelink = item_dict['sitelinks']['commonswiki']
        except:
            continue

        # Get the value for P910
        try:
            p910 = item_dict['claims']['P910']
        except:
            print 'No P910 value found!'
            continue

        # Get the info about the category item
        for clm in p910:
            # try:
            val = clm.getTarget()
            p910_id = val.title()
            p910_dict = val.get()
            # except:
            #     print 'Unable to get target!'
            #     continue
            # print(p910_id)

        try:
            sitelink2 = p910_dict['sitelinks']['commonswiki']
        except:
            continue

        # see if one is a redirect
        redirect1 = get_commons_redirect_target(sitelink)
        redirect2 = get_commons_redirect_target(sitelink2)
        if redirect1 == '' and redirect2 == '':
            continue

        text = 'y'
        if debug:
            print(redirect1)
            print(redirect2)
            print(sitelink)
            print(sitelink2)
            text = 'n'
            if redirect1 == sitelink2.replace('Category:',''):
                print('Will remove ' + sitelink)
                # text = raw_input("Save? ")
            elif redirect2 == sitelink.replace('Category:',''):
                print('Will remove ' + sitelink2)
                # text = raw_input("Save? ")
            else:
                print('No change')

        if text != 'n':
            if redirect1 == sitelink2.replace('Category:',''):
                page.removeSitelink(site='commonswiki', summary=u'Removing Commons sitelink as it is a redirect to the category sitelinked in the linked category item (' + str(p910_id) + ')')
            elif redirect2 == sitelink.replace('Category:',''):
                val.removeSitelink(site='commonswiki', summary=u'Removing Commons sitelink as it is a redirect to the category sitelinked in the linked topic item (' + str(qid) + ')')
        

# EOF