#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Touch categories on Commons
# Mike Peel     19-Sep-2018      v1 - start

# Import modules
import pywikibot
from pywikibot import pagegenerators
from pywikibot.data import api
import numpy as np
import requests

# You may need to enforce the use of utf-8
import sys
reload(sys)
sys.setdefaultencoding('UTF8')

# Connect to commons
commons = pywikibot.Site('commons', 'commons')

catname = 'Category:Uses of Wikidata Infobox with no instance of'

cat = pywikibot.Category(commons,catname)

i = 0
for result in pagegenerators.SubCategoriesPageGenerator(cat, recurse=False):
    result.touch()
    i += 1
    print i
