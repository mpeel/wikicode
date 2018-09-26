#!/usr/bin/python
# -*- coding: utf-8  -*-
# Moving calls to Infobox WHS to a Wikidata version
# Mike Peel     14-Oct-2017     Initial version

from __future__ import unicode_literals
import pywikibot
import numpy as np
import time
import string
from pywikibot import pagegenerators
import time
import sys
import string
import datetime

# Make sure we have the right encoding
reload(sys)
sys.setdefaultencoding('utf-8')

site = pywikibot.Site('en', 'wikipedia')
repo = site.data_repository()

template = pywikibot.Page(site, 'Template:Infobox person/Wikidata')

uses = template.embeddedin()

for page in uses:
    print "\n"+page.title()
    # print page.text
    try:
        target = (page.text.split("person/Wikidata"))[1].split("}}")[0]
        print target
        if 'url' in target:
            print 'Found'
            text = raw_input("Pausing")
        else:
            continue
    except:
        continue
