#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Touch categories on Commons
# Mike Peel     23-Sep-2018      v1 - start

# Import modules
import pywikibot

# Connect to commons
commons = pywikibot.Site('commons', 'commons')

catname = 'Category:Uses of Wikidata Infobox with no instance of'
cat = pywikibot.Category(commons,catname)

i = 0
for result in pagegenerators.SubCategoriesPageGenerator(cat, recurse=False):
    result.touch()
    i += 1
    print i
