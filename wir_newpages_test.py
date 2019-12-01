# Import modules
import pywikibot
import datetime
import dateparser
from wir_newpages import *

lang = 'de'

# Connect to enwiki
enwiki = pywikibot.Site(lang, 'wikipedia')
repo = enwiki.data_repository()  # this is a DataSite object


page = pywikibot.Page(enwiki, 'Ernst Krohn')
print(page.text)
print(authorIsNewbie(page=page,lang=lang))
print(pageIsRubbish(page,lang=lang))
print(pageIsBiography(page,lang=lang))
birthdate = calculateBirthDateFull(page=page,lang=lang)
print(birthdate)
deathdate = calculateDeathDateFull(page=page,lang=lang)
if deathdate != '0-0-0':
	print(deathdate)
wd_item = pywikibot.ItemPage.fromPage(page)
print(wd_item.editTime())
print(datetime.datetime.now())
print((datetime.datetime.now()-wd_item.editTime()).seconds)
# addBirthDateClaim(repo=repo,item=wd_item,date=birthdate,lang=lang)
# addDeathDateClaim(repo=repo,item=wd_item,date=deathdate,lang=lang)
