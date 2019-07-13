# Import modules
import pywikibot
from wir_newpages import *

lang = 'de'

# Connect to enwiki
enwiki = pywikibot.Site(lang, 'wikipedia')
repo = enwiki.data_repository()  # this is a DataSite object


page = pywikibot.Page(enwiki, 'Simon Coppel')
print(page.text)
print(authorIsNewbie(page=page,lang=lang))
print(pageIsRubbish(page,lang=lang))
print(pageIsBiography(page,lang=lang))
birthdate = calculateBirthDateFull(page=page,lang=lang)
print(birthdate)
deathdate = calculateDeathDateFull(page=page,lang=lang)
print(deathdate)
wd_item = pywikibot.ItemPage.fromPage(page)
addBirthDateClaim(repo=repo,item=wd_item,date=birthdate,lang=lang)
# addDeathDateClaim(repo=repo,item=wd_item,date=deathdate,lang=lang)
