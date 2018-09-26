#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Check for consistency in commons category usage
# Mike Peel     01-Mar-2018      v1 - start
# Mike Peel     26-Jun-2018      v2 - restructure with options for running, and database
from __future__ import unicode_literals

import pywikibot
import numpy as np
import time
import string
from pywikibot import pagegenerators
from pywikibot import textlib
import urllib
import csv

import sys
# sys.setdefaultencoding() does not exist, here!
reload(sys)  # Reload does the trick!
sys.setdefaultencoding('UTF8')

maxnum = 5000000
nummodified = 0

commons = pywikibot.Site('commons', 'commons')
repo = commons.data_repository()  # this is a DataSite object
manual = False
random = False
usequery = False
usetemplate = ''#'Individual aircraft'
usequarry = 'quarry15.csv'
quarry_reference = ''#'quarry5.csv'
useimport = 'import.csv'
newstyle = False
database = True

existing_uses = {}
if database:
    print 'Loading database...'
    with open('commons_wikidata_infobox_uses.csv', mode='r') as infile:
        reader = csv.reader(infile)
        existing_uses = {rows[0] for rows in reader}
    print 'Database loaded!'

targetcats = ['Category:CommonsRoot']

catredirect_templates = ["category redirect", "Category redirect", "seecat", "Seecat", "see cat", "See cat", "categoryredirect", "Categoryredirect", "catredirect", "Catredirect", "cat redirect", "Cat redirect", "catredir", "Catredir", "redirect category", "Redirect category", "cat-red", "Cat-red", "redirect cat", "Redirect cat", "category Redirect", "Category Redirect", "cat-redirect", "Cat-redirect"]

templatestoavoid = ["Wikidata Infobox", "Wikidata infobox", "wikidata infobox", "wikidata Infobox", "Infobox Wikidata", "infobox Wikidata", "Infobox wikidata", "infobox wikidata", "Wikidata person", "wikidata person", "Wikidata place", "wikidata place", "{{Institution", "{{institution", "{{Creator", "{{creator", "User:Rama/Catdef", "Building address", "building address", "Taxonavigation", "taxonavigation", "Category definition:", "category definition:", "MDcat", "mDcat", "Date navbox", "date navbox", "Monthbyyear", "monthbyyear", "{{Artwork", "{{artwork", 'Lepidoptera', 'lepidoptera', 'Coleoptera', 'coleoptera', 'Disambig', 'disambig', 'Disambiguation', 'disambiguation', 'Razločitev', 'razločitev', 'Begriffsklärung', 'begriffsklärung', 'Dab', 'dab', 'Aimai', 'aimai', 'Finlandyear', 'finlandyear', 'Finlandyear-Sweden', 'finlandyear-Sweden', 'AirDisasters', 'airDisasters'] + catredirect_templates
templatestoremove = ["Interwiki from Wikidata", "interwiki from Wikidata", "Interwiki from wikidata", "interwiki from wikidata", "PeopleByName", "peopleByName", "Authority control", "authority control", "On Wikidata", "on Wikidata", "In Wikidata", "in Wikidata", "Wikidata", "wikidata", "Object location", "object location", 'mainw', "Mainw", "en", "En", "individual aircraft", "Individual aircraft"]
templatestobebelow = ["Object location", "object location", "Authority control", "authority control", "{{ac", "{{Ac", "On Wikidata", "on Wikidata", "{{Wikidata", "{{wikidata", "In Wikidata", "in Wikidata", "New Testament papyri", "new Testament papyri", "Geogroup", "geogroup", "GeoGroup", "geoGroup", "GeoGroupTemplate", "geoGroupTemplate", "FoP-Brazil"]
templates_to_skip_to_end = ["Cultural Heritage Russia", "cultural Heritage Russia", "Historic landmark", "historic landmark", "FOP-Armenia", "{{HPC","NavigationBox"]

