#!/usr/bin/python
# -*- coding: utf-8  -*-
# Check for consistency in commons category usage
# Mike Peel     18-Apr-2018      v1 - start

from __future__ import unicode_literals

import pywikibot
import numpy as np
import time
import string
from pywikibot import pagegenerators
import urllib

maxnum = 1000
nummodified = 0

commons = pywikibot.Site('commons', 'commons')
repo = commons.data_repository()  # this is a DataSite object
debug = 1
manual = 1
savemessage = "Disable defaultsort from infobox to avoid conflict"

def fixcat(targetcat):
    target_text = targetcat.get()
    print target_text

    target_text = target_text.replace("{{Wikidata Infobox}}", "{{Wikidata Infobox|defaultsort=no}}")
    target_text = target_text.replace("{{Wikidata infobox}}", "{{Wikidata Infobox|defaultsort=no}}")
    target_text = target_text.replace("{{wikidata Infobox}}", "{{Wikidata Infobox|defaultsort=no}}")
    target_text = target_text.replace("{{wikidata infobox}}", "{{Wikidata Infobox|defaultsort=no}}")

    # Time to save it
    if (target_text != targetcat.get()):
        print target_text
        targetcat.text = target_text.strip()
        print savemessage
        text = raw_input("Save on Commons? ")
        if manual:
            if text == 'y':
                try:
                    targetcat.save(savemessage)
                    return 1
                except:
                    print "That didn't work!"
                    return 0
            else:
                return 0
        else:
            try:
                targetcat.save(savemessage)
                return 1
            except:
                print "That didn't work!"
                return 0
    else:
        return 0


startcat = 'Category:Pages with DEFAULTSORT conflicts'
cat = pywikibot.Category(commons,startcat)
targetcats = pagegenerators.SubCategoriesPageGenerator(cat, recurse=False);

for targetcat in targetcats:
    print targetcat
    print "\n" + targetcat.title()
    # print target.text
    nummodified += fixcat(targetcat)

    if nummodified >= maxnum:
        print 'Reached the maximum of ' + str(maxnum) + ' entries modified, quitting!'
        exit()

print 'Done! Edited ' + str(nummodified) + ' entries'
                
# EOF