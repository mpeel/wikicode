#!/usr/bin/python
# -*- coding: utf-8  -*-
# Migrate object photo to art photo
# Started 25 August 2018 by Mike Peel
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
debug = True
manual = True
category = 'Category:Luba headrest-70.1999.9.1'
templates = ['Object photo']
savemessage="Switch to use {{Art photo}}"

def migratefile(targetfile, wikidata):
    print targetfile
    target_text = targetfile.get()
    print target_text

    if templates[0] not in target_text:
        return 0

    newtext = target_text.replace(templates[0], 'Art photo')
    newtext = newtext.replace('object = ' + category.replace('Category:',''), 'wikidata = ' + wikidata)
    newtext = newtext.replace('object=' + category.replace('Category:',''), 'wikidata=' + wikidata)
    newtext = newtext.replace('object      = ' + category.replace('Category:',''), 'wikidata    = ' + wikidata)
    newtext = newtext.replace('author=','photographer=')
    newtext = newtext.replace('author      =','photographer=')
    newtext = newtext.replace(' |detail =\n','')
    newtext = newtext.replace(' |detail      =\n','')
    newtext = newtext.replace(' |description =\n','')
    newtext = newtext.replace(' |date = \n','')
    newtext = newtext.replace(' |date        =\n','')
    print newtext

    if newtext != target_text:
        text = raw_input("Save on Commons? ")
        if text == 'y':
            try:
                targetfile.text = newtext
                targetfile.save(savemessage)
                return 1
            except:
                print "That didn't work!"
                return 0
        else:
            return 0
    else:
        return 0

# Start the category walker
cat = pywikibot.Category(commons,category)
images = cat.members(recurse=True);
wikidata = pywikibot.ItemPage.fromPage(cat)
item_dict = wikidata.get()
try:
    existing_id = item_dict['claims']['P301']
    print 'P301 exists, following that.'
    for clm2 in existing_id:
        wikidata = clm2.getTarget()
except:
    null = 0

print wikidata
print images
for image in images:
    print image.title()
    nummodified += migratefile(image, wikidata.title())

    if nummodified >= maxnum:
        print 'Reached the maximum of ' + str(maxnum) + ' entries modified, quitting!'
        exit()

print 'Done! Edited ' + str(nummodified) + ' entries'
                
# EOF