# This is the main template
def addtemplate(target):
    try:
        wd_item = pywikibot.ItemPage.fromPage(target)
    except:
        # print "No Wikidata sitelink found"
        return 0
    try:
        item_dict = wd_item.get()
        print wd_item.title()
    except:
        return 0
    try:
        target_text = target.get()
    except:
        # print 'Error, page not found!'
        return 0

    redirect = ''
    print "\n" + target.title()

    # Quick-check for an existing infobox, and skip this if found before doing more processing
    if "Wikidata Infobox" in target_text:
        'Already uses Wikidata Infobox!'
        return 0

    # We have a category that's linked to a Wikidata item. Check if we want to add the template:
    if any(option in target_text for option in templatestoavoid):
        for option in templatestoavoid:
            if option in target_text:
                print 'Category uses ' + option + ', skipping'
        return 0

    # Check the Wikidata item to see if we want to skip this.
    wd_id = 0
    try:
        p301 = item_dict['claims']['P301']
        for clm in p301:
            print clm
            savemessage = 'Adding {{Wikidata Infobox}}, current Wikidata ID is ' + wd_item.title() + ', linked to ' + clm.getTarget().title()
            wd_id = clm.getTarget().title()
            # Check to see if it's linked to a list item, and avoid if so
            test = pywikibot.ItemPage(repo, wd_id)
            try:
                testitem = test.get()
                test_p31 = testitem['claims']['P31']
                for clm in test_p31:
                    if 'Q13406463' in clm.getTarget().title():
                        print 'Category linked to a list item'
                        return 0
            except:
                print 'nm'
    except:
        # print 'P301 not found'
        savemessage = 'Adding {{Wikidata Infobox}}, current Wikidata ID is ' + wd_item.title()
        try:
            p971 = item_dict['claims']['P971']
        except:
            try:
                p31 = item_dict['claims']['P31']
                test = 1
                for clm in p31:
                    if 'Q4167836' in clm.getTarget().title():
                        # We have a Wikimedia category with no P301, skip it
                        print 'Wikimedia category, no P301'
                        return 0
                    if 'Q14204246' in clm.getTarget().title():
                        # We have a Wikimedia category with no P301, skip it
                        print 'Wikimedia project page'
                        return 0
                    if 'Q13406463' in clm.getTarget().title():
                        # We have a Wikimedia category with no P301, skip it
                        print 'Wikimedia list page'
                        return 0
                    if 'Q4167410' in clm.getTarget().title():
                        # We have a Wikimedia category with no P301, skip it
                        print 'Wikimedia disambiguation page'
                        return 0
            except:
                print 'P31 not found'

    # Remove unneeded templates
    for option in templatestoremove:
        if option in target.text:
            target_text = target_text.replace("{{"+option+"|"+wd_item.title()+"}}\n", "")
            target_text = target_text.replace("{{"+option+"|"+wd_item.title()+"}}", "")
            if wd_id != 0:
                target_text = target_text.replace("{{"+option+"|"+wd_id+"}}\n", "")
                target_text = target_text.replace("{{"+option+"|"+wd_id+"}}", "")
            target_text = target_text.replace("{{"+option+"|Wikidata="+wd_item.title()+"}}\n", "")
            target_text = target_text.replace("{{"+option+"|Wikidata="+wd_item.title()+"}}", "")
            if wd_id != 0:
                target_text = target_text.replace("{{"+option+"|Wikidata="+wd_id+"}}\n", "")
                target_text = target_text.replace("{{"+option+"|Wikidata="+wd_id+"}}", "")
            target_text = target_text.replace("{{"+option+"}}\n", "")
            target_text = target_text.replace("{{"+option+"}}", "")
            target_text = target_text.replace("{{"+option+"|}}\n", "")
            target_text = target_text.replace("{{"+option+"|}}", "")
            target_text = target_text.replace("{{"+option+"| }}\n", "")
            target_text = target_text.replace("{{"+option+"| }}", "")

    # We're good to go. Look for the best line to add the template in.
    i = 0
    lines = target_text.splitlines()
    insertline = 0
    skip_to_end = 1
    if any(option in target_text for option in templates_to_skip_to_end) or skip_to_end:
        for line in lines:
            i += 1
            if "}}" in line:
                insertline = i
            if "|}" in line:
                insertline = i
    else:
        for line in lines:
            i += 1
            if any(option in line for option in templatestobebelow):
                insertline = i
    lines[insertline:insertline] = ["{{Wikidata Infobox}}"]
    target_text = "\n".join(lines)

    # Time to save it
    print target_text
    target.text = target_text.strip()
    print savemessage
    if manual:
        text = raw_input("Save on Commons? ")
        if text == 'y':
            try:
                target.save(savemessage)
                return 1
            except:
                print "That didn't work!"
                return 0
        else:
            return 0
    else:
        try:
            target.save(savemessage)
            return 1
        except:
            print "That didn't work!"
            return 0

# That's the end of the function, now on to the category walkers

