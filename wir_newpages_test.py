# Import modules
import pywikibot
from wir_newpages import *

lang = 'en'

# Connect to enwiki
enwiki = pywikibot.Site(lang, 'wikipedia')
repo = enwiki.data_repository()  # this is a DataSite object


page = pywikibot.Page(enwiki, 'Satanmuanglek CP Freshmart')
print(page.text)
birthdate = calculateBirthDateFull(page=page,lang=lang)
print(birthdate)
deathdate = calculateDeathDateFull(page=page,lang=lang)
print(deathdate)
wd_item = pywikibot.ItemPage.fromPage(page)
# addBirthDateClaim(repo=repo,item=wd_item,date=birthdate,lang='de')
# addDeathDateClaim(repo=repo,item=wd_item,date=deathdate,lang='de')
