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

templates = ["Wikidata person", "wikidata person", "On Wikidata", "on Wikidata", "In Wikidata", "in Wikidata", "Wikidata", "wikidata"]

def prettyPrint(variable):
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(variable)

wikidata_site = pywikibot.Site("wikidata", "wikidata")
repo = wikidata_site.data_repository()  # this is a DataSite object
commons = pywikibot.Site('commons', 'commons')

usetemplate = 1
if usetemplate:
    templates_to_search = ['Wikidata person']
    template = pywikibot.Page(commons, 'Template:'+templates_to_search[0])
    targetcats = template.embeddedin(namespaces='14')
else:
    category = 'Category:Categories with Wikidata link'
    # category = 'Category:Uses of Wikidata Infobox with problems'
    cat = pywikibot.Category(commons,category)
    targetcats = pagegenerators.SubCategoriesPageGenerator(cat, recurse=False);


for targetcat in targetcats:
    print targetcat.title()
    target_text = targetcat.get()

    id_val = 0
    for i in range(0,len(templates)):
        try:
            value = (target_text.split("{{"+templates[i]+" |1="))[1].split("}}")[0]
            try:
                value = value.split('|')[0]
            except:
                null = 1
            if value and id_val == 0:
                id_val = value
        except:
            null = 2
            # print '2'
        try:
            value = (target_text.split("{{"+templates[i]+"|1="))[1].split("}}")[0]
            try:
                value = value.split('|')[0]
            except:
                null = 1
            if value and id_val == 0:
                id_val = value
        except:
            null = 3
            # print '3'
        try:
            value = (target_text.split("{{"+templates[i]+"|"))[1].split("}}")[0]
            try:
                value = value.split('|')[0]
            except:
                null = 1
            if value and id_val == 0:
                id_val = value
        except:
            null = 1
            # print '1'
    print id_val
    if id_val != 0:
        try:
            candidate_item = pywikibot.ItemPage(repo, id_val)
            candidate_item_dict = candidate_item.get()
        except:
            print 'Huh - no page found'

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
            try:
                sitelink = candidate_item_dict['sitelinks']['commonswiki']
            except:
                # No existing sitelink found, add the new one
                data = {'sitelinks': [{'site': 'commonswiki', 'title': targetcat.title()}]}
                # try:
                print "\n\n"
                print id_val
                prettyPrint(candidate_item_dict)
                print data
                text = raw_input("Save? ")
                if text == 'y':
                    candidate_item.editEntity(data, summary=u'Add commons sitelink based on QID on Commons')
                    continue
                else:
                    continue
                # except:
                #     print 'Edit failed'

    # if nummodified >= maxnum:
    #     print 'Reached the maximum of ' + str(maxnum) + ' entries modified, quitting!'
    #     exit()


# maxnum = 2
# nummodified = 0
# stepsize =  10000
# maximum = 2000000
# numsteps = int(maximum / stepsize)


# for i in range(0,numsteps):
#     print 'Starting at ' + str(i*stepsize)

#     query = "SELECT ?item\n"\
#     "WITH { \n"\
#     "  SELECT ?item ?categoryitem WHERE {\n"\
#     "    ?item wdt:P373 ?categoryitem . \n"\
#     '  } LIMIT '+str(stepsize)+' OFFSET '+str(i*stepsize)+'\n'\
#     "} AS %items\n"\
#     "WHERE {\n"\
#     "  INCLUDE %items .\n"\
#     "    SERVICE wikibase:label { bd:serviceParam wikibase:language \"nl,fr,en,de,it,es,no,pt\". }\n"\
#     "    FILTER(NOT EXISTS {\n"\
#     "        ?item rdfs:label ?lang_label.\n"\
#     "        FILTER(LANG(?lang_label) = \"en\")\n"\
#     "    })\n"\
#     "}"

#     print query

#     generator = pagegenerators.WikidataSPARQLPageGenerator(query, site=wikidata_site)
#     for page in generator:
#         # Get the page
#         item_dict = page.get()
#         qid = page.title()
#         print "\n" + qid
#         # Get the value for P373
#         try:
#             p373 = item_dict['claims']['P373']
#         except:
#             print 'No P373 value found!'
#             continue
#         p373_check = 0
#         for clm in p373:
#             p373_check += 1
#         # Only attempt to do this if there is only one value for P373
#         if p373_check != 1:
#             print 'More than one P373 value found! Skipping...'

#         # Check to see if we're looking at a category item
#         catitem = 0
#         try:
#             p31 = item_dict['claims']['P31']
#             print p31
#             for clm in p31:
#                 if 'Q4167836' in clm.getTarget().title():
#                     catitem = 1
#         except:
#             print 'No P31 in target'

#         for clm in p373:
#             new_label = clm.getTarget()
#             if catitem:
#                 new_label = 'Category:' + new_label
#             # if we don't have an English language label, add it.
#             try:
#                 label = val.labels['en']
#                 print label
#             except:
#                 try:
#                     page.editLabels(labels={'en': new_label}, summary=u'Add en label to match Commons category name')
#                     nummodified += 1
#                 except:
#                     print 'Unable to save label edit on Wikidata!'

#             if nummodified >= maxnum:
#                 print 'Reached the maximum of ' + str(maxnum) + ' entries modified, quitting!'
#                 exit()

#     print 'Done! Edited ' + str(nummodified) + ' entries'
         
# # EOF