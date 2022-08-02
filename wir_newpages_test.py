# Import modules
import pywikibot
import datetime
import dateparser
from wir_newpages import *

lang = 'en'
article = 'Donald Broadnax'
enwp_site = 'enwiki'

# Connect to enwiki
enwiki = pywikibot.Site(lang, 'wikipedia')
repo = enwiki.data_repository()  # this is a DataSite object
page = pywikibot.Page(enwiki, article)
# for cat in page.categories():
# 	print(cat.title())
# exit()
# if '#redirect' in page.text.lower():
# 	print("Page is a redirect but isn't marked as one")
# for template, _ in page.templatesWithParams():
# 	print(template)

# exit()
# Create a new item
# new_item = pywikibot.ItemPage(repo)
# new_item.editLabels(labels={"en":page.title()}, summary="Creating item")
# itemfound = pywikibot.ItemPage(repo, new_item.getID())
# data = {'sitelinks': [{'site': enwp_site, 'title': page.title()}]}
# itemfound.editEntity(data, summary=u'Add '+enwp_site+' sitelink')

# itemfound = pywikibot.ItemPage.fromPage(page)
# addBiographyClaims(repo=repo, wikisite=enwiki, item=itemfound, page=page, lang=lang)

# exit()

# Test code
# print(page.text)
# print(authorIsNewbie(page=page,lang=lang))
print(pageIsRubbish(page,lang=lang))
print(pageIsBiography(page,lang=lang))
birthdate = calculateBirthDate(page=page,lang=lang)
print(birthdate)
deathdate = calculateDeathDate(page=page,lang=lang)
if deathdate != '0-0-0':
	print(deathdate)
print(calculateGender(page,lang=lang))
itemfound = pywikibot.ItemPage.fromPage(page)
# addDeathDateClaim(repo=repo,item=wd_item,date=deathdate,lang=lang)
# exit()
# addBiographyClaims(repo=repo, wikisite=enwiki, item=itemfound, page=page, lang=lang)

# deathdate = '2021-01-01'
# addDateClaim(repo=repo, item='Q4115189', claim='P569', date=deathdate, lang='en')
exit()

# print(page.title().encode('utf-8'), 'need item')
# wtitle = page.title()
# wtitle_ = wtitle.split('(')[0].strip()
# searchitemurl = 'https://www.wikidata.org/w/api.php?action=wbsearchentities&search=%s&language=%s&format=xml' % (urllib.parse.quote(wtitle_), lang)
# raw = getURL(searchitemurl)
# print(searchitemurl.encode('utf-8'))

# #check birthdate and if it matches, then add data
# numcandidates = '' #do not set to zero
# if not '<search />' in raw:
# 	m = re.findall(r'id="(Q\d+)"', raw)
# 	numcandidates = len(m)
# 	print("Found %s candidates" % (numcandidates))
# 	if numcandidates > 5: #too many candidates, skiping
# 		print("Too many, skiping")
# 	print(raw)
# 	for itemfoundq in m:
# 		print(itemfoundq)
# 		itemfound = pywikibot.ItemPage(repo, itemfoundq)
# 		itemfound.get()
# 		if ('%swiki' % (lang)) in itemfound.sitelinks:
# 			print("Candidate %s has sitelink, skiping" % (itemfoundq))
# 			numcandidates -= 1
# 			continue
# 		pagebirthyear = calculateBirthYear(page=page, lang=lang)
# 		pagebirthyear = pagebirthyear and int(pagebirthyear.split('-')[0]) or ''
# 		if not pagebirthyear:
# 			print("Page doesnt have birthdate, skiping")
# 			continue
# 		if 'P569' in itemfound.claims and itemfound.claims['P569'][0].getTarget().precision in [9, 10, 11]:
# 			print('OK?')
# 			continue

# wd_item = pywikibot.ItemPage.fromPage(page)
# print(wd_item.editTime())
# print(datetime.datetime.now())
# print((datetime.datetime.now()-wd_item.editTime()).seconds)
# # addBirthDateClaim(repo=repo,item=wd_item,date=birthdate,lang=lang)
# # addDeathDateClaim(repo=repo,item=wd_item,date=deathdate,lang=lang)
