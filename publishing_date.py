import pandas as pd
import re 
import wikipedia
import pywikibot 
import requests
from pywikibot import pagegenerators

wiki = pywikibot.Site('wikidata', 'wikidata') 
wiki_repo = wiki.data_repository() 

enwiki = pywikibot.Site('en', 'wikipedia')
enwiki_repo = enwiki.data_repository() 

# article_name = "Oxford Dictionary of World Religions"
# QID = "Q7115313"

targetcat = 'Category:Online dictionaries'
cat = pywikibot.Category(enwiki, targetcat)

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

subpages = pagegenerators.CategorizedPageGenerator(cat, recurse=False);
for subpage in subpages:
    article_name = subpage.title()
    # print (article_name)   
    QID = wiki_title_to_wikidata_id(subpage.title())
    # print(QID)          

    article = wikipedia.page(article_name).content
    wikidata_item = pywikibot.ItemPage(wiki_repo, QID)
    item_dict = wikidata_item.get() 

    try:
        test = item_dict['claims']['P577']
        print(article_name + 'has publication date in Wikidata Item.')
    except:
        # todo: have to create new item 
        print (article_name + 'does not have publication date in Wikidata Item.')

        for item in article.split("."):
            if "published" in item:
                #check synonims for publish
                line_with_date = item.strip()
                print(line_with_date)

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
    for ind,vals in dict(df.apply(lambda x:re.search(r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-zA-Z.,-]*[\s-]?(\d{1,2})?[,\s-]?[\s]?\d{4}',
                                                     x,re.I|re.M))).items():
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
    
    # return date_series
    print(date_series)

date_extractor(line_with_date)
