#!/usr/bin/python
# -*- coding: utf-8  -*-
# Marking submissions that have been declined as closed
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
# reload(sys)
# sys.setdefaultencoding('utf-8')

site = pywikibot.Site('wikimania', 'wikimania')
repo = site.data_repository()

template = pywikibot.Page(site, 'Template:2019:Open submission')

uses = template.embeddedin()

# whitelist = set('abcdefghijklmnopqrstuvwxy ABCDEFGHIJKLMNOPQRSTUVWXYZ 1234567890')
# alllinks = ''
count = 0
for page in uses:
    if ' Form' not in page.title() and ' form' not in page.title():
        print(page.title())
        count += 1
        target_text = page.text
        target_text = target_text.replace('{{Template:2019:Open submission}}','{{Template:2019:Closed submission}}')
        if page.text != target_text.strip():
            page.text = target_text.strip()
            print(target_text)
            # text = input("Save? ")
            # if text == 'y':
            page.save("Marking submission as closed")
                # continue
                # except:
                #     print("That didn't work!")
                #     continue
print(count)
