#!/usr/bin/python
# -*- coding: utf-8  -*-
# Make corrections to labels
# Mike Peel     24-Oct-2020      v1 - start
import pywikibot
from pywikibot import pagegenerators

wikidata_site = pywikibot.Site("wikidata", "wikidata")
repo = wikidata_site.data_repository()

lang = 'lb'
string = 'chemesch Verbindung'
replacement = 'cheemesch Verbindung'
savemessage = 'Change ' + lang + ' label to '
debug = False
query = 'SELECT '\
'	?search '\
'	?item ?itemLabel ?itemDescription '\
'	?instanceof ?instanceofLabel'\
' WHERE'\
' {'\
'	 VALUES ?text { "'+string+'" }'\
'	 BIND ( CONCAT(?text, \' hasdescription:'+lang+' -inlabel:"\', ?text, \'"\') as ?search  ) '\
'	 SERVICE wikibase:mwapi'\
'	 {'\
'		 bd:serviceParam wikibase:api "Search" .'\
'		 bd:serviceParam wikibase:endpoint "www.wikidata.org" .'\
'		 bd:serviceParam mwapi:srnamespace "0" .'\
'		 bd:serviceParam mwapi:srsearch ?search .'\
'		 ?item wikibase:apiOutputItem mwapi:title.'\
'	 }'\
'	 FILTER EXISTS {   ?item schema:description ?desc . '\
'										 FILTER( lang(?desc)="'+lang+'" && CONTAINS( ?desc, ?text) ) '\
'									}'\
'	 OPTIONAL {?item wdt:P31 wd:instanceof }'\
'	 SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],'+lang+'" .}'\
' }'\
' ORDER BY deSC(?check_text)'
print(query)
count = 100
while count > 0:

	pages = pagegenerators.WikidataSPARQLPageGenerator(query, site=repo)
	count = 0

	for wd_item in pages:
		count += 1
		print(wd_item)
		# wd_item = pywikibot.ItemPage.fromPage(page)
		item_dict = wd_item.get()
		qid = wd_item.title()
		olddescription = item_dict['descriptions'][lang]
		newdescription = olddescription.replace(string,replacement)
		newdescriptions = {lang: newdescription}
		print(newdescriptions)
		test = 'y'
		if debug:
			test = input('Save?')
		if test == 'y':
			try:
				wd_item.editDescriptions(newdescriptions, summary=savemessage + newdescription)
			except:
				print("Something went wrong")
			