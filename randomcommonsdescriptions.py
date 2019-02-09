#!/usr/bin/python
# -*- coding: utf-8  -*-
# Fetch N random articles, and print their descriptions
# Mike Peel     11-Dec-2017     Initial version

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
checked = 0
error = 0
numfound = 0
text = "This is a sample of " + str(num) + " random images and descriptions that could be copied to captions.\n\n"
while numfound < num:
    for page in pagegenerators.RandomPageGenerator(total=10, site=site, namespaces=[6]):
        checked += 1
        # print page
        filetext = page.get()
        caption = ""
        if '{{en|1=' in filetext:
            caption = filetext.split('{{en|1=')[1].split('}}')[0]
        elif '{{en|' in filetext:
            caption = filetext.split('{{en|')[1].split('}}')[0]
        if caption != '':
            if len(caption) < 200:
                numfound += 1
                print page.title() + "|" + caption
                if numfound >= num:
                    print 'checked ' + str(checked) + " files"
                    exit()
