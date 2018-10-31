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
import re

# Make sure we have the right encoding
reload(sys)
sys.setdefaultencoding('utf-8')

site = pywikibot.Site('meta', 'meta')
repo = site.data_repository()

schedule = pywikibot.Page(site, 'GLAMTLV2018/Program')
scheduletext = schedule.get()
category = pywikibot.Category(site, 'Category:GLAM TLV 2018 submissions')

uses = pagegenerators.CategorizedPageGenerator(category, recurse=False);

whitelist = set('abcdefghijklmnopqrstuvwxy ABCDEFGHIJKLMNOPQRSTUVWXYZ 1234567890')
alllinks = ''
for page in uses:
    title = page.title().replace('GLAMTLV2018/Submissions/','')

    shortname = ''.join(filter(whitelist.__contains__, page.title().replace('GLAMTLV2018/Submissions/','')))
    shortname = shortname.split()
    try:
        shortname = shortname[0:4]
    except:
        print "Trimming string didn't work!"
    shortname = '_'.join(shortname)
    # if title in scheduletext:
    #     print "* '''" + title + " - https://etherpad.wikimedia.org/p/GLAMWIKI2018-" + shortname + "'''"
    # else:
    #     print "* " + title + " - " + shortname


    # if title in scheduletext and "etherpad" not in page.text:
    if "etherpad" not in page.text:
        target_text = page.text
        lines = target_text.splitlines()
        insertline = 0
        i = 0
        for line in lines:
            i += 1
            if "----" in line and insertline==0:
                insertline = i-1
        lines[insertline:insertline] = ['; [https://etherpad.wikimedia.org/p/GLAMWIKI2018-' + shortname + ' Etherpad]']
        target_text = "\n".join(lines)
        print target_text
        if page.text != target_text.strip():
            page.text = target_text.strip()
            # text = raw_input("Save? ")
            # if text == 'y':
            try:
                page.save("Adding link to etherpad")
                continue
            except:
                print "That didn't work!"
                continue
            # else:
            #     continue
