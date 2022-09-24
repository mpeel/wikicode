#!/usr/bin/python
# -*- coding: utf-8  -*-
# Archive closed bot requests
# Mike Peel     11-Oct-2021      v1 - start

import pywikibot
import numpy as np
import time
import string
from pywikibot import pagegenerators
from pywikibot.data import api
import urllib
import random
from datetime import datetime

# Sites
wikidata_site = pywikibot.Site("wikidata", "wikidata")
repo = wikidata_site.data_repository()  # this is a DataSite object

# Get the current archive page
archivepagename = 'Wikidata:Requests for permissions/RfBot/'+datetime.now().strftime('%B')+' '+datetime.now().strftime('%Y')
archivepage = pywikibot.Page(wikidata_site, archivepagename)
newarchivepage = archivepage.text

# Get the list of open bot requests
listpage = pywikibot.Page(wikidata_site, 'Wikidata:Requests for permissions/Bot')
newbotpage = listpage.text
lines = listpage.text.splitlines()

# Now let's run through the list and see what has been approved or withdrawn
for line in lines:
	if ('Wikidata:Requests for permissions/Bot' in line or 'Wikidata:Requests_for_permissions/Bot' in line) and 'Header' not in line:
		botpagetitle = line.strip().replace('{{','').replace('}}','')
		print(botpagetitle)
		botpage = pywikibot.Page(wikidata_site, botpagetitle)
		if '{{approved}}' in botpage.text.lower():
			try:
				newarchivepage = newarchivepage.replace('= Successful requests =','= Successful requests =\n* ' + line.replace('{','[').replace('}',']'))
				newbotpage = newbotpage.replace(line+'\n', '')
			except:
				print("That didn't work")
				exit()
			null = 0
		if '{{withdrawn}}' in botpage.text.lower() or '{{not done|withdrawn}}' in botpage.text.lower() or '{{not done|disapproved}}' in botpage.text.lower():
			try:
				newarchivepage = newarchivepage.replace('= Unsuccessful requests =','= Unsuccessful requests =\n* ' + line.replace('{','[').replace('}',']'))
				newbotpage = newbotpage.replace(line+'\n', '')
			except:
				print("That didn't work")
				exit()
			null = 0
		if '{{not done}}' in botpage.text.lower():
			try:
				newarchivepage = newarchivepage.replace('= Unsuccessful requests =','= Unsuccessful requests =\n* ' + line.replace('{','[').replace('}',']'))
				newbotpage = newbotpage.replace(line+'\n', '')
			except:
				print("That didn't work")
				exit()
			null = 0

# Do some last tidying up
newbotpage = newbotpage.replace('Requests_for_permissions','Requests for permissions')
newbotpage = newbotpage.replace('\n\n\n','\n')

# And save things
archivepage.text = newarchivepage
archivepage.save('Archiving from [[Wikidata:Requests for permissions/Bot]]')
listpage.text = newbotpage
listpage.save('Archiving closed requests to [['+archivepagename+']]')
