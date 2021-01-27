#!/usr/bin/python
# -*- coding: utf-8  -*-
# Copy human names from selected other languages to English
# Mike Peel     21-Dec-2020      v1

from __future__ import unicode_literals

import pywikibot
import numpy as np
import time
import string
from pywikibot import pagegenerators
import urllib

maxnum = 1000
nummodified = 0
stepsize =  10000
maximum = 4000000
numsteps = int(maximum / stepsize)
debug = False

langs = 'en-ca,en-gb,de,fr,es,pt,nl,it,sv,af,an,ast,bar,bm,br,ca,co,cs,cy,da,de-at,de-ch,eo,et,eu,fi,frc,frp,fur,ga,gd,gl,gsw,hr,ia,id,ie,io,jam,kab,kg,lb,li,lij,lt,mg,mi,nap,nb,nds,nds-nl,nn,nrm,min,ms,oc,pap,pcd,pms,prg,pt-br,rgn,rm,ro,sc,scn,sco,sk,sl,sq,sr-el,sw,tr,vec,vi,vls,vmf,vo,wa,wo,zu'
langs_exclude = 'en,ru'
# Q159 = Russia, Q15180 = Soviet Union, Q17=Japan
country_qid_exclude = ['Q159', 'Q15180','Q17']

def isEnglish(s):
	try:
		s.encode(u'latin1')
	except UnicodeEncodeError:
		return False
	else:
		try:
			s.encode(u'latin2')
		except UnicodeEncodeError:
			return False
		else:
			if any(char.isdigit() for char in s):
				return False
			else:
				return True

wikidata_site = pywikibot.Site("wikidata", "wikidata")
repo = wikidata_site.data_repository()  # this is a DataSite object

lang_list = langs.split(',')
lang_sparql = ''
for l in lang_list:
	lang_sparql = lang_sparql + "'"+l+"',"
lang_sparql = lang_sparql[:-1]

lang_list_exclude = langs_exclude.split(',')
lang_exclude_sparql = ''
for l in lang_list_exclude:
	lang_exclude_sparql = lang_exclude_sparql + "'"+l+"',"
lang_exclude_sparql = lang_exclude_sparql[:-1]

lang_combine_sparql = lang_sparql + "," + lang_exclude_sparql

for i in range(0,numsteps):
	print('Starting at ' + str(i*stepsize))

	query = "SELECT ?item\n"\
	"WITH { \n"\
	"  SELECT ?item WHERE {\n"\
	"    ?item wdt:P31 wd:Q5 . \n"\
	'  } LIMIT '+str(stepsize)+' OFFSET '+str(i*stepsize)+'\n'\
	"} AS %items\n"\
	"WHERE {\n"\
	"  INCLUDE %items .\n"\
	"    SERVICE wikibase:label { bd:serviceParam wikibase:language \""+lang_combine_sparql+"\". }\n"\
	"    FILTER(NOT EXISTS {\n"\
	"        ?item rdfs:label ?lang_label.\n"\
	"        FILTER(LANG(?lang_label) in ("+lang_exclude_sparql+"))\n"\
	"    })\n"\
	"    FILTER(EXISTS {\n"\
	"        ?item rdfs:label ?lang_label.\n"\
	"        FILTER(LANG(?lang_label) in ("+lang_sparql+"))\n"\
	"    })\n"\
	"}"

	print(query)

	generator = pagegenerators.WikidataSPARQLPageGenerator(query, site=wikidata_site)
	for page in generator:
		# Get the page
		item_dict = page.get()
		qid = page.title()
		print("\nhttps://www.wikidata.org/wiki/" + qid)

		skip = False
		# Check for excluded P27 values
		try:
			p27 = item_dict['claims']['P27']
			for clm in p27:
				if clm.getTarget().title() in country_qid_exclude:
					skip = True
		except:
			null = 0
		if skip == True:
			# input('Hi')
			continue

		# Check for excluded P27 values within P19 places of birth
		try:
			p27 = item_dict['claims']['P19']
			for clm in p27:
				val = clm.getTarget()
				p27 = val['claims']['P27']
				for clm in p27:
					if clm.getTarget().title() in country_qid_exclude:
						skip = True
		except:
			null = 0
		if skip == True:
			input('Hi')
			continue

		# Check that it hasn't already got an en label
		try:
			label = item_dict['labels']['en']
			print(label)
			print("That shouldn't have worked, continuing")
			continue
		except:
			print('No English label')

		# Get the new label
		label = ''
		labellang = ''
		for val in lang_list:
			if label != '':
				break
			try:
				if isEnglish(item_dict['labels'][val]):
					label = item_dict['labels'][val]
					labellang = val
			except:
				continue

		if label != '':
			if debug:
				print(label)
				print(labellang)
				test = input('Save?')
			else:
				test = 'y'
			if test == 'y':
				try:
					page.editLabels(labels={'en': label}, summary=u'Copy ' + labellang + " label to en label")
					nummodified += 1
				except:
					print('Edit failed')

		if nummodified >= maxnum:
			print('Reached the maximum of ' + str(maxnum) + ' entries modified, quitting!')
			exit()

print('Done! Edited ' + str(nummodified) + ' entries')
		 
# EOF