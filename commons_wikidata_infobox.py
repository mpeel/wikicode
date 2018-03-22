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

targetcats = ['Category:Monuments and memorials in São Paulo (city)']

catredirect_templates = ["category redirect", "Category redirect", "seecat", "Seecat", "see cat", "See cat", "categoryredirect", "Categoryredirect", "catredirect", "Catredirect", "cat redirect", "Cat redirect", "catredir", "Catredir", "redirect category", "Redirect category", "cat-red", "Cat-red", "redirect cat", "Redirect cat", "category Redirect", "Category Redirect", "cat-redirect", "Cat-redirect"]

templatestoavoid = ["Wikidata Infobox", "Wikidata infobox", "wikidata infobox", "wikidata Infobox", "Infobox Wikidata", "infobox Wikidata", "Wikidata person", "wikidata person", "Wikidata place", "wikidata place", "{{Institution", "{{institution", "{{Creator", "{{creator"] + catredirect_templates
templatestoremove = ["Interwiki from Wikidata", "interwiki from Wikidata", "Interwiki from wikidata", "interwiki from wikidata", "PeopleByName", "peopleByName", "Authority control", "authority control"]
templatestobebelow = ["Object location", "object location", "Authority control", "authority control", "{{ac", "{{Ac", "On Wikidata", "on Wikidata", "{{Wikidata", "{{wikidata", "In Wikidata", "in Wikidata", "On Wikidata", "on Wikidata", "New Testament papyri", "new Testament papyri", "Geogroup", "geogroup", "GeoGroup", "geoGroup", "GeoGroupTemplate", "geoGroupTemplate", "FoP-Brazil"]
templates_to_skip_to_end = ["Cultural Heritage Russia", "cultural Heritage Russia", "Historic landmark", "historic landmark", "FOP-Armenia", "{{HPC",]

checkedcats = []
for targetcat in targetcats:
    print "\n" + targetcat
    cat = pywikibot.Category(commons,targetcat)
    targets = cat.subcategories(recurse=True);
    for target in targets:
        # If we've already checked this category in this run, then skip it.
        if target.title() in checkedcats:
            continue
        checkedcats.append(target.title())

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

        # We're good to go. Look for the best line to add the template in.
        i = 0
        lines = target_text.splitlines()
        insertline = 0
        skip_to_end = 0
        if any(option in target_text for option in templates_to_skip_to_end):
            for line in lines:
                i += 1
                if "}}" in line:
                    insertline = i
        else:
            for line in lines:
                i += 1
                if any(option in line for option in templatestobebelow):
                    insertline = i
        lines[insertline:insertline] = ["{{Wikidata Infobox}}\n"]
        target_text = "\n".join(lines)

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

        # time.sleep(5)
        if nummodified >= maxnum:
            print 'Reached the maximum of ' + str(maxnum) + ' entries modified, quitting!'
            break

print 'Done! Edited ' + str(nummodified) + ' entries'

# EOF