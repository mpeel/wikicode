from __future__ import unicode_literals
#!/usr/bin/python
# -*- coding: utf-8  -*-
# Check the WLM 2016 UK categories for inconsistencies
# Mike Peel		04-Sep-2016		v1 - initial version

def diff(first, second):
    second = set(second)
    return [item for item in first if item not in second]

import pywikibot
import numpy as np
import time
import string
from pywikibot import pagegenerators

site = pywikibot.Site('commons', 'commons')
repo = site.data_repository()  # this is a DataSite object

maincat = pywikibot.Category(site,u'Category:Images from Wiki Loves Monuments 2016 in the United Kingdom')
encat = pywikibot.Category(site,u'Category:Images from Wiki Loves Monuments 2016 in England')
cycat = pywikibot.Category(site,u'Category:Images from Wiki Loves Monuments 2016 in Wales')
scocat = pywikibot.Category(site,u'Category:Images from Wiki Loves Monuments 2016 in Scotland')
nicat = pywikibot.Category(site,u'Category:Images from Wiki Loves Monuments 2016 in Northern Ireland')

imagelist = []
for image in encat.articles():
	imagelist.append(image)
for image in cycat.articles():
	imagelist.append(image)
for image in scocat.articles():
	imagelist.append(image)
for image in nicat.articles():
	imagelist.append(image)

mainlist = []
for image in maincat.articles():
	mainlist.append(image)

report = ""
diff1 = diff(imagelist, mainlist)
diff2 = diff(mainlist, imagelist)
report = "Files only in a subcat and not the main cat:\n\n"
for i in range(0,len(diff1)):
	report = report + str(diff1[i]).replace('[[commons','* [[')+"\n"
report = report + u"----\n"
report = report + "Files only in the main cat and not in a subcat:\n\n"
for i in range(0,len(diff2)):
	report = report + str(diff2[i]).replace('[[commons','* [[')+"\n"

# Get the page we want to save the report to
page = pywikibot.Page(site, u"User:Mike Peel/WLM UK check")
# print page.text

print report

page.text = report
page.save(u"Updating")
# print report