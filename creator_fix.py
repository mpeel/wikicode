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

template = pywikibot.Page(site, 'Template:Wikidata person')

uses = template.embeddedin(namespaces='6')

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

    print page.text
    try:
        target = (page.text.split("{{Wikidata person|1="))[1].split("}}")[0]
    except:
        try:
            target = (page.text.split("{{Wikidata person|"))[1].split("}}")[0]
        except:
            continue
    print target

    targetitem = pywikibot.ItemPage(repo, target)
    targetitem.get()
    if targetitem.claims:
        if 'P1472' in targetitem.claims: # instance of
            print(targetitem.claims['P1472'][0].getTarget())
            print "{{Wikidata person|1="+target+"}}"
            target_text = page.text
            target_text = target_text.replace("{{Wikidata person|1="+target+"}}", "{{Creator:"+targetitem.claims['P1472'][0].getTarget()+"}}")
            target_text = target_text.replace("{{Wikidata person|"+target+"}}", "{{Creator:"+targetitem.claims['P1472'][0].getTarget()+"}}")
            print target_text
            page.text = target_text.strip()
            # text = raw_input("Save on Commons? ")
            # if text == 'y':
                # try:
            page.save("Changing from using Wikidata person to Creator")
                    # continue
                # except:
                    # print "That didn't work!"
                    # continue
            # else:
                # continue
        else:
            continue
    else:
        continue
