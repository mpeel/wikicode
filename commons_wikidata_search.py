#!/usr/bin/python
# -*- coding: utf-8  -*-
# Move commons category sitelinks to category items where needed
# Mike Peel     10-Jun-2018      v1

from __future__ import unicode_literals

import pywikibot
from pywikibot.data import api
import numpy as np
import time
import string
from pywikibot import pagegenerators
import urllib
import pprint
import csv
import random

database = False
manual = False
maxnum = 1000000
usetemplate = 0
usecategory = 1
wikidata_site = pywikibot.Site("wikidata", "wikidata")
repo = wikidata_site.data_repository()  # this is a DataSite object
commons = pywikibot.Site('commons', 'commons')

# From https://gist.github.com/ettorerizza/7eaebbd731781b6007d9bdd9ddd22713
def search_entities(site, itemtitle):
     params = { 'action' :'wbsearchentities', 
                'format' : 'json',
                'language' : 'en',
                'type' : 'item',
                'search': itemtitle}
     request = api.Request(site=site, parameters=params)
     return request.submit()

def get_entities(site, wdItem):
    request = api.Request(site=site,
                          action='wbgetentities',
                          format='json',
                          ids=wdItem,
                          languages='en|fr',
                          props='sitelinks/urls|descriptions|aliases|labels',
                          sitefilter='enwiki|frwiki')    
    return request.submit()

def prettyPrint(variable):
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(variable)

def runimport(targetcat):
    print targetcat.title()
    try:
        wd_item = pywikibot.ItemPage.fromPage(targetcat)
        item_dict = wd_item.get()
        print wd_item.title()
        return 0
    except:
        print 'No existing link'

    searchname = targetcat.title().replace('Category:','')
    searchname2 = searchname.split('(', 1)[0]
    if searchname2 != '':
        searchname = searchname2
    wikidataEntries = search_entities(wikidata_site, searchname)
    prettyPrint(wikidataEntries)
    if wikidataEntries['search'] != []:
        results = wikidataEntries['search']
        prettyPrint(results)
        numresults = len(results)
        for i in reversed(range(0,numresults)):
            qid = results[i]['id']
            try:
                candidate_item = pywikibot.ItemPage(repo, qid)
                candidate_item_dict = candidate_item.get()
            except:
                print 'Huh - no page found'

            skip = 0
            try:
                p31 = candidate_item_dict['claims']['P31']
                for clm in p31:
                    if 'Q4167410' in clm:
                        skip = 1
            except:
                null = 0
            if skip == 1:
                continue
            incat = 0
            try:
                p18 = candidate_item_dict['claims']['P18']
                for clm in p18:
                    title = clm.getTarget()
                    print title.title()
                    page = pywikibot.Page(commons, title.title())
                    test = page.get()
                    if '[['+targetcat.title()+']]' in test:
                        incat = 1
                        continue
                    else:
                        incat = 2
                if incat == 1:
                    continue
            except:
                print 'No image found'
        try:
            sitelink = candidate_item_dict['sitelinks']['commonswiki']
        except:
            try:
                existing_id = candidate_item_dict['claims']['P910']
                print 'P910 exists, following that.'
                for clm2 in existing_id:
                    candidate_item = clm2.getTarget()
                    candidate_item_dict = candidate_item.get()
                    print candidate_item.title()
            except:
                null = 0
            # Try the sitelink check again
            try:
                sitelink = candidate_item_dict['sitelinks']['commonswiki']
            except:
                # No existing sitelink found, add the new one
                data = {'sitelinks': [{'site': 'commonswiki', 'title': targetcat.title()}]}
                try:
                    if manual:
                        print "\n\n"
                        prettyPrint(candidate_item_dict)
                        print data
                        print qid
                        print targetcat.title()
                        if incat == 1:
                            print 'Image is in category'
                        elif incat == 2:
                            print 'Image not in category'
                        else:
                            print 'No image'
                        text = raw_input("Save? ")
                        if text == 'y':
                            candidate_item.editEntity(data, summary=u'Add commons sitelink')
                            return 1
                        else:
                            return 0
                    else:
                        if incat == 1:
                            candidate_item.editEntity(data, summary=u'Add commons sitelink based on label and image')
                            return 1
                        else:
                            return 0
                except:
                    print 'Edit failed'
        return 0
    return 0

existing_uses = {}
if database:
    print 'Loading database...'
    with open('commons_wikidata_infobox_uses.csv', mode='r') as infile:
        reader = csv.reader(infile)
        existing_uses = {rows[0] for rows in reader}
    print 'Database loaded!'

nummodified = 0
if usetemplate:
    templates = ['South African Heritage Site']
    template = pywikibot.Page(commons, 'Template:'+templates[0])
    targetcats = template.embeddedin(namespaces='14')

    for targetcat in targetcats:
        print targetcat.title()

        if targetcat.title() in existing_uses:
            print 'In database'
            continue
        else:
            runimport(targetcat)
elif usecategory:
    targetcats = ['Category:Astronomy']
    # targetcats = ['Category:Cultural heritage monuments in Norway with known IDs']#['Category:São Vicente (São Paulo)']
    # New style of category walker
    numchecked = 0
    catschecked = 0
    i = 0
    seen   = set(targetcats)
    active = set(targetcats)

    while active:
        i+=1
        next_active = set()
        for item in active:
            cat = pywikibot.Category(commons,item)
            if cat.title() not in existing_uses:
                nummodified += runimport(cat)
            else:
                print 'Already in database'
            numchecked += 1
            print str(nummodified) + " - " + str(numchecked) + "/" + str(len(seen)) + "/" + str(len(active)) + "/" + str(len(next_active))

            # See if there are subcategories that we want to check in the future
            # if i == 1:
            for result in pagegenerators.SubCategoriesPageGenerator(cat, recurse=False):
                if result.title() not in seen:
                    seen.add(result.title())
                    next_active.add(result.title())
        temp = list(next_active)
        random.shuffle(temp)
        active = set(temp)
        if nummodified >= maxnum:
            print 'Reached the maximum of ' + str(maxnum) + ' entries modified, quitting!'
            break
else:
    # Pick random categories
    while nummodified < maxnum:
        targets = pagegenerators.RandomPageGenerator(total=100, site=commons, namespaces='14')
        for target in targets:
            print target.title()
            if target.title() not in existing_uses:
                nummodified += runimport(target)
                print nummodified
            
            if nummodified >= maxnum:
                print 'Reached the maximum of ' + str(maxnum) + ' entries modified, quitting!'
                break

# EOF