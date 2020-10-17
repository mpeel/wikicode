#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Touch categories on Commons
# Mike Peel     23-Sep-2018      v1 - start
# Mike Peel     02-Oct-2020      Specific for WLM Brazil

import pywikibot
from pywikibot import pagegenerators

# Connect to commons
commons = pywikibot.Site('commons', 'commons')
catname = 'Category:Uses of MonumentID for Brazil with no picture on Wikidata'

cat = pywikibot.Category(commons,catname)
print(cat)
i = 0
first = ''
for result in pagegenerators.CategorizedPageGenerator(cat, recurse=False):
	result.touch()
