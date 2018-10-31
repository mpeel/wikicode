#!/usr/bin/python
# -*- coding: utf-8  -*-
# Move the coordinate template from the wikitext into the infobox
# Mike Peel     17-Aug-2018      v1

from __future__ import unicode_literals

import pywikibot
from pywikibot.data import api
import numpy as np
import time
import string
from pywikibot import pagegenerators
import urllib
import pprint
import csv

site = pywikibot.Site("en", "wikipedia")
repo = site.data_repository()

template = 'Infobox observatory'
alt_template = 'Infobox Observatory'
templateparam = 'coordinates'
def movecoord(article):
    print article.title()
    if article.title() == 'Royal Observatory, Greenwich':
        return 0
    # article = pywikibot.Page(site, page)
    article_text = article.get()
    if "{{coord" not in article_text:
        return 0
    # print article_text

    # Look for the infobox
    infobox_text = article_text
    try:
        infobox_text = article_text.split("{{"+template)[1]
    except:
        print "That didn't work"
    if infobox_text == article_text:
        infobox_text = article_text.split("{{"+alt_template)[1]
        article_text = article_text.replace(template, alt_template)
    print infobox_text

    # infobox_text_copy = infobox_text
    # diff = 1
    # while diff > 0:
    #     nextstart = infobox_text.find('{')
    #     infobox_text = infobox_text[:nextstart] + '[' + infobox_text[nextstart+1:]
    #     nextend = infobox_text.find('}')
    #     infobox_text = infobox_text[:nextend] + ']' + infobox_text[nextend+1:]
    #     diff = nextend-nextstart
    #     print nextend
    #     # print infobox_text
    #     # print diff
    #     # print nextstart
    #     # print nextend
    #     # print diff
    # # Need to do this once more
    # nextend = infobox_text.find('}')
    # infobox_text = infobox_text[:nextend] + ']' + infobox_text[nextend+1:]
    # # print infobox_text
    # # print nextend
    # infobox_text = infobox_text_copy[:nextend]
    # # print infobox_text
    # # exit()

    coordinate = "{{coord"+(article_text.split("{{coord"))[1].split("}}")[0]+"}}"
    # print coordinate

    # if coordinate in infobox_text:
    #     return 0

    article_text = article_text.replace(coordinate+'\n','')
    article_text = article_text.replace(coordinate,'')
    article_text = article_text.replace('{{'+template,'{{'+template+'\n| '+templateparam+" = " + coordinate)
    print '\n\n\n\n'
    print article_text
    print article.title()
    text = raw_input("Save? ")
    if text == 'y':
        try:
            article.text = article_text
            article.save('Moving coordinates into infobox')
            return 1
        except:
            print "That didn't work!"
            return 0

    return 0

targettemplate = pywikibot.Page(site, 'Template:'+template)
targetpages = targettemplate.embeddedin()
i = 0
nummodified = 0
for target in targetpages:
    i += 1
    nummodified += movecoord(target)
    print str(nummodified) + ', ' + str(i) + 'checked'
