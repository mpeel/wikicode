#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Touch categories on Commons
# Mike Peel     23-Sep-2018      v1 - start

# Import modules
import pywikibot
from pywikibot import pagegenerators

# Connect to commons
commons = pywikibot.Site('commons', 'commons')

template = pywikibot.Page(commons, 'Template:Mechanical Curator image')
pages = template.embeddedin()
for result in pages:
	print(result.title())
	result.touch()
