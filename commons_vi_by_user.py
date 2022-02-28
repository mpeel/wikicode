#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Featured Image categories by user
# Mike Peel     15-Jan-2022      v1 - start
# Import modules
import pywikibot
from pywikibot import pagegenerators

commons = pywikibot.Site('commons', 'commons')

targetcat = 'Category:Valued images by user'
destinationpage = 'Commons:Valued images by user'
skip = ['by country', 'by subject', 'images from', 'Wiki Loves']


page = pywikibot.Page(commons, destinationpage)
pagetext = '{{en|This is a list of [[Commons:Valued images|valued images]] by user. If you want to be included in this list, create a subcategory of [[:Category:Valued images by user]] with the format \'Valued images by <username>\', and you will be included in this list with the next bot update (daily). This page is automatically updated by [[User:Pi bot]]. If you want to change the format of this page, or want to be excluded from this list, please contact [[User:Mike Peel]]. Manual changes will be ignored by the bot update.}}\n== {{LangSwitch|cs=Tabulka|de=Tabelle|en=Table|zh=表格}} ==\n\n{|class="wikitable sortable" cellspacing="0"\n!{{LangSwitch|de=Benutzer|en=User|es=Usuario|zh=用戶}}\n!{{LangSwitch|de=Kategorie|es=Categoría|en=Category|zh=分類}}\n!{{LangSwitch|de=Anzahl VIs|en=Number VIs {{VI seal|size=15}}|zh=優質圖像數量}}\n'
cat = pywikibot.Category(commons, targetcat)
subcats = pagegenerators.SubCategoriesPageGenerator(cat, recurse=False);
for subcat in subcats:
	skipthis = False
	for toskip in skip:
		if toskip in subcat.title():
			skipthis = True
	if skipthis:
		continue
	print(subcat.title())
	title = subcat.title()
	title = title.replace('By','by')
	title = title.replace('user','User')
	print(title)
	if "'s" in title:
		username = title.split("'s")[0]
	elif " - " in title:
		username = title.split("-")[0]
	elif "/" in title:
		username = title.split("/")[0]
	elif "of " in title:
		username = title.split("of ")[1]
	elif "from " in title:
		username = title.split("from ")[1]
	else:
		username = title.split('by ')[1]
	username = username.replace('User:','')
	username = username.replace('Photographs by','')
	username = username.replace('Files by','')
	username = username.replace('Category:','')
	username = username.replace('Yann Forget','Yann')
	if '(' in username:
		username = username.split('(')[0]
	username = username.strip()
	if '/' in username:
		username = username.split('/')[0]

	count = 0
	filenames = []
	files = pagegenerators.CategorizedPageGenerator(subcat, recurse=False);
	for file in files:
		if file.title() not in filenames:
			filenames.append(file.title())
			count += 1
	for result in pagegenerators.SubCategoriesPageGenerator(subcat, recurse=False):
		files = pagegenerators.CategorizedPageGenerator(result, recurse=False);
		for file in files:
			if file.title() not in filenames:
				filenames.append(file.title())
				count += 1

	pagetext = pagetext + '|-\n'+'|[[User:'+username+'|'+username+']] || [[:'+subcat.title() + '|' + subcat.title().replace('Category:','') + ']] || align="right" | ' + str(count) + '\n'

pagetext = pagetext + '\n|}[[Category:Valued images by user| ]]'
page.text = pagetext
page.save('Updating')
