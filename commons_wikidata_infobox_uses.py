#!/usr/bin/python
# -*- coding: utf-8  -*-
# Get a list of wikidata infobox uses from Commons
# Mike Peel     26-Jun-2018     v1 - initial version
import pywikibot
import numpy as np
import time
import string
from pywikibot import pagegenerators
import codecs

site = pywikibot.Site('commons', 'commons')
repo = site.data_repository()  # this is a DataSite object

cat = pywikibot.Category(site,'Category:Uses of Wikidata Infobox')
print cat
outputfile = codecs.open('commons_wikidata_infobox_uses.csv', "w", "utf-8")

uses = cat.members(recurse=False);
# i = 0
for use in uses:
    # i++
    # if i % 1000:
    #     print i
    outputfile.write(use.title()+"\n")

outputfile.close()