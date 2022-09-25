#!/usr/bin/python
# -*- coding: utf-8  -*-
# Make corrections to labels
# Mike Peel     24-Oct-2020      v1 - start
import pywikibot
from pywikibot import pagegenerators

wikidata_site = pywikibot.Site("wikidata", "wikidata")
repo = wikidata_site.data_repository()

replacements = [
{'lang': 'cs', 'string': 'Silnice I/', 'replacement': 'silnice I/'},\
{'lang': 'cs', 'string': 'Silnice II/', 'replacement': 'silnice II/'},\
{'lang': 'cs', 'string': 'Silnice III/', 'replacement': 'silnice III/'},\
{'lang': 'en', 'string': 'Route I/', 'replacement': 'route I/'},\
{'lang': 'en', 'string': 'Route II/', 'replacement': 'route II/'},\
{'lang': 'sk', 'string': 'Cesta I. triedy ', 'replacement': 'cesta I. triedy '},\
{'lang': 'sk', 'string': 'Cesta II. triedy ', 'replacement': 'cesta II. triedy '},\
{'lang': 'de', 'string': 'Cesta I. triedy ', 'replacement': 'cesta I. triedy '},\
{'lang': 'de', 'string': 'Cesta II. triedy ', 'replacement': 'cesta II. triedy '},\
{'lang': 'lmo', 'string': 'Strada de prima class ', 'replacement': 'strada de prima class '},\
{'lang': 'lmo', 'string': 'Strada de segonda class ', 'replacement': 'strada de segonda class '},\
{'lang': 'pl', 'string': 'Droga krajowa nr', 'replacement': 'droga krajowa nr'},\
{'lang': 'pl', 'string': 'Droga ekspresowa', 'replacement': 'droga ekspresowa'},\
{'lang': 'cs', 'string': 'Dálnice D', 'replacement': 'dálnice D'},\
{'lang': 'sk', 'string': 'Diaľnica D', 'replacement': 'diaľnica D'},\
{'lang': 'cs', 'string': 'Rychlostní silnice R', 'replacement': 'rychlostní silnice R'},\
{'lang': 'sk', 'string': 'Rýchlostná cesta R', 'replacement': 'rýchlostná cesta R'},\
{'lang': 'de', 'string': 'Rýchlostná cesta R', 'replacement': 'rýchlostná cesta R'},\
{'lang': 'cs', 'string': 'Železniční trať ', 'replacement': 'železniční trať '},\
{'lang': 'sk', 'string': 'Železničná trať ', 'replacement': 'železničná trať '},\
{'lang': 'pl', 'string': 'Linia kolejowa ', 'replacement': 'linia kolejowa '},\
{'lang': 'en', 'string': 'Railway line ', 'replacement': 'railway line '},\
{'lang': 'cs', 'string': 'Evropská silnice ', 'replacement': 'evropská silnice '},\
{'lang': 'cs', 'string': 'Mezinárodní silnice ', 'replacement': 'mezinárodní silnice '},\
{'lang': 'sk', 'string': 'Európska cesta ', 'replacement': 'európska cesta '},\
{'lang': 'es', 'string': 'Ruta europea ', 'replacement': 'ruta europea '},\
{'lang': 'fr', 'string': 'Route europeenne ', 'replacement': 'route europeenne '},\
{'lang': 'lmo', 'string': 'Strada europea ', 'replacement': 'strada europea '},\
{'lang': 'pl', 'string': 'Trasa europejska ', 'replacement': 'trasa europejska '},\
{'lang': 'pt', 'string': 'Estrada europeia ', 'replacement': 'estrada europeia '},\
{'lang': 'pt-br', 'string': 'Estrada europeia ', 'replacement': 'estrada europeia '},\
{'lang': 'ro', 'string': 'Drumul european ', 'replacement': 'drumul european '},\

#     uk aliases beginning with "Автошлях "
#     cs aliases beginning with "Železniční trať "
#     cs aliases beginning with "Trať "
#     pl aliases beginning with "Linia kolejowa "
]

debug = True
for replacement in replacements:
	savemessage = 'Change ' + replacement['lang'] + ' label to '
	query = 'SELECT ?item ?label'\
	'WHERE'\
	'{'\
	'  SERVICE wikibase:mwapi'\
	'  {'\
	'    bd:serviceParam wikibase:endpoint "www.wikidata.org" .'\
	'    bd:serviceParam wikibase:api "Generator" .'\
	'    bd:serviceParam mwapi:generator "search" .'\
	'    bd:serviceParam mwapi:gsrsearch \'inlabel:"'+replacement['string']+'@'+replacement['lang']+'"\' .'\
	'    bd:serviceParam mwapi:gsrlimit "max".'\
	'    ?item wikibase:apiOutputItem mwapi:title.'\
	'  }'\
	'  ?item rdfs:label ?label'\
	'  FILTER (LANG(?label) = "'+replacement['lang']+'")'\
	'  FILTER STRSTARTS(?label, "'+replacement['string']+'")'\
	'}'
	print(query)
	count = 1
	while count > 0:

		pages = pagegenerators.WikidataSPARQLPageGenerator(query, site=repo)
		count = 0
		print('Running...')

		for wd_item in pages:
			count += 1
			print(wd_item)
			# wd_item = pywikibot.ItemPage.fromPage(page)
			item_dict = wd_item.get()
			qid = wd_item.title()
			oldlabel = item_dict['labels'][replacement['lang']]
			newlabel = oldlabel.replace(replacement['string'],replacement['replacement'],1)
			newlabels = {replacement['lang']: newlabel}
			test = 'y'
			if debug:
				test = input('Save?')
			if test == 'y':
				try:
					wd_item.editLabels(labels=newlabels, summary=savemessage + newlabel)
					sleep(1)
				except:
					print("Something went wrong")
