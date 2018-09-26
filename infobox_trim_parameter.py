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
    print page.title()
    if 'onlysourced' in page.text:
        print page.text
        target_text = page.text
        target_text = target_text.replace("| presentation=yes\n", "")
        target_text = target_text.replace("| presentation=\n", "")
        if page.text != target_text.strip():
            page.text = target_text.strip()
            print page.text
            # text = raw_input("Save? ")
            # if text == 'y':
            try:
                page.save("Trimming presentation parameter from poster")
                continue
            except:
                print "That didn't work!"
                continue
            # else:
                # continue


    # if 'slides_size' not in target_text:
    #     lines = target_text.splitlines()
    #     insertline = 0
    #     i = 0
    #     for line in lines:
    #         i += 1
    #         if "| slides" in line:
    #             insertline = i
    #     lines[insertline:insertline] = ["| slides_caption=Placeholder: replace with slides/image/video"]
    #     lines[insertline:insertline] = ["| slides_size=150px"]
    #     target_text = "\n".join(lines)
    #     print target_text
    #     if page.text != target_text.strip():
    #         page.text = target_text.strip()
    #         # text = raw_input("Save? ")
    #         # if text == 'y':
    #         try:
    #             page.save("Adding slides_size and slides_caption parameters")
    #             continue
    #         except:
    #             print "That didn't work!"
    #             continue
    #         # else:
    #         #     continue
