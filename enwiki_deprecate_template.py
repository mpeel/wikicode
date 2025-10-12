#!/usr/bin/python
# -*- coding: utf-8  -*-
# Deprecate templates from enwiki
# Mike Peel     12-Oct-2025      v1 - start
import pywikibot
from pywikibot import pagegenerators

# Config
templatename = 'Authority control (arts)'
newname = 'Authority control|show=arts'
debug = True

site = pywikibot.Site('en', 'wikipedia')
targettemplate = pywikibot.Page(site, 'Template:'+templatename)
targetpages = targettemplate.embeddedin()
for page in targetpages:
	print("https://en.wikipedia.org/wiki/"+page.title().replace(' ','_'))
	page_old = page.text
	page.text = page.text.replace('{{'+templatename+'}}','{{'+newname+'}}')
	if page.text != page_old:
		if debug == True:
			print(page.text)
			test = input('Save?')
		else:
			test = 'y'
		if test != 'n':
			page.save('Migrating from [[Template:' + templatename + ']] to [[Template:' + newname + ']]')#,minor=False)
