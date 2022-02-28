#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Quality Image categories by user
# Mike Peel     15-Jan-2022      v1 - start
# Import modules
import pywikibot
from pywikibot import pagegenerators

commons = pywikibot.Site('commons', 'commons')

targetcat = 'Category:Quality images by user'
destinationpage = 'Commons:Quality images by user'
skip = ['by country', 'by subject', 'images from', 'Wiki Loves']


page = pywikibot.Page(commons, destinationpage)
pagetext = '{{Box-2\n | {{LangSwitch\n    | default = [[File:Quality images logo.svg|left|64px]] This is a list of [[Commons:Quality images|quality images]] by user. If you want to be included in this list, create a subcategory of [[:Category:Quality images by user|Quality images by user]] with the format \'Quality images by <username>\', and you will be included in this list with the next bot update (daily). This page will be automatically updated by [[User:Pi bot|Pi bot]]. If you want to change the format of this page, or want to be excluded from this list, please contact [[User:Mike Peel|Mike Peel]]. Manual changes will be ignored by the bot update.\n    | de = [[File:Quality images logo.svg|64px|left]] Dies ist eine Liste von [[Commons:Quality images/de|Qualitätsbildern]] nach Benutzer. Wenn du in diese Liste aufgenommen werden möchtest, erstelle eine Unterkategorie von [[:Category:Quality images by user|Quality images by user]] mit dem Format „Quality images by <Benutzername>“, und du wirst mit dem nächsten Bot-Update (täglich) in diese Liste aufgenommen. Diese Seite wird automatisch vom [[User:Pi bot|Pi bot]] aktualisiert. Wenn du das Format dieser Seite ändern oder von dieser Liste ausgeschlossen werden möchtest, wende dich bitte an [[User:Mike Peel|Mike Peel]]. Manuelle Änderungen werden vom Bot-Update ignoriert.\n   }}\n}}\n\n== {{LangSwitch\n    | default = Table\n    | cs      = Tabulka\n    | de      = Tabelle\n    | es      = Tabla\n    | zh      = 表格\n   }} ==\n\n{|class="wikitable sortable" cellspacing="0"\n!{{LangSwitch|de=Benutzer|default=User|es=Usuario|zh=用戶}}\n!{{LangSwitch|de=Kategorie|default=Category|es=Categoría|zh=分類}}\n!{{LangSwitch|de=Anzahl QIs|default=Number QIs|zh=優質圖像數量}}\n'
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
	elif "from " in title:
		username = title.split("from ")[1]
	elif "of " in title:
		username = title.split("of ")[1]
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
	pagetext = pagetext + '|-\n'+'|[[User:'+username+'|'+username+']] || [[:'+subcat.title() + '|'

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

	pagetext = pagetext + subcat.title().replace('Category:','') + ']] || align="right" | ' + str(count) + '\n'

pagetext = pagetext + '\n|}[[Category:Quality images by user| ]]'
page.text = pagetext
page.save('Updating')
