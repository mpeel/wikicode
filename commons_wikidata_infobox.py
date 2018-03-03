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

targetcats = ['Category:Santos']

catredirect_templates = ["category redirect", "Category redirect", "seecat", "Seecat", "see cat", "See cat", "categoryredirect", "Categoryredirect", "catredirect", "Catredirect", "cat redirect", "Cat redirect", "catredir", "Catredir", "redirect category", "Redirect category", "cat-red", "Cat-red", "redirect cat", "Redirect cat", "category Redirect", "Category Redirect", "cat-redirect", "Cat-redirect"]

templatestoavoid = ["Wikidata Infobox", "Wikidata infobox", "wikidata infobox", "wikidata Infobox", "Wikidata person", "wikidata person", "Wikidata place", "wikidata place", "Object location", "object location", "Authority control", "authority control", "{{ac", "{{Ac"] + catredirect_templates
templatestoremove = ["Interwiki from Wikidata", "interwiki from Wikidata", "PeopleByName"]

for targetcat in targetcats:
    print "\n" + targetcat
    cat = pywikibot.Category(commons,targetcat)
    targets = cat.members(recurse=True);
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
            else:
                # We have a category that's linked to a Wikidata item. Check if we want to add the template:
                test = 1
                for option in templatestoavoid:
                    if option in target_text:
                        test = 0
                        print 'Category uses ' + option + ', skipping'

                # No point doing this next stage if we've already aborted at the previous stage
                if test:
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
                            for clm in p31:
                                if 'Q4167836' in clm.getTarget().title():
                                    # We have a Wikimedia category with no P301, skip it
                                    test = 0
                                    print 'Wikimedia category, no P301'
                        except:
                            print 'P31 not found'

                if test:
                    # We're good to go.
                    target_text = "{{Wikidata Infobox}}\n" + target_text

                    # Remove unneeded templates
                    for option in templatestoavoid:
                        if option in target.text:
                            target_text = target_text.replace("{{"+option+"}}", "")

                    # Try removing interwikis - currently not working
                    # target_text2 = textlib.removeLanguageLinks(target_text)
                    # if target_text2 != target_text:
                    #     print target_text
                    #     print 'Removing interwikis'
                    #     target_text = target_text2

                    # Time to save it
                    try:
                        print target_text
                        target.text = target_text
                        print savemessage
                        text = raw_input("Save on Commons? ")
                        if text == 'y':
                            target.save(savemessage)
                        nummodified += 1
                    except:
                        print "That didn't work!"

        if nummodified >= maxnum:
            print 'Reached the maximum of ' + str(maxnum) + ' entries modified, quitting!'
            exit()

print 'Done! Edited ' + str(nummodified) + ' entries'

# EOF