#!/usr/bin/python
# -*- coding: utf-8  -*-
# Copy descriptions to captions
# Mike Peel     27-Jan-2019      v1

from __future__ import unicode_literals

import pywikibot
import numpy as np
import time
import string
from pywikibot import pagegenerators
import urllib
import pprint
import csv
from database_login import *

database = False
manual = True
maxnum = 1000000
usetemplate = 0
usecategory = 1
wikidata_site = pywikibot.Site("wikidata", "wikidata")
repo = wikidata_site.data_repository()  # this is a DataSite object
commons = pywikibot.Site('commons', 'commons')

def get_login_token(site):
     params = { 'action' :'query', 
                'meta' : 'tokens',
                'type' : 'login',
                'format' : 'json'}
     request = pywikibot.data.api.Request(site=site, parameters=params)
     return request.submit()

def do_login(site,token):

    loginmanager = pywikibot.data.api.LoginManager(password=commons_testbot_pass, sysop=False, site=site, user=commons_testbot_username)
    return loginmanager.login()

     # params = { 'action' :'login', 
     #            'lgname' : commons_testbot_username,
     #            'lgpassword' : commons_testbot_pass,
     #            'format' : 'json',
     #            'lgtoken':token}
     # request = pywikibot.data.api.Request(site=site, parameters=params)
     # return request.submit()

def get_token(site):
     params = { 'action' :'query', 
                'meta' : 'tokens',
                'format' : 'json'}
     request = pywikibot.data.api.Request(site=site, parameters=params)
     return request.submit()

def get_userinfo(site):
     params = { 'action' :'query', 
                'meta' : 'userinfo',
                'format' : 'json'}
     request = pywikibot.data.api.Request(site=site, parameters=params)
     return request.submit()

def get_mid(site, itemtitle):
     params = { 'action' :'query', 
                'prop' : 'info',
                'format' : 'json',
                'titles' : itemtitle}
     request = pywikibot.data.api.Request(site=site, parameters=params)
     return request.submit()

def get_caption(site, itemtitle):
     params = { 'action' :'wbgetentities', 
                'format' : 'json',
                'ids': itemtitle}
     request = pywikibot.data.api.Request(site=site, parameters=params)
     return request.submit()

def set_caption(site, itemtitle, caption,language='en'):
     loginmanager = pywikibot.data.api.LoginManager(password=commons_testbot_pass, sysop=False, site=site, user=commons_testbot_username)
     print loginmanager.login()
     print loginmanager.get_login_token()
     # print loginmanager.getCookie()
     # test = pywikibot.login.LoginManager(password=commons_testbot_pass,site=site, user=commons_testbot_username)
     # print test.botAllowed()
     # test.login()
     # prettyPrint(test)
     # caption = 'Sala Sao Paulo, Brazil'
     caption = caption.replace(' ','%20')
     print caption
     params = { 'action' :'wbsetlabel', 
                'format' : 'json',
                # 'lgname' : commons_testbot_username,
                'token': loginmanager.get_login_token(),
                'id': itemtitle,
                'language' : language,
                'value': caption}
     print params
     # print pywikibot.data.api.encode_url(params)
     request = pywikibot.data.api.Request(site=site, parameters=params)
     return request.submit()

def prettyPrint(variable):
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(variable)

def check_and_set_caption(target):

    # token = get_login_token(commons)
    # prettyPrint(token)
    # print token['query']['tokens']['logintoken']
    # login = do_login(commons, token['query']['tokens']['logintoken'])
    # prettyPrint(login)
    # tokens = get_token(commons)
    # prettyPrint(tokens)
    # edittoken = tokens['query']['tokens']['csrftoken']
    # print edittoken
    # userinfo = get_userinfo(commons)
    # prettyPrint(userinfo)
    # return 1

    print target.title()
    filetext = target.get()
    if '{{en|1=' in filetext:
        caption = filetext.split('{{en|1=')[1].split('}}')[0]
        print caption
    # Get the media ID
    mid_temp = get_mid(commons, target.title())
    prettyPrint(mid_temp)
    for val in mid_temp['query']['pages']:
        # print val
        mid = val
    print mid

    captions = get_caption(commons, 'M'+str(mid))
    prettyPrint(captions)

    test = set_caption(commons, 'M'+str(mid), caption,language='en')

    return 0

# That's the end of the function definitions, now run them.

file = pywikibot.Page(commons, 'File:Sala São Paulo 2018 07.jpg')
check_and_set_caption(file)

# EOF