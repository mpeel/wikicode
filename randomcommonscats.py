#!/usr/bin/python
# -*- coding: utf-8  -*-
# Fetch N random commons categories without wikidata links
# Mike Peel     27-Jun-2018     Initial version

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

site = pywikibot.Site('commons', 'commons')
repo = site.data_repository()

num = 1000
blank = 0
error = 0
text = "This is a sample of " + str(num) + " random categories without Wikidata sitelinks.\n\n"

# Pick random categories
numfound = 0
while numfound < num:
    targets = pagegenerators.RandomPageGenerator(total=100, site=site, namespaces='14')
    for target in targets:
        print target.title()
        try:
            wd_item = pywikibot.ItemPage.fromPage(target)
        except:
            text += "# " + "[[:"+target.title()+"]]\n"
            numfound += 1

        if numfound >= num:
            print 'Reached the maximum of ' + str(num) + ' entries modified, quitting!'
            break
print text

page = pywikibot.Page(site, u"User:Mike Peel/Commons categories without Wikidata sitelink")
page.text = text
page.save(u"Fresh batch")
