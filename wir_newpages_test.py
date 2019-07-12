# Import modules
import pywikibot
from wir_newpages import *

# Connect to enwiki
enwiki = pywikibot.Site('de', 'wikipedia')
repo = enwiki.data_repository()  # this is a DataSite object


page = pywikibot.Page(enwiki, 'Jørgen Fleischer')
print(page.text)
birthdate = calculateBirthDateFull(page=page,lang='de')
print(birthdate)
deathdate = calculateDeathDateFull(page=page,lang='de')
print(deathdate)
wd_item = pywikibot.ItemPage.fromPage(page)
addBirthDateClaim(repo=repo,item=wd_item,date=birthdate,lang='de')
addDeathDateClaim(repo=repo,item=wd_item,date=deathdate,lang='de')
