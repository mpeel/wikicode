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

# Make sure we have the right encoding
reload(sys)
sys.setdefaultencoding('utf-8')

site = pywikibot.Site('en', 'wikipedia')
repo = site.data_repository()

template = pywikibot.Page(site, 'Template:Infobox World Heritage Site')

uses = template.embeddedin()

i = 0
for page in uses:
    #lines.append(page.title())
    print page.title()
    text = page.text
    text = string.replace(text, "{{Infobox World Heritage Site|child=yes}}", "{{Infobox World Heritage Site/wikidata|child=yes}}")
    text = string.replace(text, "{{Infobox World Heritage Site}}", "{{Infobox World Heritage Site/wikidata}}")
    if text != page.text:
	    page.text = text
	    page.save(u"Moving Infobox World Heritage Site call to the wikidata-specific version")
	else:
	    print 'Not updating: page is identical'