from __future__ import unicode_literals
#!/usr/bin/python
# -*- coding: utf-8  -*-
# Get a list of my photos from Wikimedia Commons
# Mike Peel     17-Jul-2016     v1 - initial version

import pywikibot
import numpy as np
import time
import string
from pywikibot import pagegenerators
import time
import sys


reload(sys)
sys.setdefaultencoding('utf-8')

site = pywikibot.Site('commons', 'commons')
repo = site.data_repository()  # this is a DataSite object

print 'Fetch list 1'
cat1 = pywikibot.Category(site,'Category:Images_from_Wiki_Loves_Earth_Biosphere_Reserves_2017')
#cat1 = pywikibot.Category(site,'Category:Biosphere_reserves_by_country')
# cat1 = pywikibot.Category(site,'Category:Photos_by_Mike_Peel_using_an_iPhone_5')
print 'Fetch list 2'
cat2 = pywikibot.Category(site,'Category:Images_from_Wiki_Loves_Earth_2017')
# cat2 = pywikibot.Category(site,'Category:Photos_by_Mike_Peel')


print 'Run through list 1'
# cat1_images = [image for image in cat1.articles(recurse=True)]

cat1_images = []
i = 0
for image in cat1.articles(recurse=4):
    cat1_images.append(image.title())
    print str(i) + " - " + image.title()
    i += 1
cat1_file = open('cat1.txt', 'w')
for item in cat1_images:
  cat1_file.write("%s\n" % item)
cat1_file.close()

print "Done list 1"

print 'Run through list 2'
# cat2_images = [image for image in cat2.articles(recurse=True)]
cat2_images = []
i = 0
for image in cat2.articles(recurse=10):
    cat2_images.append(image.title())
    print str(i) + " - " + image.title()
    i += 1
cat2_file = open('cat2.txt', 'w')
for item in cat2_images:
  cat2_file.write("%s\n" % item)
cat2_file.close()

print "Done list 2"

print 'Comparing'
inboth = list(set(cat1_images) & set(cat2_images))

print inboth
inboth_file = open('inboth.txt', 'w')
for item in inboth:
  inboth_file.write("%s\n" % item)
inboth_file.close()

infirstonly = list(set(cat1_images) - set(cat2_images))

infirstonly_file = open('infirstonly.txt', 'w')
for item in infirstonly:
  infirstonly_file.write("%s\n" % item)
infirstonly_file.close()
