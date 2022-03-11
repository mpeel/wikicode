#!/usr/bin/python
# -*- coding: utf-8  -*-
# 
# Script to cross-compare the NASA exoplanet database with Wikidata
# Fetch table from http://exoplanetarchive.ipac.caltech.edu/cgi-bin/IceTable/nph-iceTblDownload
# Mike Peel    06 Apr 2017    Started
# Mike Peel    15 Apr 2017    Continuing to write

import datetime
import feedparser
import pywikibot
import sys
import urllib2
import csv
import pprint
from pywikibot.data import api
import xml.etree.ElementTree as ET, urllib, gzip, io

def prettyPrint(variable):
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(variable)

def multipleReplace(text, wordDict):
    for key in wordDict:
        text = text.replace(key, wordDict[key])
    return text

def find_item_with_prop(site, name, prop, val):
    # Look for a match for it in Wikidata
    wikidataEntries = get_items(site, name)
    for wdEntry in wikidataEntries["search"]:
        item = pywikibot.ItemPage(repo, wdEntry['id'])
        item.get()
        claims = item.get().get('claims')
        if claims:
            if prop in claims:
                P31 = item.claims[prop][0].target.getID()
                if P31 == val:
                    return item
    return false

# Following functions from https://www.wikidata.org/wiki/Wikidata:Pywikibot_-_Python_3_Tutorial/Quantities_and_Units
def get_items(site, item_title):
    """
    Requires a site and search term (item_title) and returns the results.
    """
    params = {"action": "wbsearchentities",
              "format": "json",
              "language": "en",
              "type": "item",
              "search": item_title}
    request = api.Request(site=site, **params)
    return request.submit()

def check_target(repo, site, item, property, target):
    """
    Requires a property, value, uncertainty and unit and returns boolean.
    Returns the claim that fits into the defined precision or None.
    """
    item_dict = item.get()
    try:
        claims = item_dict["claims"][property]
    except:
        return None

    try:
        claim_exists = False
        uncert_set = False
        for claim in claims:
            wb_quant = claim.getTarget()
            if wb_quant == target:
                return claim
    except:
        return None

def check_claim_and_uncert(repo, site, item, property, data):
    """
    Requires a property, value, uncertainty and unit and returns boolean.
    Returns the claim that fits into the defined precision or None.
    """
    item_dict = item.get()
    value, upperBound, lowerBound, unit = data
    value, upperBound, lowerBound = float(value), float(upperBound), float(lowerBound)
    try:
        claims = item_dict["claims"][property]
    except:
        return None

    try:
        claim_exists = False
        uncert_set = False
        for claim in claims:
            wb_quant = claim.getTarget()
            delta_amount = float(wb_quant.amount) - float(value)
            if abs(delta_amount) < precision:
                claim_exists = True
            if wb_quant.lowerBound is None and lowerBound == 0:
                uncert_set = True
            else:
                check_lower = abs(float(wb_quant.lowerBound) - (float(value) - abs(float(lowerBound)))) < precision
                check_upper = abs(float(wb_quant.upperBound) - float(value) - float(upperBound)) < precision
                if check_upper and check_lower:
                    uncert_set = True

            if claim_exists and uncert_set:
                return claim
    except:
        return None

def check_source_set(repo, site, claim, property, source_data):
    source_claims = claim.getSources()
    if len(source_claims) == 0:
        return False

    for source in source_claims:
        try:
            stated_in_claim = source[source_data[0]]
        except:
            return False
        for claim in stated_in_claim:
            trgt = claim.target
            if trgt.id == source_data[1]:
                return True

def set_claim(repo, site, item, property, data):
    value, upperBound, lowerBound, unit = data
    value, upperBound, lowerBound = float(value), float(upperBound), float(lowerBound)
    claim = pywikibot.Claim(repo, property)
    if unit == '' and upperBound != 0:
        wb_quant = pywikibot.WbQuantity(amount=str(value), error=(str(upperBound), str(lowerBound)), site=site)
    elif unit == '' and upperBound == 0:
        wb_quant = pywikibot.WbQuantity(amount=str(value), site=site)
    elif upperBound == 0:
        unit_item = pywikibot.ItemPage(repo, unit)
        wb_quant = pywikibot.WbQuantity(amount=str(value), unit=pywikibot.ItemPage(repo, unit), site=site)
    else:
        unit_item = pywikibot.ItemPage(repo, unit)
        wb_quant = pywikibot.WbQuantity(amount=str(value), error=(str(upperBound), str(lowerBound)), unit=pywikibot.ItemPage(repo, unit), site=site)
    claim.setTarget(wb_quant)
    item.addClaim(claim, bot=False, summary="Adding data from the NASA Exoplanet Database.")
    return claim

def set_target(repo, site, item, property, target):
    claim = pywikibot.Claim(repo, property)
    claim.setTarget(target)
    item.addClaim(claim, bot=False, summary="Adding data from the NASA Exoplanet Database.")
    return claim

def create_source_claim(repo, site, claim, source_data):
    print source_data
    trgt_itempage = pywikibot.ItemPage(repo, source_data[1])
    source_claim = pywikibot.Claim(repo, source_data[0], isReference=True)
    source_claim.setTarget(trgt_itempage)
    claim.addSources([source_claim])
    return True


reload(sys)
sys.setdefaultencoding('utf-8')

# constellations = {'Com': 'Comae Berenices'}
entries = {'exoplanet': u'Q44559',
            'database': u'Q5420639'}
