# Import modules
import pywikibot
from wir_newpages import *

# Connect to enwiki
enwiki = pywikibot.Site('en', 'wikipedia')
repo = enwiki.data_repository()  # this is a DataSite object


page = pywikibot.Page(enwiki, 'Guy Balland')
print(page.text)
birthdate = calculateBirthDateFull(page=page,lang='en')
print(birthdate)
wd_item = pywikibot.ItemPage.fromPage(page)
addBirthDateClaim(repo=repo,item=wd_item,date=birthdate,lang='en')
