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

def getlist(category,maxdepth=10):

    catlist = []

    seen   = set(category)
    active = set(category)
    print active
    numsets = 0
    while active:
        next_active = set()
        for item in active:
            cat = pywikibot.Category(site,item)
            print cat.title()
            for image in cat.articles():
                if image.title() not in catlist:
                    catlist.append(image.title())

            # See if there are subcategories that we want to check in the future
            if numsets < maxdepth:
                for result in pagegenerators.SubCategoriesPageGenerator(cat, recurse=False):
                    if result.title() not in seen:
                        seen.add(result.title())
                        next_active.add(result.title())
        active = next_active
        numsets += 1
    # print catlist
    return catlist

prefix = 'wle/geoparks_'
print 'Fetch list 1'
cat1 = ['Category:Wiki Loves Earth 2018']
#cat1 = pywikibot.Category(site,'Category:Wiki Loves Earth 2018')
inputfile1=''#'wle/geoparks_cat1.txt'
#'Category:Images_from_Wiki_Loves_Earth_Biosphere_Reserves_2017')
#cat1 = pywikibot.Category(site,'Category:Biosphere_reserves_by_country')
# cat1 = pywikibot.Category(site,'Category:Photos_by_Mike_Peel_using_an_iPhone_5')
print 'Fetch list 2'
cat2 = ['Category:Geoparks']
#cat2 = pywikibot.Category(site,'Category:Geoparks')
inputfile2 = ''
#'Category:Images_from_Wiki_Loves_Earth_2017')
# cat2 = pywikibot.Category(site,'Category:Photos_by_Mike_Peel')


print 'Run through list 1'
# cat1_images = [image for image in cat1.articles(recurse=True)]
cat1_images = []
if inputfile1 != '':
    with open(inputfile1, mode='r') as infile:
        reader = csv.reader(infile)
        cat1_images = {rows[0] for rows in reader}
else:
    cat1_images = getlist(cat1, maxdepth=3)
    cat1_file = open(prefix+'cat1.txt', 'w')
    for item in cat1_images:
        cat1_file.write("%s\n" % item)
    cat1_file.close()

print "Done list 1"

print 'Run through list 2'
# cat2_images = [image for image in cat2.articles(recurse=True)]
cat2_images = []
if inputfile2 != '':
    with open(inputfile1, mode='r') as infile:
        reader = csv.reader(infile)
        cat2_images = {rows[0] for rows in reader}
else:
    cat2_images = getlist(cat2, maxdepth=10)
    # for image in cat2.articles(recurse=10):
    #     cat2_images.append(image.title())
    #     print str(i) + " - " + image.title()
    #     i += 1
    cat2_file = open(prefix+'cat2.txt', 'w')
    for item in cat2_images:
      cat2_file.write("%s\n" % item)
    cat2_file.close()

print "Done list 2"

print 'Comparing'
inboth = list(set(cat1_images) & set(cat2_images))

print inboth
inboth_file = open(prefix+'inboth.txt', 'w')
for item in inboth:
  inboth_file.write("%s\n" % item)
inboth_file.close()

infirstonly = list(set(cat1_images) - set(cat2_images))

infirstonly_file = open(prefix+'infirstonly.txt', 'w')
for item in infirstonly:
  infirstonly_file.write("%s\n" % item)
infirstonly_file.close()
