from __future__ import unicode_literals
#!/usr/bin/python
# -*- coding: utf-8  -*-
# A script to add commons as another site where commons already exists
# Mike Peel		9-Feb-2016		v1 - initial version

import pywikibot
import numpy as np
import time
import string
from pywikibot import pagegenerators

# site = pywikibot.Site('en', 'wikipedia')
site = pywikibot.Site('commons', 'commons')
# pagename = input('Page name: ')
# page = pywikibot.Page(site, pagename)
# item = pywikibot.ItemPage.fromPage(page)

repo = site.data_repository()  # this is a DataSite object
# pagename = raw_input("Wikidata ID: ")
pagename = 'Q1200061'
print pagename
item = pywikibot.ItemPage(repo, pagename)
item.get()
# print item.sitelinks

commonscat_property = item.claims['P373'][0].getTarget()
print 'Commonscat is currently ' + str(commonscat_property)
if 'commonswiki' in item.sitelinks:
	commonscat_sitelink = item.sitelinks['commonswiki']
else:
	commonscat_sitelink = ''
print 'Commonscat sitelink is currently ' + str(commonscat_sitelink)

if 'enwiki' in item.sitelinks:
	en_sitelink = item.sitelinks['enwiki']
else:
	en_sitelink = ''
print 'en sitelink is currently ' + str(en_sitelink)


if ('Category:'+commonscat_property == commonscat_sitelink):
	print 'Both are the same!'
else:
	print 'These are different!'

if (commonscat_sitelink == ''):
	print 'Sitelink is empty!'

page = pywikibot.Page(site, 'Category:'+commonscat_property)
# page = pywikibot.Page(site, en_sitelink)
interwikis = page.langlinks()
start = "[[wikipedia:"
end = "]]"
text = page.text
print text
for vals in interwikis:
	# print vals
	val = str(vals)
	interwiki = string.split(val[val.find(start)+len(start):val.rfind(end)], ':')
	site = interwiki[0]
	value = interwiki[1]
	print 'Site: ' + str(site) + ', value: ' + value
	if site+'wiki' in item.sitelinks:
		print item.sitelinks[site+'wiki']
		text.decode("utf-8").remove(u'[['+str(site)+':'+item.sitelinks[site+'wiki']).encode("utf-8")
	else:
		print 'Site match not found'

print text

# print page.text
# print interwikis

