#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Example pywikibot code description here
# Mike Peel     17-Sep-2018      v1 - start

# Import modules
import pywikibot
from pywikibot import pagegenerators
from pywikibot.data import api
import numpy as np
import requests

# You may need to enforce the use of utf-8
import sys
reload(sys)
sys.setdefaultencoding('UTF8')

# Connect to ptwiki
ptwiki = pywikibot.Site('pt', 'wikipedia')
# and then to wikidata
ptwiki_repo = ptwiki.data_repository()

def editarticle(page):
    text = page.get()
    text = text + "\nThis is a test edit"
    page.text = text
    try:
        page.save("Saving test edit")
        return 1
    except:
        print "That didn't work!"
        return 0

def editarticle2(page):
    text = page.get()
    text = text.replace('This is a test edit','Isto é uma edição de teste')
    page.text = text
    try:
        page.save("Saving test edit")
        return 1
    except:
        print "That didn't work!"
        return 0

def printwikidata(wd_item):
    qid = wd_item.title()
    print qid

    item_dict = wd_item.get()

    try:
        print 'Name: ' + item_dict['labels']['en']
    except:
        print 'No English label!'
    try:
        print 'ptwiki article: ' + item_dict['sitelinks']['ptwiki']
    except:
        print 'No Portuguese article!'
    try:
        print item_dict['claims']['P31']
    except:
        print 'No P31'

    try:
        for claim in item_dict['claims']['P31']:
            p31_value = claim.getTarget()
            p31_item_dict = p31_value.get()
            print 'P31 value: ' + p31_value.title()
            print 'P31 label: ' + p31_item_dict['labels']['en']
    except:
        print "That didn't work!"
    return 0

def editwikidata(wd_item, propertyid, value):
    qid = wd_item.title()
    print qid
    item_dict = wd_item.get()

    claim_target = pywikibot.ItemPage(ptwiki_repo, value)
    newclaim = pywikibot.Claim(ptwiki_repo, propertyid)
    newclaim.setTarget(claim_target)

    print newclaim
    text = raw_input("Save? ")
    if text == 'y':
        wd_item.addClaim(newclaim, summary=u'Adding test claim')

    return 0

def parsesite(url):
    try:
        r = requests.get(url)
        websitetext = r.text
    except:
        print 'Problem fetching page!'
        return 0
    # print websitetext
    split = websitetext.split("<h1 style='display:none'>")
    i = 0
    for item in split:
        i+=1
        # Skip the top part
        if i > 2:
            # print item
            print 'Title: ' + item.split('</h1>')[0].strip() + '\n'
            print 'Museum: ' + item.split("strong>Museu:</strong><span itemprop='publisher'>")[1].split("</span>")[0].strip() + "\n"
    return 0

# From https://gist.github.com/ettorerizza/7eaebbd731781b6007d9bdd9ddd22713
def search_entities(site, itemtitle):
     params = { 'action' :'wbsearchentities', 
                'format' : 'json',
                'language' : 'en',
                'type' : 'item',
                'search': itemtitle}
     request = api.Request(site=site, parameters=params)
     return request.submit()

# Page must exist already!
page = pywikibot.Page(ptwiki, 'Usuário(a):Mike_Peel/teste')
test = editarticle(page)
print test
test = editarticle2(page)

page = pywikibot.ItemPage(ptwiki_repo, 'Q511405')
test = printwikidata(page)

sparql = "SELECT ?item WHERE { ?item wdt:P31 wd:Q184356 } LIMIT 10"
generator = pagegenerators.WikidataSPARQLPageGenerator(sparql, site=ptwiki_repo)
for page in generator:
    printwikidata(page)

targetcat = 'Categoria:Telescópios'
cat = pywikibot.Category(ptwiki, targetcat)
subcats = pagegenerators.SubCategoriesPageGenerator(cat, recurse=False);
for subcat in subcats:
    print subcat.title()

pages = pagegenerators.CategorizedPageGenerator(cat, recurse=False);
for page in pages:
    print page.title()

template = pywikibot.Page(ptwiki, 'Predefinição:Info/Telescópio')
targets = template.embeddedin()
for target in targets:
    print target.title()

targets = pagegenerators.RandomPageGenerator(total=10, site=ptwiki, namespaces='14')
for target in targets:
    print target.title()

wikidataEntries = search_entities(ptwiki_repo, "Neuromat")
if wikidataEntries['search'] != []:
    results = wikidataEntries['search']
    numresults = len(results)
    for i in range(0,numresults):
        qid = results[i]['id']
        label = results[i]['label']
        print qid + " - " + label

# Do a test edit to Wikidata
testqid = 'Q4115189' # Wikidata sandbox
testproperty = 'P31' # instance of
testvalue = 'Q3938'  # Sandbox
wd_item = pywikibot.ItemPage(ptwiki_repo, testqid)
print editwikidata(wd_item, testproperty, testvalue)

parsesite('http://www.museusdoestado.rj.gov.br/sisgam/index.php?pagina=1&operador=or&busca=a%20b%20c%20d%20e%20f%20g%20h%20i%20j%20k%20l%20m%20n%20o%20p%20q%20r%20s%20t%20u%20v%20w%20x%20y%20z&museu=todos&qresultados=40')
