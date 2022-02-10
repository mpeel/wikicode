# !/usr/bin/python
# -*- coding: utf-8  -*-
# Check for consistency in commons category usage
# Mike Peel     01-Mar-2018      v1 - start

from __future__ import unicode_literals

import pywikibot
import numpy as np
import time
import string
from pywikibot import pagegenerators
import urllib
from database_login import *
from pibot_functions import *
import time

# mydb = mysql.connector.connect(
#   host=database_host,
#   user=database_user,
#   passwd=database_password,
#   database=database_database
# )
# mycursor = mydb.cursor()

maxnum = 10000
nummodified = 0

wikidata_site = pywikibot.Site("wikidata", "wikidata")
repo = wikidata_site.data_repository()  # this is a DataSite object
commons = pywikibot.Site('commons', 'commons')
langcode = 'es'#'pl'
# langcode = 'simple'
# langcode = 'fr'
# langcode = 'pt'
# enwp = pywikibot.Site('en', 'wikipedia')
# enwp = pywikibot.Site('meta', 'meta')
# enwp = pywikibot.Site('es', 'wikipedia')
# enwp = pywikibot.Site('sv', 'wikipedia')
# enwp = pywikibot.Site('nl', 'wikipedia')
# enwp = pywikibot.Site('pl', 'wikipedia')
enwp = pywikibot.Site(langcode, 'wikipedia')
debug = 1
trip = 1
templates = ['commonscat', 'Commonscat', 'commonscategory', 'Commonscategory', 'commons category', 'Commons category', 'commons cat', 'Commons cat', 'commons_category', 'Commons_category', 'commons_cat', 'Commons_cat', 'Commons category-inline', 'commons category-inline', 'Commons cat-inline', 'commons cat-inline', 'commonscat-inline', 'Commonscat-inline', 'Commons category inline', 'commons category inline', 'commons-cat-inline', 'Commons-cat-inline', 'Commons cat inline', 'commons cat inline', 'commonscat inline', 'Commonscat inline', 'Commons Category', 'commons Category','commonscatinline', 'Commonscatinline','Autres projets','Ccat','ccat','Cc','cc']

templates = ['Commons','Common','Wikicommons','Wikicommon']
include_cat = True

# category = 0
dolinkcheck = 0

template = pywikibot.Page(enwp, 'Template:Commonscat')
pages = template.embeddedin(namespaces='14')
# pages = template.embeddedin(namespaces='0')

