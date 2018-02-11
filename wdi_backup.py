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
text = u'This page backs up the QIDs used by calls to {{tl|Wikidata Infobox}}. It was last updated at ' + str(datetime.date(now.year, now.month, now.day)) + '. The source code is available. For any maintenance issues, please leave [[User talk:Mike Peel|Mike Peel]] a note.\n'

for page in uses:
    wd_item = pywikibot.ItemPage.fromPage(page)
    wd_item.get()
    wd_id = wd_item.getID()

    text = text + ("* [[:" + page.title() + "|" + page.title() + "]] - [[:d:" + wd_id + "|" + wd_id + "]]\n")

if text != logpage.text:
    logpage.text = text
    page.save(u"Updating")
