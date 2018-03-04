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
from pywikibot import textlib
import urllib

maxnum = 100
nummodified = 0

commons = pywikibot.Site('commons', 'commons')
repo = commons.data_repository()  # this is a DataSite object
debug = 1

targetcats = ['Category:Buildings at the University of Manchester']

catredirect_templates = ["category redirect", "Category redirect", "seecat", "Seecat", "see cat", "See cat", "categoryredirect", "Categoryredirect", "catredirect", "Catredirect", "cat redirect", "Cat redirect", "catredir", "Catredir", "redirect category", "Redirect category", "cat-red", "Cat-red", "redirect cat", "Redirect cat", "category Redirect", "Category Redirect", "cat-redirect", "Cat-redirect"]

templatestoavoid = ["Wikidata Infobox", "Wikidata infobox", "wikidata infobox", "wikidata Infobox", "Wikidata person", "wikidata person", "Wikidata place", "wikidata place", "Object location", "object location", "Authority control", "authority control", "{{ac", "{{Ac", "{{Institution", "{{institution", "{{Creator", "{{creator"] + catredirect_templates
templatestoremove = ["Interwiki from Wikidata", "interwiki from Wikidata", "PeopleByName"]

for targetcat in targetcats:
    print "\n" + targetcat
    cat = pywikibot.Category(commons,targetcat)
    targets = cat.subcategories(recurse=True);
    for target in targets:
        if 'Category:' in target.title():
            redirect = ''
            print "\n" + target.title()
            # print target.text
            target_text = target.get()
            try:
                wd_item = pywikibot.ItemPage.fromPage(target)
                item_dict = wd_item.get()
                print wd_item.title()
            except:
                print "No Wikidata sitelink found"
                continue

            # We have a category that's linked to a Wikidata item. Check if we want to add the template:
            if any(option in target_text for option in templatestoavoid):
                for option in templatestoavoid:
                    if option in target_text:
                        print 'Category uses ' + option + ', skipping'
                continue

            # Check the Wikidata item to see if we want to skip this.
            try:
                p301 = item_dict['claims']['P301']
                for clm in p301:
                    savemessage = 'Adding {{Wikidata Infobox}}, current Wikidata ID is ' + wd_item.title() + ', linked to ' + clm.getTarget().title()
            except:
                # print 'P301 not found'
                savemessage = 'Adding {{Wikidata Infobox}}, current Wikidata ID is ' + wd_item.title()
                try:
                    p31 = item_dict['claims']['P31']
                    test = 1
                    for clm in p31:
                        if 'Q4167836' in clm.getTarget().title():
                            # We have a Wikimedia category with no P301, skip it
                            print 'Wikimedia category, no P301'
                            test = 0
                    if test == 0:
                        continue
                except:
                    print 'P31 not found'

            # We're good to go.
            target_text = "{{Wikidata Infobox}}\n" + target_text

            # Remove unneeded templates
            for option in templatestoremove:
                if option in target.text:
                    target_text = target_text.replace("{{"+option+"}}", "")

            # Time to save it
            print target_text
            target.text = target_text
            print savemessage
            text = raw_input("Save on Commons? ")
            if text == 'y':
                try:
                    target.save(savemessage)
                    nummodified += 1
                except:
                    print "That didn't work!"

        if nummodified >= maxnum:
            print 'Reached the maximum of ' + str(maxnum) + ' entries modified, quitting!'
            break

print 'Done! Edited ' + str(nummodified) + ' entries'

# EOF