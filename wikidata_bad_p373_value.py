#!/usr/bin/python3
# -*- coding: utf-8  -*-
# Remove P373 values
# Mike Peel     05-Feb-2020      v1 - start

import pywikibot
import numpy as np
from pywikibot import pagegenerators
from pibot_functions import *

wikidata_site = pywikibot.Site("wikidata", "wikidata")
repo = wikidata_site.data_repository()

query = "SELECT DISTINCT ?item ?itemLabel WHERE {{     ?statement wikibase:hasViolationForConstraint wds:P373-B6CB2058-B6B7-4E4D-98D3-ED2C4F3D7184 .     ?item ?p ?statement .     FILTER( ?item NOT IN ( wd:Q4115189, wd:Q13406268, wd:Q15397819 ) ) . }}"

# query = "SELECT DISTINCT ?item ?itemLabel ?count ?sample1  ?sample2  ?exception\n"\
# "WITH {\n"\
# "	SELECT ?formatter WHERE {\n"\
# "		OPTIONAL { wd:P373 wdt:P1630 ?formatter }\n"\
# "	} LIMIT 1\n"\
# "} AS %formatter\n"\
# "WHERE\n"\
# "{\n"\
# "	{\n"\
# "		SELECT ?item (COUNT(?value) AS ?count) (MIN(?value) AS ?sample1) (MAX(?value) AS ?sample2) {\n"\
# "			?item wdt:P373 ?val .\n"\
# "			INCLUDE %formatter .\n"\
# "			BIND( IF( BOUND( ?formatter ), URI( REPLACE( ?formatter, '\\\\$1', ?val ) ), ?val ) AS ?value ) .\n"\
# "		} GROUP BY ?item HAVING ( ?count > 1 ) LIMIT 100\n"\
# "	} .\n"\
# "	OPTIONAL {\n"\
# "		wd:P373 p:P2302 [ ps:P2302 wd:Q19474404; pq:P2303 ?exc ] .\n"\
# "		FILTER( ?exc = ?item ) .\n"\
# "	} .\n"\
# "	BIND( BOUND( ?exc ) AS ?exception ) .\n"\
# '	SERVICE wikibase:label { bd:serviceParam wikibase:language "en" } .\n'\
# "}\n"\
# "ORDER BY DESC(?count)"


usereport = True
candidates = []
if usereport:
	reportpage = pywikibot.Page(repo, 'Wikidata:Database reports/Constraint violations/P373')
	text = reportpage.get()
	text = text.split('== "Single value" violations ==')[1].split('== "Commons link" violations ==')[0]
	lines = text.splitlines()
	for line in lines:
		try:
			qid = line.split('* [[')[1].split(']]')[0]
			# print(qid)
			candidates.append(qid)
		except:
			continue
else:
	print(query)
	generator = pagegenerators.WikidataSPARQLPageGenerator(query, site=wikidata_site)

# for page in generator:
for pageid in candidates:
	page = pywikibot.ItemPage(repo, pageid)
	item_dict = ''
	p373cat = ''
	candidate_item_dict = ''

	# Get the target item
	print('\n\n')
	try:
		item_dict = page.get()
	except:
		continue
	qid = page.title()
	print("\nhttp://www.wikidata.org/wiki/" + qid)
	
	try:
		sitelink = get_sitelink_title(item_dict['sitelinks']['commonswiki'])
		print('http://commons.wikimedia.org/wiki/'+sitelink.replace(' ','_'))
	except:
		print('No sitelink')
		# continue

	has_p910 = False
	try:
		existing_id = item_dict['claims']['P910']
		print('P910 exists, following that.')
		for clm2 in existing_id:
			candidate_item = clm2.getTarget()
			candidate_item_dict = candidate_item.get()
			print(candidate_item.title())
			qid2 = candidate_item.title()
			has_p910 = True
	except:
		null = 0

	try:
		sitelink = get_sitelink_title(candidate_item_dict['sitelinks']['commonswiki'])
		print('http://commons.wikimedia.org/wiki/'+sitelink.replace(' ','_'))
	except:
		print('No sitelink')
		continue

	# For the topic item
	try:
		p373 = item_dict['claims']['P373']
		for clm in p373:
			val = clm.getTarget()
			p373cat = u"Category:" + val
			if p373cat != sitelink:
				try:
					print(item_dict['labels']['en'])
				except:
					print('')
				try:
					print(item_dict['descriptions']['en'])
				except:
					print('')
				print('Remove P373?')
				print(' http://www.wikidata.org/wiki/'+qid)
				print('http://commons.wikimedia.org/wiki/' + str(p373cat).replace(' ','_'))
				test = input('OK?')
				if test == 'y':
					savemessage = "Remove incorrect P373 value"# that doesn't match the sitelink"
					# print(savemessage)
					page.removeClaims(clm,summary=savemessage)
	except:
		null = 1

	# ... and for the category item
	if has_p910:
		try:
			p373 = candidate_item_dict['claims']['P373']
			for clm in p373:
				val = clm.getTarget()
				p373cat = u"Category:" + val
				if p373cat != sitelink:
					try:
						print(candidate_item_dict['labels']['en'])
					except:
						print('')
					try:
						print(candidate_item_dict['descriptions']['en'])
					except:
						print('')
					print('Remove P373?')
					print(' http://www.wikidata.org/wiki/'+qid2)
					print('http://commons.wikimedia.org/wiki/' + str(p373cat).replace(' ','_'))
					test = input('OK?')
					if test == 'y':
						savemessage = "Remove incorrect P373 value"# that doesn't match the sitelink"
						# print(savemessage)
						candidate_item.removeClaims(clm,summary=savemessage)
		except:
			null = 2
# EOF