nummodified = 0
numchecked = 0
test = 0
if random:
    # Pick random categories
    while nummodified < maxnum:
        targets = pagegenerators.RandomPageGenerator(total=100, site=commons, namespaces='14')
        for target in targets:
            print target.title()
            if target.title() not in existing_uses:
                nummodified += addtemplate(target)
                print nummodified
            
            if nummodified >= maxnum:
                print 'Reached the maximum of ' + str(maxnum) + ' entries modified, quitting!'
                break
elif usetemplate:
    # Go through uses of a template
    template = pywikibot.Page(commons, 'Template:'+usetemplate)
    targetcats = template.embeddedin(namespaces='14')
    for target in targetcats:
        print target.title()
        if target.title() not in existing_uses:
            nummodified += addtemplate(target)
            print nummodified
        
        if nummodified >= maxnum:
            print 'Reached the maximum of ' + str(maxnum) + ' entries modified, quitting!'
            break
elif usequarry:
    quarry_ref = []
    if quarry_reference != '':
        with open(quarry_reference, mode='r') as infile:
            reader = csv.reader(infile)
            quarry_ref = {rows[1] for rows in reader}
    with open(usequarry, mode='r') as infile:
        reader = csv.reader(infile)
        targets = {rows[1] for rows in reader}
    for target in targets:
        # if test == 0 and 'Toyota JPN' not in target:
        if target in quarry_ref:
            continue
        # else:
            # test = 1
        print target
        cat = pywikibot.Category(commons,'Category:'+target)
        if cat.title() not in existing_uses:
            nummodified += addtemplate(cat)
        else:
            print 'Already in database'
elif useimport:
    with open(useimport, mode='r') as infile:
        reader = csv.reader(infile)
        targets = {rows[0] for rows in reader}
    for target in targets:
        cat = pywikibot.Category(commons,target)
        if cat.title() not in existing_uses:
            nummodified += addtemplate(cat)
        else:
            print 'Already in database'
elif usequery:
    query = 'SELECT (COUNT(DISTINCT ?cat) AS ?count) ?item ?itemCat WHERE {\n'\
        '  ?cat wdt:P971 ?item .\n'\
        '  ?item wdt:P373 ?itemCat .\n'\
        '} GROUP BY ?item ?itemCat \n'\
        'ORDER BY DESC (?count)'
    generator = pagegenerators.WikidataSPARQLPageGenerator(query, site=repo)
    for page in generator:
        try:
            print page.title()
            item_dict = page.get()
            p373 = item_dict['claims']['P373']
            for clm in p373:
                val = clm.getTarget()
                commonscat = u"Category:" + val
            # sitelink = item_dict['sitelinks']['commonswiki']
        except:
            print 'Something went wrong'
        print commonscat
        if commonscat not in existing_uses:
            nummodified += addtemplate(pywikibot.Category(commons,commonscat))
        else:
            print 'Already in database'
        if nummodified >= maxnum:
            print 'Reached the maximum of ' + str(maxnum) + ' entries modified, quitting!'
            break


elif newstyle:
    # New style of category walker
    numchecked = 0
    catschecked = 0

    seen   = set(targetcats)
    active = set(targetcats)

    while active:
        next_active = set()
        for item in active:
            cat = pywikibot.Category(commons,item)
            if cat.title() not in existing_uses:
                nummodified += addtemplate(cat)
            else:
                print 'Already in database'
            numchecked += 1
            print str(nummodified) + " - " + str(numchecked) + "/" + str(len(seen)) + "/" + str(len(active)) + "/" + str(len(next_active))

            # See if there are subcategories that we want to check in the future
            for result in pagegenerators.SubCategoriesPageGenerator(cat, recurse=False):
                if result.title() not in seen:
                    seen.add(result.title())
                    next_active.add(result.title())
        active = next_active
        if nummodified >= maxnum:
            print 'Reached the maximum of ' + str(maxnum) + ' entries modified, quitting!'
            break
else:
    # Old style of category walker
    for targetcat in targetcats:
        cat = pywikibot.Category(commons,targetcat)
        if cat.title() not in existing_uses:
            nummodified += addtemplate(cat)
        else:
            print 'Already in database'
        numchecked += 1
        print str(nummodified) + " - " + str(numchecked) + "/" + str(len(targetcats))

        # See if there are subcategories that we want to check in the future
        subcats = pagegenerators.SubCategoriesPageGenerator(cat, recurse=False);
        for subcat in subcats:
            if subcat.title() in targetcats:
                continue
            else:
                targetcats.append(subcat.title())

        if nummodified >= maxnum:
            print 'Reached the maximum of ' + str(maxnum) + ' entries modified, quitting!'
            break

print 'Done! Edited ' + str(nummodified) + ' entries'

# EOF
