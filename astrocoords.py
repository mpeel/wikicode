#!/usr/bin/python
# -*- coding: utf-8  -*-
# Migrate data from Commons to Wikidata
# Started 12 May 2018 by Mike Peel
from __future__ import unicode_literals

import pywikibot
import numpy as np
import time
import string
from pywikibot import pagegenerators
import urllib

commons = pywikibot.Site('commons', 'commons')
repo = commons.data_repository()  # this is a DataSite object

globe_item = pywikibot.ItemPage(repo, 'Q111') # Mars
# globe_item = pywikibot.ItemPage(repo, 'Q405') # Moon
# globe_item = pywikibot.ItemPage(repo, 'Q596') # Ceres


wd_item = pywikibot.ItemPage(repo, 'Q2083022')
item_dict = wd_item.get()
print(wd_item.title())

coordinateclaim  = pywikibot.Claim(repo, u'P625')
coordinate = pywikibot.Coordinate(lat=-1.95, lon=354.47, precision=0.01, globe_item=globe_item,site=repo)
coordinateclaim.setTarget(coordinate)
print(coordinateclaim)
wd_item.addClaim(coordinateclaim, summary=u'Adding coordinate on Moon')
