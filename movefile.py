#!/usr/bin/python
# -*- coding: utf-8  -*-
# Move files
# Mike Peel     15-Apr-2020      v1 - start

from __future__ import unicode_literals

import pywikibot
from pywikibot import pagegenerators

commons = pywikibot.Site('commons', 'commons')
repo = commons.data_repository()

filename = 'File:Colonia del Sacramento 2016 016.jpg'
filename_new = 'File:Colonia del Sacramento 2016 016 - Ford Model T.jpg'
page = pywikibot.Page(commons, filename)
linkeduses = page.linkedPages()
# for use in linkeduses:
# 	print(use.title())
# exit()
page.move(filename_new,reason="Include subject in filename",movetalk=True,noredirect=True)
