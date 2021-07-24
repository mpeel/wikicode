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

globe_item = pywikibot.ItemPage(repo, 'Q111')#Q12134')

wd_item = pywikibot.ItemPage(repo, 'Q718908')
item_dict = wd_item.get()
print(wd_item.title())
# print(item_dict['claims']['P625'])

coordinateclaim  = pywikibot.Claim(repo, u'P625')
coordinate = pywikibot.Coordinate(lat=-45, lon=202, precision=1.0, globe_item=globe_item,site=repo)
coordinateclaim.setTarget(coordinate)
print(coordinateclaim)
wd_item.addClaim(coordinateclaim, summary=u'Adding coordinate on Mars')
