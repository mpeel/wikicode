from __future__ import unicode_literals
#!/usr/bin/python
# -*- coding: utf-8  -*-
# Add some text to a wiki page
# Mike Peel     11-Jul-2017     v1 - initial version

import pywikibot
import numpy as np
import time
import string
from pywikibot import pagegenerators
import time
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

def addtext(site, project, toedit, text, othertext='',rate=10, trialrun=0):

    site = pywikibot.Site('commons', 'commons')
    repo = site.data_repository()  # this is a DataSite object

    for item in toedit:
        item = item.decode('utf-8').strip()
        print item
        page = pywikibot.Page(site, item)
        if page.text == '':
            print "Error - page is empty!"
        elif text not in page.text:
            if (othertext == '') or (othertext not in page.text):
                if trialrun:
                    print ' - To edit'
                else:
                    page.text = page.text + "\n" + text
                    page.save(u"Adding " + text)
