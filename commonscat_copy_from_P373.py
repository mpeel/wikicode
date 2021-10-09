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
from pibot_functions import *

maxnum = 100000
nummodified = 0
stepsize =  1000
maximum = 6000000
numsteps = int(maximum / stepsize)

catredirect_templates = ["category redirect", "Category redirect", "seecat", "Seecat", "see cat", "See cat", "categoryredirect", "Categoryredirect", "catredirect", "Catredirect", "cat redirect", "Cat redirect", "catredir", "Catredir", "redirect category", "Redirect category", "cat-red", "Cat-red", "redirect cat", "Redirect cat", "category Redirect", "Category Redirect", "cat-redirect", "Cat-redirect"]


wikidata_site = pywikibot.Site("wikidata", "wikidata")
repo = wikidata_site.data_repository()
commons = pywikibot.Site('commons', 'commons')
debug = 1
for i in range(0,numsteps):
    print('Starting at ' + str(i*stepsize))

    query = 'SELECT ?item\n'\
    'WITH {\n'\
    '   SELECT ?item ?commonscat WHERE {\n'\
    '       ?item wdt:P373 ?commonscat .\n'\
    '  }  LIMIT ' + str(stepsize) + ' OFFSET ' + str(i*stepsize) + '\n'\
    '} AS %cats \n'\
    'WHERE {\n'\
    '    hint:Query hint:optimizer "None".\n'\
    '    INCLUDE %cats .\n'\
    '    MINUS {?item wikibase:directClaim [] } . \n'\
    '    BIND(STRLANG(CONCAT("Category:", ?commonscat),"en") AS ?c1) .\n'\
    '    OPTIONAL {\n'\
    '         ?commonspage schema:name ?c1 .\n'\
    '         ?commonspage schema:isPartOf <https://commons.wikimedia.org/> .\n'\
    '         ?commonspage schema:about [] .\n'\
    '    }\n'\
    '    FILTER (!bound(?commonspage)) \n'\
    '    MINUS {?item wdt:P31 wd:Q4167410}\n'\
    '    OPTIONAL {\n'\
    '        ?item2 wdt:P373 ?commonscat .\n'\
    '    }\n'\
   '    FILTER NOT EXISTS {\n'\
   '        ?item3 wdt:P373 ?commonscat .\n'\
   '        FILTER (?item3 != ?item) .\n'\
   '        FILTER (!(bound(?item2) && ?item3 = ?item2))\n'\
   '    }\n'\
    '    MINUS {?commonslink schema:about ?item . ?commonslink schema:isPartOf <https://commons.wikimedia.org/> . } \n'\
    '}'
    # '    MINUS {?item wdt:P910 [] }\n'\
    # '}'

    print(query)

    try:
        generator = pagegenerators.WikidataSPARQLPageGenerator(query, site=wikidata_site)
	    for page in generator:
	        try:
	            item_dict = page.get()
	            qid = page.title()
	        except:
	            print('Huh - no page found')
	            continue


	        print("\n" + qid)
	        print(page.labels)
	        try:
	            p373 = item_dict['claims']['P373']
	        except:
	            print('Huh - no P373 found')
	            continue
	        p373_check = 0
	        for clm in p373:
	            p373_check += 1

	        # If we have a P910 value, switch to using that item
	        try:
	            existing_id = item_dict['claims']['P910']
	            print('P910 exists, following that.')
	            for clm2 in existing_id:
	                page = clm2.getTarget()
	                item_dict = page.get()
	                print(page.title())
	        except:
	            null = 0

	        # Double-check that we don't already have a sitelink
	        try:
	            sitelink = get_sitelink_title(item_dict['sitelinks']['commonswiki'])
	            sitelink_check = 1
	        except:
	            sitelink_check = 0

	        # If we have a sitelink, is the P373 value we found a redirect to it?
	        if sitelink_check == 1:
	            for clm in p373:
	                val = clm.getTarget()
	                val = clm.getTarget()
	                commonscat = u"Category:" + val
	                try:
	                    targetpage = pywikibot.Page(commons, commonscat)
	                except:
	                    print('Found a bad sitelink')
	                else:
	                    redirect = ''
	                    for option in catredirect_templates:
	                        if "{{" + option in targetpage.text:
	                            try:
	                                redirect = (targetpage.text.split("{{" + option + "|"))[1].split("}}")[0]
	                            except:
	                                try:
	                                    redirect = (targetpage.text.split("{{" + option + " |"))[1].split("}}")[0]
	                                except:
	                                    print('Wikitext parsing bug!')
	                            redirect = redirect.replace(u":Category:","")
	                            redirect = redirect.replace(u"Category:","")
	                    if redirect != '':
	                        # print clm
	                        # print redirect
	                        print(sitelink)
	                        if redirect == str(sitelink).replace(u'Category:',''):
	                            # text = raw_input("Save? ")
	                            # if text == 'y':
	                            clm.changeTarget(redirect, summary=u"Update P373 to avoid commons category redirect")
	                            nummodified+=1


	        # Only attempt to do this if there is only one value for P373 and no existing sitelink
	        if p373_check == 1 and sitelink_check == 0:
	            for clm in p373:
	                val = clm.getTarget()
	                commonscat = u"Category:" + val
	                # The commons category must already exist
	                try:
	                    sitelink_page = pywikibot.Page(commons, commonscat)
	                except:
	                    print('Found a bad sitelink')
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
	                            print(nummodified)
	                        except:
	                            print('Edit failed')

	                if nummodified >= maxnum:
	                    print('Reached the maximum of ' + str(maxnum) + ' entries modified, quitting!')
	                    exit()
    except:
        continue

print('Done! Edited ' + str(nummodified) + ' entries')

# EOF