units = {'day': u'Q573',
        'jmass': u'Q651336',
        'parsec': u'Q12129'
        }
properties = {'discovery': u'P1046'}
source_cat = ['P143', entries['database']]
precision = 10 ** -10
methods = {'Radial Velocity': u'Q240105'}
# Get the page we want to save the table to
site = pywikibot.Site('wikidata', 'wikidata')
repo = site.data_repository()
# page = pywikibot.Page(site, u"User:Mike Peel/Guardian obits")

now = datetime.datetime.now()

# Get a copy of the exoplanet item, so we can use that as the instance of later on.
instance = pywikibot.ItemPage(repo, entries['exoplanet'])
instance.get()

# Set up the access to the Open Exoplanet Cataloggue
# url = "https://github.com/OpenExoplanetCatalogue/oec_gzip/raw/master/systems.xml.gz"
url = 'exoplanets/systems.xml.gz'
oec = ET.parse(gzip.GzipFile(fileobj=io.BytesIO(urllib.urlopen(url).read())))
planets = oec.findall(".//planet")
print planets
print planets.findtext('name')
exit()

# Open the CSV
# Should download from http://exoplanetarchive.ipac.caltech.edu/cgi-bin/nstedAPI/nph-nstedAPI?table=exoplanets
cr = csv.reader(open('exoplanets/nph-nstedAPI?table=exoplanets.csv'))

i = 0
for row in cr:
    # We want to skip the first one, but run through each of the others.
    if i != 0:
        # Get the name from the database
        name = row[0] + " " + row[1]
        # name = multipleReplace(name, constellations)
        print name + ' - ' + row[4] + ' +- ' + row[5]

        # Look for a match for it in Wikidata
        wikidataEntries = get_items(site, name)
        if len(wikidataEntries["search"]) == 0:
            # We don't have a Wikidata entry for this one yet. We should probably create it. But for now, just skip it.
            j = 0
        else:
            for wdEntry in wikidataEntries["search"]:
                item = pywikibot.ItemPage(repo, wdEntry['id'])
                item.get()
                claims = item.get().get('claims')
                if claims:
                    if 'P31' in claims: # instance of
                        P31 = item.claims['P31'][0].target.getID()
                        if P31 == entries['exoplanet']:
                            print 'We have an exoplanet with a matching name!'

                            # See if we can identify a Wikidata entry for its host
                            host = find_item_with_prop(site, row[0], u'P31', u'Q523')

                            # How about the discovery method?
                            method = methods[row[2]]
                            if method:
                                method = pywikibot.ItemPage(repo, method)
                                method.get()

                            # If we have empty uncertainties, then set them to zero
                            if row[5] == '':
                                row[5] = 0.0
                            if row[6] == '':
                                row[6] = 0.0
                            if row[10] == '':
                                row[10] = 0.0
                            if row[11] == '':
                                row[11] = 0.0
                            if row[15] == '':
                                row[15] = 0.0
                            if row[16] == '':
                                row[16] = 0.0
                            if row[25] == '':
                                row[25] = 0.0
                            if row[26] == '':
                                row[26] = 0.0
                            if row[51] == '':
                                row[51] = 0.0
                            if row[52] == '':
                                row[52] = 0.0

                            # Set up the data array
                            exoplanet_data = {u'P2146': {'data': [float(row[4]), abs(float(row[5])), abs(float(row[6])), units['day']], 'target': ''}, # Period
                                            u'P2233': {'data': [float(row[9]), abs(float(row[10])), abs(float(row[11])), ''], 'target': ''}, # Semi-major axis
                                            u'P1096': {'data': [float(row[14]), abs(float(row[15])), abs(float(row[16])), ''], 'target': ''}, # Eccentricity
                                            u'P2067': {'data': [float(row[24]), abs(float(row[25])), abs(float(row[26])), units['jmass']], 'target': ''}, # Mass
                                            u'P2583': {'data': [float(row[50]), abs(float(row[51])), abs(float(row[52])), units['parsec']], 'target': ''}, # Distance
                                            u'P397': {'data': [''], 'target': host}, # Parent astronomical body
                                            u'P1046': {'data': [''], 'target': method}, # Discovery method
                                            u'P31': {'data': [''], 'target': instance}
                                            }

                            # ... and run through checking it and importing it as needed
                            for key in exoplanet_data:
                                print key
                                # Only import the data if it has been set in the database
                                data = exoplanet_data[key]['data']
                                if data[0] != 0 and data[0] != '':
                                    claim = check_claim_and_uncert(repo, site, item, key, data)
                                    if claim:
                                        source = check_source_set(repo, site, claim, key, source_cat)
                                        if source:
                                            pass
                                        else:
                                            create_source_claim(repo, site, claim, source_cat)
                                            null = 1
                                    else:
                                        claim = set_claim(repo, site, item, key, data)
                                        create_source_claim(repo, site, claim, source_cat)
                                        null = 2

                                # ... or, if we have a target page rather than a data value
                                target = exoplanet_data[key]['target']
                                if target != '' and target != False:
                                    claim = check_target(repo, site, item, key, target)
                                    print claim
                                    if claim:
                                        source = check_source_set(repo, site, claim, key, source_cat)
                                        if source:
                                            pass
                                        else:
                                            create_source_claim(repo, site, claim, source_cat)
                                            null = 1
                                    else:
                                        claim = set_target(repo, site, item, key, target)
                                        create_source_claim(repo, site, claim, source_cat)
                                        null = 2

            exit()
    i += 1

