#!/usr/bin/python
# -*- coding: utf-8  -*-
# Collating various functions used by pi bot
# Mike Peel     20-Jan-2019      v1 - start

import pywikibot
import numpy as np
import time
import string
from pywikibot import pagegenerators


def check_if_category_has_contents(category, site=''):
	if site != '':
		if 'Category:' not in category:
			category = 'Category:'+category
		category = pywikibot.Category(site, category)

	pages = pagegenerators.CategorizedPageGenerator(category, recurse=False);
	for page in pages:
		return True
		exit()

	pages = pagegenerators.SubCategoriesPageGenerator(category, recurse=False);
	for page in pages:
		return True
		exit()

	return False