for page in pages:
	if trip == 0:
		if "Varanasi" in page.title():
			trip = 1
		else:
			print(page.title())
			continue
	try:
		# item_dict = page.get()
		# qid = page.title()
		wd_item = pywikibot.ItemPage.fromPage(page)
		item_dict = wd_item.get()
		qid = wd_item.title()
	except:
		print('Huh - no page found')
		continue
	# print(item_dict)
	# exit()

	print("\n" + qid)
	print('https://'+langcode+'.wikipedia.org/wiki/'+page.title().replace(' ','_'))

	# Get the candidate page
	target_text = page.get()
	id_val = 0
	abort = 0
	null = 0
	for i in range(0,len(templates)):
		if id_val == 0:
			try:
				value = (target_text.split("{{"+templates[i]+"|"))[1].split("}}")[0].strip()
				values = (value.split("|"))
				if 'position' in values[0]:
					value = values[1]
				else:
					value = values[0]
				print('0')
				null = 0
				print(value)
				if value and id_val == 0:
					id_val = value
			except:
				null = 1
				try:
					value = (target_text.split("{{"+templates[i]+" |1="))[1].split("}}")[0].strip()
					print('1')
					null = 1
					print(value)
					if value and id_val == 0:
						id_val = value
					elif id_val != 0:
						print('Found multiple IDs')
				except:
					null = 2
					try:
						value = (target_text.split("{{"+templates[i])[1]).strip()
						# print(value)
						value = value.split("}}")[0].strip()
						print(value)
						values = (value.split("|"))
						print(values)
						if 'position' in values[1] or 'wiktionary' in values[1]:
							value = values[2]
						else:
							value = values[1]
						null = 2
						print('2')
						print(value)
						if value and id_val == 0:
							id_val = value
					except:
						null = 3
	print(null)
	# exit()
	if id_val == 0:
		try:
			p373 = item_dict['claims']['P373']
			print('P373 exists, following using.')
			for clm in p373:
				id_val = clm.getTarget()
		except:
			id_val = page.title().replace('Category:','')
	if id_val == 0:
		id_val = page.title().replace('Category:','')

	# Do some tidying of the link
	if id_val != 0:
		if "|" in id_val:
			if 'position' in id_val.split("|")[0] or 'bullet' in id_val.split("|")[0]:
				if 'position' in id_val.split("|")[1] or 'bullet' in id_val.split("|")[1]:
					id_val = id_val.split("|")[2]
				else:
					id_val = id_val.split("|")[1]
			else:
				id_val = id_val.split("|")[0]
		try:
			id_val = id_val.strip()
		except:
			null = 1

		if "{{PAGENAME" in id_val:
			id_val = page.title().replace('Category:','')

		try:
			id_val = id_val.strip()
		except:
			null = 1
		try:
			id_val = id_val.replace('Commons=', '').replace('Commons =','').replace('commons=', '').replace('commons =','').replace('Category:','').replace('category:','')
			if '|' in id_val:
				id_val = id_val.split('|')[0]
		except:
			null = 1
		try:
			id_val = id_val.strip()
		except:
			null = 1

		# Check for bad characters
		if "{" in id_val or "<" in id_val or "]" in id_val or "[" in id_val:
			continue
	else:
		id_val = page.title()

	id_val = id_val.replace('::',':')
	print(id_val)

	# If we have a P910 value, switch to using that item
	if include_cat:
		have_followed_p910 = False
		try:
			existing_id = item_dict['claims']['P910']
			print('P910 exists, following that.')
			for clm2 in existing_id:
				wd_item = clm2.getTarget()
				item_dict = wd_item.get()
				print(wd_item.title())
			have_followed_p910 = True
		except:
			null = 0

	# Double-check that we don't already have a sitelink
	try:
		sitelink = get_sitelink_title(item_dict['sitelinks']['commonswiki'])
		sitelink_check = 1
	except:
		sitelink_check = 0

	# Only attempt to do this if there is only one value for P373 and no existing sitelink
	if id_val != 0 and sitelink_check == 0:
		if include_cat:
			commonscat = u"Category:" + id_val
		else:
			commonscat = id_val
		commonscat = commonscat.replace('::',':')
		if commonscat[0] == ':':
			commonscat = commonscat[1:]

		# The commons category must already exist
		test = 'n'
		check = 0
		try:
			sitelink_page = pywikibot.Page(commons, commonscat)
			check = 1
		except:
			print('Found a bad sitelink')
			# print('https://commons.wikimedia.org/wiki/'+commonscat.replace(' ','_'))
			# test = input('Create it?')
			# if test == 'y':
			# 	check = create_commons_category(commonscat, commons)
			# clm.changeTarget("", summary=u"Remove non-functional value of P373")
		if check == 1:
			# Check the category to see if it already has a Wikidata item
			commonscat_sitelink_exists = 0
			try:
				commonscat_page = pywikibot.Page(commons, commonscat)
				commonscat_item = pywikibot.ItemPage.fromPage(commonscat_page)
				commonscat_item_dict = commonscat_item.get()
				commonscat_sitelink_exists = 1
			except:
				try:
					text = commonscat_page.get()
				except:
					print('Commons category does not exist - fix that?')
					last_check = check_if_category_has_contents(id_val,site=commons)
					if last_check and include_cat:
						print('https://commons.wikimedia.org/wiki/'+commonscat.replace(' ','_'))
						test = input('Create it?')
						check = 0
						if test == 'y':
							check = create_commons_category(commonscat, commons)
						if check != 0:
							time.sleep(3)
							commonscat_page = check
							text = ''
						if check == 0:
							continue
					else:
						continue

				if '{{Disambig' not in text and '{{disambig' not in text and '{{Category redirect' not in text and '{{category redirect' not in text:


					# That didn't work, add it to the Wikidata entry
					data = {'sitelinks': [{'site': 'commonswiki', 'title': commonscat}]}
					print('http://www.wikidata.org/wiki/'+qid)
					print('http://commons.wikimedia.org/wiki/'+commonscat.replace(' ','_'))
					text = input("Save? ")
					if text != 'n':
						try:
							wd_item.editEntity(data, summary=u'Add commons sitelink')
						except:
							time.sleep(1)
							wd_item.editEntity(data, summary=u'Add commons sitelink')
						nummodified += 1
						# commonscat_page.touch()

					print(nummodified)
					if nummodified >= maxnum:
						print('Reached the maximum of ' + str(maxnum) + ' entries modified, quitting!')
						exit()
			if dolinkcheck and commonscat_sitelink_exists and not have_followed_p910:
				# print('Hi')
				# print(commonscat_item_dict)
				if category == 0:
					skipthis = False
					islist = False
					try:
						p31val = commonscat_item_dict['claims']['P31']
						for p31clm in p31val:
							p31_item = p31clm.getTarget()
							# print(p31clm)
							if p31_item.title() == "Q13406463":
								islist = True
							elif p31_item.title() == "Q4167836":
								if category:
									skipthis = True
								else:
									print('OK')
							else:
								skipthis = True
					except:
						skipthis = False
					if skipthis:
						continue
					try:
						p31val = item_dict['claims']['P31']
					except:
						skipthis = False
					print(p31val)
					for p31clm in p31val:
						p31_item = p31clm.getTarget()
						if p31_item.title() == "Q13406463":
							islist = True
					print(islist)
					p1753 = False
					p301 = False
					p1754 = False
					p910 = False
					try:
						if islist:
							p1753 = commonscat_item_dict['claims']['P1753']
							print('hi')
						else:
							p301 = commonscat_item_dict['claims']['P301']
							print('hi2')
					except:
						try:
							if islist:
								p1754 = item_dict['claims']['P1754']
							else:
								p910 = item_dict['claims']['P910']
						except:
							null = 0
						if p1754 == False and p910 == False:
							try:
								if islist:
									p1753 = item_dict['claims']['P1753']
								else:
									p301 = item_dict['claims']['P301']
							except:
								print('Yes')
								print('Item:')
								print('http://www.wikidata.org/wiki/'+qid)
								try:
									print(item_dict['labels']['en'])
								except:
									print('')
								print('Category:')
								print('http://www.wikidata.org/wiki/'+commonscat_item.title())
								try:
									print(commonscat_item_dict['labels']['en'])
								except:
									print('')
								print('http://commons.wikimedia.org/wiki/'+commonscat.replace(' ','_'))
								if islist:
									newclaim = pywikibot.Claim(repo, 'P1753')
									newclaim.setTarget(wd_item)
									newclaim2 = pywikibot.Claim(repo, 'P1754')
									newclaim2.setTarget(commonscat_item)
									text = input("Link list? ")
									if text != 'n':
										wd_item.addClaim(newclaim2, summary=u'Linking to category item')
										commonscat_item.addClaim(newclaim, summary=u'Linking to list item')
										continue
								else:
									newclaim = pywikibot.Claim(repo, 'P301')
									newclaim.setTarget(wd_item)
									newclaim2 = pywikibot.Claim(repo, 'P910')
									newclaim2.setTarget(commonscat_item)
									text = input("Link? ")
									if text != 'n':
										wd_item.addClaim(newclaim2, summary=u'Linking to category item')
										commonscat_item.addClaim(newclaim, summary=u'Linking to topic item')
										continue
						print(p1753)
						print(p1754)
						print(p301)
						print(p910)
						# if p1753 == False and p1754 != False:
						# 	print('Have a mismatch in the list linking, fix?')
						# 	print('Item:')
						# 	print('http://www.wikidata.org/wiki/'+qid)
						# 	print('Category:')
						# 	print('http://www.wikidata.org/wiki/'+commonscat_item.title())
						# 	print('http://commons.wikimedia.org/wiki/'+commonscat.replace(' ','_'))
						# 	newclaim = pywikibot.Claim(repo, 'P1753')
						# 	newclaim.setTarget(wd_item)
						# 	text = input("Fix list link? ")
						# 	if text != 'n':
						# 		commonscat_item.addClaim(newclaim, summary=u'Linking to list item')
						# 		continue
						# elif p1753 != False and p1754 == False:
						# 	print('Have a mismatch in the list linking (2), fix?')
						# 	print('Item:')
						# 	print('http://www.wikidata.org/wiki/'+qid)
						# 	print('Category:')
						# 	print('http://www.wikidata.org/wiki/'+commonscat_item.title())
						# 	print('http://commons.wikimedia.org/wiki/'+commonscat.replace(' ','_'))
						# 	newclaim2 = pywikibot.Claim(repo, 'P1754')
						# 	newclaim2.setTarget(commonscat_item)
						# 	text = input("Fix list link 2? ")
						# 	if text != 'n':
						# 		wd_item.addClaim(newclaim2, summary=u'Linking to category item')
						# 		continue
						# elif p301 == False and p910 != False:
						# 	print('Have a mismatch in the category linking, fix?')
						# 	print('Item:')
						# 	print('http://www.wikidata.org/wiki/'+qid)
						# 	print('Category:')
						# 	print('http://www.wikidata.org/wiki/'+commonscat_item.title())
						# 	print('http://commons.wikimedia.org/wiki/'+commonscat.replace(' ','_'))
						# 	newclaim = pywikibot.Claim(repo, 'P301')
						# 	newclaim.setTarget(wd_item)
						# 	text = input("Fix cat link? ")
						# 	if text != 'n':
						# 		commonscat_item.addClaim(newclaim, summary=u'Linking to topic item')
						# 		continue
						# elif p301 != False and p910 == False:
						# 	print('Have a mismatch in the category linking (2), fix?')
						# 	print('Item:')
						# 	print('http://www.wikidata.org/wiki/'+qid)
						# 	print('Category:')
						# 	print('http://www.wikidata.org/wiki/'+commonscat_item.title())
						# 	print('http://commons.wikimedia.org/wiki/'+commonscat.replace(' ','_'))
						# 	newclaim2 = pywikibot.Claim(repo, 'P910')
						# 	newclaim2.setTarget(commonscat_item)
						# 	text = input("Fix cat link 2? ")
						# 	if text != 'n':
						# 		wd_item.addClaim(newclaim2, summary=u'Linking to category item')
						# 		continue

				else:
					skipthis = False
					islist = False
					p1753 = False
					p301 = False
					p1754 = False
					p910 = False
					try:
						p31val = commonscat_item_dict['claims']['P31']
						for p31clm in p31val:
							p31_item = p31clm.getTarget()
							# print(p31clm)
							if p31_item.title() == "Q13406463":
								islist = True
							elif p31_item.title() == "Q4167836":
								if category:
									skipthis = True
								else:
									print('OK')
							else:
								skipthis = True
					except:
						null = 1
					if skipthis:
						continue
					try:
						if islist:
							p1753 = item_dict['claims']['P1753']
						else:
							p301 = item_dict['claims']['P301']
					except:
						try:
							if islist:
								p1754 = commonscat_item_dict['claims']['P1754']
							else:
								p910 = commonscat_item_dict['claims']['P910']
						except:
							null = 0
						if p1754 == False and p910 == False:
							try:
								if islist:
									p1753 = commonscat_item_dict['claims']['P1753']
								else:
									p301 = commonscat_item_dict['claims']['P301']
							except:
								print('Yes2')
								print('Item:')
								print('http://www.wikidata.org/wiki/'+commonscat_item.title())
								try:
									print(commonscat_item_dict['labels']['en'])
								except:
									print('')
								print('Category:')
								print('http://www.wikidata.org/wiki/'+qid)
								try:
									print(item_dict['labels']['en'])
								except:
									print('')
								print('http://commons.wikimedia.org/wiki/'+commonscat.replace(' ','_'))

								if islist:
									newclaim = pywikibot.Claim(repo, 'P1753')
									newclaim.setTarget(commonscat_item)
									newclaim2 = pywikibot.Claim(repo, 'P1754')
									newclaim2.setTarget(wd_item)
									text = input("Link list? ")
									if text != 'n':
										wd_item.addClaim(newclaim, summary=u'Linking to list item')
										commonscat_item.addClaim(newclaim2, summary=u'Linking to category item')
										continue
								else:
									newclaim = pywikibot.Claim(repo, 'P301')
									newclaim.setTarget(commonscat_item)
									newclaim2 = pywikibot.Claim(repo, 'P910')
									newclaim2.setTarget(wd_item)
									text = input("Link? ")
									if text != 'n':
										wd_item.addClaim(newclaim, summary=u'Linking to topic item')
										commonscat_item.addClaim(newclaim2, summary=u'Linking to category item')
										continue
						print(p1753)
						print(p1754)
						print(p301)
						print(p910)
						if p1753 == False and p1754 != False:
							print('Have a mismatch in the list linking, fix?')
							print('Item:')
							print('http://www.wikidata.org/wiki/'+qid)
							print('Category:')
							print('http://www.wikidata.org/wiki/'+commonscat_item.title())
							print('http://commons.wikimedia.org/wiki/'+commonscat.replace(' ','_'))
							newclaim = pywikibot.Claim(repo, 'P1753')
							newclaim.setTarget(wd_item)
							text = input("Fix list link? ")
							if text != 'n':
								wd_item.addClaim(newclaim2, summary=u'Linking to category item')
								continue
						elif p1753 != False and p1754 == False:
							print('Have a mismatch in the list linking (2), fix?')
							print('Item:')
							print('http://www.wikidata.org/wiki/'+qid)
							print('Category:')
							print('http://www.wikidata.org/wiki/'+commonscat_item.title())
							print('http://commons.wikimedia.org/wiki/'+commonscat.replace(' ','_'))
							newclaim2 = pywikibot.Claim(repo, 'P1754')
							newclaim2.setTarget(commonscat_item)
							text = input("Fix list link 2? ")
							if text != 'n':
								commonscat_item.addClaim(newclaim, summary=u'Linking to list item')
								continue
						elif p301 == False and p910 != False:
							print('Have a mismatch in the category linking, fix?')
							print('Item:')
							print('http://www.wikidata.org/wiki/'+qid)
							print('Category:')
							print('http://www.wikidata.org/wiki/'+commonscat_item.title())
							print('http://commons.wikimedia.org/wiki/'+commonscat.replace(' ','_'))
							newclaim = pywikibot.Claim(repo, 'P301')
							newclaim.setTarget(wd_item)
							text = input("Fix cat link? ")
							if text != 'n':
								wd_item.addClaim(newclaim2, summary=u'Linking to category item')
								continue
						elif p301 != False and p910 == False:
							print('Have a mismatch in the category linking (2), fix?')
							print('Item:')
							print('http://www.wikidata.org/wiki/'+qid)
							print('Category:')
							print('http://www.wikidata.org/wiki/'+commonscat_item.title())
							print('http://commons.wikimedia.org/wiki/'+commonscat.replace(' ','_'))
							newclaim2 = pywikibot.Claim(repo, 'P910')
							newclaim2.setTarget(commonscat_item)
							text = input("Fix cat link 2? ")
							if text != 'n':
								commonscat_item.addClaim(newclaim, summary=u'Linking to topic item')
								continue

					print('check?')



# elif id_val != 0 and sitelink_check == 1 and category == 0:
# 	print('Hello')
# 	try:
# 		sitelink_item = pywikibot.ItemPage.fromPage(sitelink)
# 		sitelink_item_dict = sitelink_item.get()
# 		print(sitelink_item_dict)
# 	except:
# 		print("That didn't work")
# exit()



print('Done! Edited ' + str(nummodified) + ' entries')

# EOF
