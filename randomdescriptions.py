#!/usr/bin/python
# -*- coding: utf-8  -*-
# Fetch N random articles, and print their descriptions
# Mike Peel     11-Dec-2017     Initial version

from __future__ import unicode_literals
import pywikibot
import numpy as np
import time
import string
from pywikibot import pagegenerators
import time
import sys
import string

# Make sure we have the right encoding
reload(sys)
sys.setdefaultencoding('utf-8')

site = pywikibot.Site('en', 'wikipedia')
repo = site.data_repository()

num = 1000
blank = 0
error = 0
text = "This is a sample of " + str(num) + " random pages and their Wikidata descriptions.\n\n"
for page in pagegenerators.RandomPageGenerator(total=num, site=site, namespaces=[0]):
    print page
    try:
        wd_item = pywikibot.ItemPage.fromPage(page)
        wd_item.get()
        try:
            text += "# " + str(page).replace("wikipedia:en:", "") + " - " + wd_item.descriptions['en'] + "\n"
        except:
            text += "# " + str(page).replace("wikipedia:en:", "") + " - \n"
            blank += 1
    except:
        text += "# " + str(page).replace("wikipedia:en:", "") + " - (no Wikidata item)\n"
        error += 1

text += "\n" + str(blank) + " were blank and " + str(error) + " had no Wikidata entry!"
print text

page = pywikibot.Page(site, u"User:Mike Peel/Wikidata descriptions")
page.text = text
page.save(u"Fresh batch")
