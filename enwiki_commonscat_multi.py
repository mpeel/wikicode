
from __future__ import unicode_literals

import pywikibot
import numpy as np
import time
import string
from pywikibot import pagegenerators
import urllib
from pibot_functions import *

maxnum = 100000
nummodified = 0

wikidata_site = pywikibot.Site("wikidata", "wikidata")
repo = wikidata_site.data_repository()  # this is a DataSite object
commons = pywikibot.Site('commons', 'commons')
enwp = pywikibot.Site('en', 'wikipedia')
debug = 1
trip = 1
templates = ['Commons category multi', 'Commonscat-N','Commoncats','Commonscat show2','Commonscats','Common cats','Commons cats','Commons cat show2','Commonscat multi','Commons cat multi','Ccatm','Commons category multiple','Commonscat-multi','Commons category-multi','Commons multiple','Commons multi','Commonscatmulti','commonscat-multi', 'commons category multi', 'commons category-multi']

catredirect_templates = ["category redirect", "Category redirect", "seecat", "Seecat", "see cat", "See cat", "categoryredirect", "Categoryredirect", "catredirect", "Catredirect", "cat redirect", "Cat redirect", "catredir", "Catredir", "redirect category", "Redirect category", "cat-red", "Cat-red", "redirect cat", "Redirect cat", "category Redirect", "Category Redirect", "cat-redirect", "Cat-redirect"]

template = pywikibot.Page(enwp, 'Template:'+templates[0])
# targetcats = template.embeddedin(namespaces='14')
targetcats = template.embeddedin(namespaces='0')


for page in targetcats:
	# Optional skip-ahead to resume broken runs
	if trip == 0:
		if "Zizia" in page.title():
			trip = 1
		else:
			print(page.title())
			continue

	print("\nhttps://en.wikipedia.org/wiki/" + page.title().replace(" ",'_'))

	# Get the candidate commonscat links
	try:
		target_text = page.get()
	except:
		continue
	id_val = 0
	abort = 0
	commonscat_string = ""
	for i in range(0,len(templates)):
		try:
			# print(templates[i])
			value = (target_text.split("{{"+templates[i]))[1].split("}}")[0]
			if value and id_val == 0:
				id_val = value
				id_template = templates[i]
				id_string = "{{"+templates[i]+id_val+"}}"
		except:
			null = 1
		try:
			template = templates[i][0].lower() + templates[i][1:]
			# print(template)
			value = (target_text.split("{{"+template))[1].split("}}")[0]
			if value and id_val == 0:
				id_val = value
				id_template = template
				id_string = "{{"+template+id_val+"}}"
		except:
			null = 1

	if id_val == 0:
		# We didn't find the commons category link, skip this one.
		input('Check?')
		continue
	
	print(id_val)
	id_vals = id_val.split('|')
	print(id_vals)

	# Do some tidying of the link
	bad_id = np.zeros(len(id_vals))
	for i in range(0,len(id_vals)):
		if 'position' in id_vals[i] or 'bullet' in id_vals[i] or 'nowrap' in id_vals[i] or 'lcfirst' in id_vals[i] or 'lcf' in id_vals[i] or 'align' in id_vals[i] or 'width' in id_vals[i] or 'delimiter' in id_vals[i] or id_vals[i] == '' or id_vals[i] == ' ':
			bad_id[i] = 1
	id_vals = np.asarray(id_vals,dtype="str")
	# print(id_vals)
	# print(bad_id)
	id_vals = id_vals[bad_id == 0]
	num_vals = len(id_vals)
	# print(id_vals)
	# exit()

	# Get the Wikidata item
	try:
		wd_item = pywikibot.ItemPage.fromPage(page)
		item_dict = wd_item.get()
		qid = wd_item.title()
		print(qid)
	except:
		# If that didn't work, go no further
		print(page.title() + ' - no page found')
		wd_item = 0
		item_dict = 0
		qid = 0
		sitelink_check = 0
		# continue

	# If we have a P910 value, switch to using that Wikidata item
	if qid != 0:
		try:
			existing_id = item_dict['claims']['P910']
			print('P910 exists, following that.')
			for clm2 in existing_id:
				wd_item = clm2.getTarget()
				item_dict = wd_item.get()
				qid = wd_item.title()
				print(wd_item.title())
		except:
			null = 0

		# Double-check that there is a sitelink on Wikidata
		try:
			sitelink = item_dict['sitelinks']['commonswiki']
			sitelink_check = 1
		except:
			sitelink = ''
			sitelink_check = 0
		print("sitelink: " + str(sitelink))

	# Let's check that the links exist
	for val in id_vals:
		val_orig = val.copy()
		val = val.strip()
		if val == '':
			continue
		commonscat = 'Category:'+str(val)
		commonscat = commonscat.replace('Category:Category:','')
		print(commonscat)
		last_check = True
		try:
			commonscat_page = pywikibot.Page(commons, commonscat)
			text = commonscat_page.get()
			for i in range(0,len(catredirect_templates)):
				if catredirect_templates[i] in text:
					last_check = False
		except:
			last_check = check_if_category_has_contents(commonscat,site=commons)
		print(last_check)
		if last_check == False:
			target_text = target_text.replace(id_val,id_val.replace('|'+val_orig,''))
			print(num_vals)
			if num_vals == 2:
				target_text = target_text.replace(id_template, 'Commons category')
			if target_text != page.text:
				test = input('Found a bad sitelink - remove it?')
				if test == 'y':
					page.text = target_text
					page.save('Removing broken Commons category link',minor=False)
					nummodified += 1
					continue

	# If one of the categories is the sitelink, switch to that?
	# if sitelink != '' and sitelink.replace('Category:','') in id_vals:
	# 	print(id_string)
	# 	target_text = target_text.replace(id_string,'{{Commons category}}')
	# 	if target_text != page.text:
	# 		test = input('Replace with sitelink?')
	# 		if test == 'y':
	# 			page.text = target_text
	# 			page.save('Changing to use Commons category and the Commons sitelink through Wikidata',minor=False)
	# 			nummodified += 1

print('Done! Edited ' + str(nummodified) + ' entries')

# EOF