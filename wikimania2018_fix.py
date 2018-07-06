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

site = pywikibot.Site('wikimania2018', 'wikimania2018')
repo = site.data_repository()

template = pywikibot.Page(site, 'Template:Session')

uses = template.embeddedin(namespaces='0')

whitelist = set('abcdefghijklmnopqrstuvwxy ABCDEFGHIJKLMNOPQRSTUVWXYZ 1234567890')
alllinks = ''
for page in uses:
    print page.title()
    shortname = ''.join(filter(whitelist.__contains__, page.title().replace('Program/','')))
    shortname = shortname.split()
    try:
        shortname = shortname[0:4]
    except:
        print "Trimming string didn't work!"
    shortname = '_'.join(shortname)
    target_text = page.text
    if 'poster=yes' not in target_text and 'Poster reception' not in page.title() and 'photo exhibition' not in page.title() and '| notes =' not in target_text:
        datetime = (target_text.split("| datetime = "))[1].split("\n")[0].strip()
        location = (target_text.split("| location = "))[1].split("\n")[0].strip()
        alllinks = alllinks + '\n*' + datetime + ', ' + location + ', https://etherpad.wikimedia.org/p/Wikimania2018-' + shortname
        lines = target_text.splitlines()
        insertline = 0
        i = 0
        for line in lines:
            i += 1
            if "| slides_caption" in line:
                insertline = i
        lines[insertline:insertline] = ['| notes = [https://etherpad.wikimedia.org/p/Wikimania2018-' + shortname + ' Etherpad]  <small>([https://etherpad.wikimedia.org/p/Wikimania2018-template template])</small>']
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

print alllinks


    # # This was for the posters
    # print page.text
    # target_text = page.text
    # target_text = target_text.replace("| presentation=yes\n", "")
    # target_text = target_text.replace("| presentation=\n", "")
    # if page.text != target_text.strip():
    #     page.text = target_text.strip()
    #     print page.text
    #     # text = raw_input("Save? ")
    #     # if text == 'y':
    #     try:
    #         page.save("Trimming presentation parameter from poster")
    #         continue
    #     except:
    #         print "That didn't work!"
    #         continue
    #     # else:
    #         # continue


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
