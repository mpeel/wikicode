#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Remove uses of {{PhotoOfTheDay}} from Commons, to replace them with the Infobox
# Mike Peel     28-Dec-2021      v1 - start

# Import modules
import pywikibot
from pywikibot import pagegenerators
import re

# Connect to Commons and Wikidata
commons = pywikibot.Site('commons', 'commons')
wikidata = commons.data_repository()

# Function to migrate the templates
def migrate_photooftheday(target):
	print('\n\n https://commons.wikimedia.org/wiki/'+target.title())
	# Only want to try this if we're already matched up with Wikidata
	try:
		wd_item = pywikibot.ItemPage.fromPage(target)
		item_dict = wd_item.get()
		qid = wd_item.title()
	except:
		print('No Wikidata item')
		return 0

	# If we have a P301 value, switch to using that Wikidata item
	try:
		existing_id = item_dict['claims']['P301']
		print('P301 exists, following that.')
		for clm2 in existing_id:
			wd_item = clm2.getTarget()
			item_dict = wd_item.get()
			qid = wd_item.title()
			print(wd_item.title())
	except:
		# No downside if we didn't find the value
		pass
	print('https://www.wikidata.org/wiki/'+qid)

	# Check that we're looking at a calendar day item
	calday = False
	P31 = ''
	try:
		P31 = item_dict['claims']['P31']
	except:
		print('No P31, skipping')
		return 0
	if P31 != '':
		for clm in P31:
			if clm.getTarget().title() == 'Q47150325':
				calday = True
	if not calday:
		print('Wikidata item is not a calendar day, skipping')
		return 0

	# See if we already have a photo
	hasphoto = False
	P18 = ''
	try:
		P18 = item_dict['claims']['P18']
		hasphoto = True
	except:
		pass
	# To implement - is it the same photo we want to add?
	# if P31 != '':
	# 	for clm in P31:
	# 		if clm.getTarget().title() == 'Q47150325':
	# 			calday = True
	if hasphoto:
		print('Wikidata item already has a photo')
		# return 0

	# Find the template, and do the migration
	filename = ''
	caption = ''
	template_params = target.templatesWithParams()
	for template_info in template_params:
		if template_info[0].title() == 'Template:PhotoOfTheDay':
			# print(template_info)
			toreplace = []
			for info in template_info[1]:
				# print(info)
				if 'file name=' in info:
					filename = info.replace('file name=','')
				if 'file description=' in info or 'text=' in info:
					try:
						info = info.split('<br />')
						info = info[0]
					except:
						pass
					newtext = info.replace('file description=','').replace('text=','')
					testing = False
					count = 0
					while testing == False:
						count += 1
						if count > 10:
							# This hasn't worked
							return 0
						print(newtext)
						startindex = newtext.find('{{w|')
						print(startindex)
						if startindex == -1:
							testing = True
						else:
							endindex = newtext[startindex:].find('}}')
							print(endindex)
							if endindex == -1:
								testing = False
							else:
								toreplace.append([newtext[startindex:startindex+endindex+2],newtext[startindex+4:startindex+endindex]])
								newtext = newtext.replace(newtext[startindex:startindex+endindex+2], newtext[startindex+4:startindex+endindex])
					# if newtext[0] == '[':
						# Avoid cases that are just wikilinks
						# continue
					# Try to strip out wikilinks
					# newtext = re.sub('\[\[([:^\]\|]*)\]\]', '\\1', newtext)
					# newtext = re.sub('\[\[([^\]\|]*)\]\]', '\\1', newtext)
					if caption == '':
						caption += newtext
					else:
						caption = newtext + ' ' + caption

			print('File name: ' + filename)
			caption = caption.strip()
			print('Caption: ' + caption)
			if filename != '':
				test = input('Save?')
			else:
				test = 'n'
			if test == 'y':
				try:
					targetimage = pywikibot.FilePage(commons, 'File:'+filename)
					# print(targetimage)
					if targetimage.text == '':
						print('Target image not found, skipping')
						return 0
					newclaim = pywikibot.Claim(wikidata, 'P18')
					newclaim.setTarget(targetimage)
					wd_item.addClaim(newclaim, summary='Importing image from Commons {{PhotoOfTheDay}} template as part of migration to Wikidata')
					caption = caption.strip()
					if caption != '':
						qualifier = pywikibot.Claim(wikidata, 'P2096')
						newqual = pywikibot.WbMonolingualText(caption, 'en')
						qualifier.setTarget(newqual)
						newclaim.addQualifier(qualifier, summary='Also importing a media legend from Commons')
				except:
					return 0
			newtext = target.text
			for case in toreplace:
				newtext = newtext.replace(case[0], case[1])
			# Prepare the replacement text for the category
			startindex = newtext.find('{{PhotoOfTheDay')
			endindex = newtext[startindex:].find('}}')
			if '{{Wikidata Infobox}}' not in target.text:
				newtext = newtext[0:startindex] + '{{Wikidata Infobox}}' + newtext[endindex+2:]
			else:
				newtext = newtext[0:startindex] + newtext[endindex+2:]
			# Do some extra tidying up
			newtext = newtext.replace('{{Interwiki from wikidata}}','')
			newtext = newtext.replace('\n\n\n','\n')
			newtext = newtext.replace('\n\n\n','\n')
			newtext = newtext.replace('\n\n{{Wikidata Infobox','\n{{Wikidata Infobox')

			print(newtext)
			if filename != '':
				test = input('Save?')
			else:
				test = 'y'
			if test == 'y':
				target.text = newtext
				target.save('Migrating from {{PhotoOfTheDay}} to {{Wikidata Infobox}}, matching ID is ' + str(qid))
			elif test == 'b':
				target.text = newtext
				target.save("Migrating from {{PhotoOfTheDay}} to {{Wikidata Infobox}} - not migrating bad image for the day. Matching ID is " + str(qid))
			# join(lines)
			return 1

	# If we're here, then things didn't work.
	return 0

template = pywikibot.Page(commons, 'Template:PhotoOfTheDay')
targets = template.embeddedin()
for target in targets:
	test = migrate_photooftheday(target)
	# if test == 1:
	# 	exit()
