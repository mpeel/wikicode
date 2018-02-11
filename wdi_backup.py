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

site = pywikibot.Site('commons', 'commons')
repo = site.data_repository()

template = pywikibot.Page(site, 'Template:Wikidata Infobox')

uses = template.embeddedin()

logpage = pywikibot.Page(site, u"User:Mike Peel/WDI backup")

now = datetime.datetime.now()
text = u'This page backs up the QIDs used by calls to {{tl|Wikidata Infobox}}. It was last updated at ' + str(datetime.date(now.year, now.month, now.day)) + '. The [https://bitbucket.org/mikepeel/wikicode/src/master/wdi_backup.py source code is available]. For any maintenance issues, please leave [[User talk:Mike Peel|Mike Peel]] a note.\n'

for page in uses:
    print page.title()
    try:
        wd_item = pywikibot.ItemPage.fromPage(page)
        if wd_item != -1:
            wd_id = wd_item.getID()
        else:
            wd_id = str(-1)
    except:
        wd_id = str(-1)

    print "* [[:" + page.title() + "|" + page.title() + "]] - [[:d:" + wd_id + "|" + wd_id + "]]"
    text = text + "* [[:" + page.title() + "|" + page.title() + "]] - [[:d:" + wd_id + "|" + wd_id + "]]\n"

print text

if text != logpage.text:
    logpage.text = text
    logpage.save(u"Updating")
