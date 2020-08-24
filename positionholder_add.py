#!/usr/bin/python
# -*- coding: utf-8  -*-
# Add position holder template on Wikidata
# Mike Peel     14-Aug-2020      v1 - start

import pywikibot

wikidata_site = pywikibot.Site("wikidata", "wikidata")
repo = wikidata_site.data_repository()

page = pywikibot.Page(wikidata_site, 'User:Mike Peel/sandbox')

qids = []
for line in page.text.splitlines():
	if '[[' in line:
		qids.append(line.replace('|','').replace('[','').replace(']',''))
print(qids)

for qid in qids:
	page = pywikibot.Page(wikidata_site, 'Talk:'+qid)
	if 'PositionHolderHistory' in page.text:
		print('Already has template')
		continue
	if page.text == '':
		print('Page is empty')
	page.text = '{{PositionHolderHistory|id='+str(qid)+'}}\n' + page.text
	page.save(u"Adding PositionHolderHistory template")
	# exit()
