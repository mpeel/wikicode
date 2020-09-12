# !/usr/bin/python
# -*- coding: utf-8  -*-
# Functions for enwp short descriptions
# Mike Peel     05-Sep-2020     v1 - start function file
# Mike Peel     12-Sep-2020     v2 - expanding

import pywikibot
from pywikibot import pagegenerators
from pywikibot.data import api
import dateparser
import re
import time

# This is the main funciton to generate and save new short descriptions.
def shortdesc_stage(targetcat, maxnum, maxnum_new, debug, trip, startpoint, endpoint, require_infobox, infobox_strings, description, add_birth_date, add_death_date,onwiki_page,local_file):
	# Initialising parameters
	count = 0
	count_new = 0
	if startpoint == '':
		trip = False
	output = ''

	# Linking with enwp and finding related pages
	wikipedia = pywikibot.Site('en', 'wikipedia')
	cat = pywikibot.Category(wikipedia, targetcat)

	## Loop over all related pages
	for page in pagegenerators.CategorizedPageGenerator(cat, recurse=False):
		# Reset/increment parameters for each loop
		enwiki_description = ''
		count += 1
		has_infobox = False

		# This checks for trip/startpoint/endpoint
		if not trip:
			if startpoint in page.title():
				trip = True
			else:
				continue
		if endpoint != '' and endpoint in page.title():
			break

		# Check if there is already a short description on enwp
		test = get_pageinfo(wikipedia,page)
		for item in test['query']['pages']:
			try:
				enwiki_description = test['query']['pages'][item]['pageprops']['wikibase-shortdesc']
			except:
				null = 0
		if len(enwiki_description) > 0:
			# The article already has a short description, move on to the next.
			# print('* [['+page.title()+']] - EXISTS: ' + enwiki_description)
			print(page.title() + ' - already has short description')
			continue

		if require_infobox:
			for option in infobox_strings:
				if option in page.text:
					has_infobox = True
			if not has_infobox:
				# The article does not have an infobox and we are only looking for articles that do have one.
				print(page.title() + ' - does not have infobox')
				continue

		enwiki_description = description
		birthdate = calculateBirthDateFull(page=page)
		deathdate = calculateDeathDateFull(page=page)

		if birthdate and deathdate and add_birth_date and add_death_date:
			enwiki_description += ' (' + str(birthdate[0:4]) + "–" + str(deathdate[0:4]) + ')'
		elif birthdate and add_birth_date:
			enwiki_description += ' (b. ' + str(birthdate[0:4]) + ')'
		elif deathdate and add_death_date:
			enwiki_description += ' (d. ' + str(birthdate[0:4]) + ')'

		# We have a new description, save it into the on-wikip page or a text file
		count_new += 1
		if onwiki_page != '':
			output += '|-\n'
			output += '| [['+page.title()+"]] || " + enwiki_description+"\n"
		else:
			output += page.title() + ' || ' + enwiki_description+"\n"
		print(page.title() + ' - NEW SHORT DESCRIPTION')

		if count >= maxnum or count_new >= maxnum_new:
			break

	# We've finished generating the new short descriptions, now save them on-wiki or to a file.
	if onwiki_page != '':
		page = pywikibot.Page(wikipedia, onwiki_page)
		page.text = '{| class="wikitable"' + output + "\n|}"
		page.save("New set of short descriptions")
		print('Your new set of short descriptions should be at https://en.wikipedia.org/wiki/' + onwiki_page.replace(' ','_'))
	else:
		file = open(local_file,'w')
		file.write(output)
		file.close()
		print('Your new set of short descriptions should be in ' + local_file)

	# All done!
	return

# This is the code that adds those short descriptions to enwp
def shortdesc_add(debug,onwiki_page,local_file,wait_time, also_wikidata):
	# Setup
	count = 0
	count2 = 0
	wikipedia = pywikibot.Site('en', 'wikipedia')

	# Get the list of articles and new short descriptions
	if onwiki_page != '':
		page = pywikibot.Page(wikipedia, onwiki_page)
		todo = page.text
	else:
		file = open(local_file,'r')
		file_contents = file.read()
		todo = file_contents.splitlines()

		file.close()

	# Work through them one by one
	for line in todo:
		print(line)
		# Only if we don't have a table header
		if '{|' not in line and '|}' not in line and line.strip() != '':
			values = line.split('||')
			page = pywikibot.Page(wikipedia, values[0].strip())
			test = 'y'
			if debug == True:
				test = 'n'
				test = input('Add ' + values[1].strip() + ' to https://en.wikipedia.org/wiki/' + values[0].strip().replace(' ','_') + "? ('y' to apply)")
			if test == 'y':
				count += 1
				page.text = '{{Short description|'+values[1].strip()+'}}\n'+page.text
				page.save('Adding short description ("'+values[1].strip()+'")')

			if also_wikidata:
				# We also want to add the description to Wikidata, if there isn't one there already, and we have a linked Wikidata item
				try:
					wd_item = pywikibot.ItemPage.fromPage(page)
					item_dict = wd_item.get()
					qid = wd_item.title()
				except:
					print('Huh - no page found')
					continue

				# Get the description from Wikidata to make sure it's empty
				wikidata_description = ''
				try:
					wikidata_description = item_dict['descriptions']['en']
				except:
					null = 0

				# Save the new description to Wikidata
				if wikidata_description == '':
					if debug:
						test = input('No description, import it?')
					else:
						test = 'y'
					mydescriptions = {u'en': values[1].strip()}
					if test == 'y':
						wd_item.editDescriptions(mydescriptions, summary=u'Adding en description ("'+values[1].strip()+'")')
			time.sleep(wait_time)

	# All done!
	print("Added descriptions to " + str(count) + " enwp articles and " + str(count2) + ' Wikidata items!')
	return


