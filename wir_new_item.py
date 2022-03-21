#!/usr/bin/python
# Matches Wikipedia articles with Wikidata items 
# Started 6 December 2021 by Mahfuza
# 21 November 2018 - focus on Category:Online dictionaries

import pandas as pd
import wikipedia
import pywikibot 
import requests
from pywikibot import pagegenerators

wiki = pywikibot.Site('wikidata', 'wikidata') 
wiki_repo = wiki.data_repository() 

enwiki = pywikibot.Site('en', 'wikipedia')
enwiki_repo = enwiki.data_repository() 

targetcat = 'Category:Online dictionaries'
cat = pywikibot.Category(enwiki, targetcat)

subpages = pagegenerators.CategorizedPageGenerator(cat, recurse=False)

# extracting date variants
def date_extractor(line_with_date): 
    df = pd.Series(line_with_date)
    df.head(10)

    # 04/20/2009; 04/20/09; 4/20/09; 4/3/09
    search1 = dict()
    for ind,vals in dict(df.apply(lambda x:re.search('\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',x))).items():
        if vals:
            search1[ind]=vals.group()

    # Mar-20-2009; Mar 20, 2009; March 20, 2009; Mar. 20, 2009; Mar 20 2009;
    search2 = dict()
    for ind,vals in dict(df.apply(lambda x:re.search(r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-zA-Z.,-]*[\s-]?(\d{1,2})?[,\s-]?[\s]?\d{4}',x,re.I|re.M))).items():
        if vals and (ind not in list(search1.keys())):
            search2[ind]=vals.group()

    # 6/2008; 12/2009
    search3 = dict()
    for ind,vals in dict(df.apply(lambda x:re.search(r'\d{1,2}[/-]\d{4}',x,re.M|re.I))).items():
        if vals and (ind not in (list(search1.keys()) + list(search2.keys()))):
            search3[ind]=vals.group()

    # 2009; 2010
    search4 = dict()
    for ind,vals in dict(df.apply(lambda x:re.search(r'\d{4}',x,re.M|re.I))).items():
        if vals and (ind not in (list(search1.keys()) + list(search2.keys()) + list(search3.keys()))):
            search4[ind]=vals.group()
    date_series = pd.concat([pd.Series(search1),pd.Series(search2),pd.Series(search3),pd.Series(search4)])
    date = date_series.to_string(index=False)

    return date

#find QID
def wiki_title_to_wikidata_id(title: str) -> str:
        protocol = 'https'
        base_url = 'en.wikipedia.org/w/api.php'
        params = f'action=query&prop=pageprops&format=json&titles={title}'
        url = f'{protocol}://{base_url}?{params}'
        
        response = requests.get(url)
        json = response.json()
        for pages in json['query']['pages'].values():
            wikidata_id = pages['pageprops']['wikibase_item']
        return wikidata_id

def newitem(category, items):
	new_item = pywikibot.ItemPage(repo)
	new_item.editLabels(labels={"en":category.title().replace('Category:','')}, summary="Creating item")
	candidate_item = pywikibot.ItemPage(repo, new_item.getID())
	print candidate_item

	data = {'sitelinks': [{'site': 'commonswiki', 'title': category.title()}]}
	candidate_item.editEntity(data, summary=u'Add commons sitelink')

	for item in items:
		claim = pywikibot.Claim(repo, item[0])
		if item[0] == 'P569' or item[0] == 'P570':
			claim.setTarget(item[1])
		else:
			claim.setTarget(pywikibot.ItemPage(repo, item[1]))
		try:
			candidate_item.addClaim(claim, summary=u'Setting '+item[0]+' value')
			claim.addSources([statedin, retrieved], summary=u'Add source.')
		except:
			print "That didn't work"
	return

for subpage in subpages:
    article_name = subpage.title()
    wikidata_item = pywikibot.ItemPage.fromPage(subpage)      
    article = subpage.text
    item_dict = wikidata_item.get() 

    try:
        test = item_dict['claims']['P577']
       
    except:
        for line in article.split("."):
            if 'publish' in line:
                date = date_extractor(line.strip())
                QID = wiki_title_to_wikidata_id(article.title())
                items.append(['P577', QID]) 
                new_item = newitem(subpage, items)
                newclaim = pywikibot.Claim(repo, 'P910')
                newclaim.setTarget(new_item)
                topic_item.addClaim(newclaim, summary=u'Link to category item')
        	break 

            else:
                print("This article does not have any info about publishing date.")  
