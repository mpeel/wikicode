#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Purge the cache for the list of candidates
# Mike Peel     20-July-2021      v1 - start
# Mike Peel     24-July-2021      v2 - configure
import pywikibot
meta = pywikibot.Site('meta', 'meta')
page = pywikibot.Page(meta,'Template:WMF elections candidate/2021/candidates gallery')
page.touch()
page.purge()
page = pywikibot.Page(meta,'Wikimedia Foundation elections/2021/Candidates')
page.touch()
page.purge()