# This function fetches the page info from a specific item
def get_pageinfo(site, itemtitle):
	 params = { 'action' :'query', 
				'format' : 'json',
				'prop' : 'pageprops',
				'titles': itemtitle}
	 request = api.Request(site=site, parameters=params)
	 return request.submit()

# This calculates the birth date based on common syntaxes present in biographies
def calculateBirthDateFull(page=''):
	if not page:
		return ''
	m = re.findall(r'\{\{(?:B|b)irth (?:D|d)ate and age\s*\|(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)', page.text.replace('|df=yes','').replace('|df=y','').replace('|mf=yes','').replace('|mf=y',''))
	if m:
		return str(m[0][0]) + '-' + str(m[0][1]) + '-' + str(m[0][2])
	m = re.findall(r'\{\{(?:B|b)irth date\|(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)', page.text.replace('|df=yes','').replace('|df=y','').replace(',','').replace('[','').replace(']',''))
	if m:
		try:
			temp = dateparser.parse(str(m[0][0])+' '+str(m[0][1])+' '+str(m[0][2]))
			return str(temp.year) + '-' + str(temp.month) + '-' + str(temp.day)
		except:
			m = False
	if m:
		return str(m[0][0]) + '-' + str(m[0][1]) + '-' + str(m[0][2])
	m = re.findall(r'\|\s*(?:B|b)irth(?:_| )date\s*=\s*(\w+)\s*(\w+)\s*(\w+)', page.text.replace('|df=yes','').replace('|df=y','').replace(',','').replace('[','').replace(']',''))
	if m:
		if (len(m[0][0]) + len(m[0][1]) + len(m[0][2]) > 5) and m[0][2].isnumeric():
			try:
				temp = dateparser.parse(str(m[0][0])+' '+str(m[0][1])+' '+str(m[0][2]))
				return str(temp.year) + '-' + str(temp.month) + '-' + str(temp.day)
			except:
				m = False
	m = re.findall(r'(?im)\[\[\s*Category\s*:\s*(\d+) births\s*[\|\]]', page.text)
	if m:
		return m[0]
	return ''

# This calculates the death date based on common syntaxes present in biographies
def calculateDeathDateFull(page=''):
	if not page:
		return ''
	m = re.findall(r'\{\{(?:D|d)da\|(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)', page.text.replace('|df=yes','').replace('|df=y','').replace('|mf=yes','').replace('|mf=y',''))
	if m:
		return str(m[0][0]) + '-' + str(m[0][1]) + '-' + str(m[0][2])
	m = re.findall(r'\{\{(?:D|d)eath date and age\|(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)', page.text.replace('|df=yes','').replace('|df=y','').replace('|mf=yes','').replace('|mf=y',''))
	if m:
		return str(m[0][0]) + '-' + str(m[0][1]) + '-' + str(m[0][2])
	m = re.findall(r'\{\{(?:D|d)eath year and age\|(\d+)', page.text.replace('|df=yes','').replace('|df=y','').replace(',','').replace('[','').replace(']',''))
	if m:
		return str(m[0])
	m = re.findall(r'\{\{(?:D|d)eath date\|(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)', page.text.replace('|df=yes','').replace('|df=y','').replace(',','').replace('[','').replace(']',''))
	if m:
		if (len(m[0][0]) + len(m[0][1]) + len(m[0][2]) > 5) and m[0][2].isnumeric():
			try:
				temp = dateparser.parse(str(m[0][0])+' '+str(m[0][1])+' '+str(m[0][2]))
				return str(temp.year) + '-' + str(temp.month) + '-' + str(temp.day)
			except:
				m = False
	m = re.findall(r'\|\s*(?:D|d)eath(?:_| )date\s*=\s*(\w+)\s*(\w+)\s*(\w+)', page.text.replace('|df=yes','').replace('|df=y','').replace(',','').replace('[','').replace(']',''))
	if m:
		if (len(m[0][0]) + len(m[0][1]) + len(m[0][2]) > 5) and m[0][2].isnumeric():
			try:
				temp = dateparser.parse(str(m[0][0])+' '+str(m[0][1])+' '+str(m[0][2]))
				return str(temp.year) + '-' + str(temp.month) + '-' + str(temp.day)
			except:
				m = False
	m = re.findall(r'(?im)\[\[\s*Category\s*:\s*(\d+) deaths\s*[\|\]]', page.text)
	if m:
		return m[0]
	return ''

# EOF