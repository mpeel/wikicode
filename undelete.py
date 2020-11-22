#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Undelete images on Commons
# Mike Peel     19-Sep-2018      v1 - start

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

# Connect to commons
commons = pywikibot.Site('commons', 'commons')

to_undelete = ["File:Litoral sul 1.jpg","File:Praia litoral sul 2.jpg","File:Interior da Igreja de São Bento.jpg","File:Igreja de São Bento setembro 2018.jpg","File:Igreja da Terceira ordem do Carmo.jpg","File:FaroldoCaboBranco.jpg","File:Brennand's view.jpg","File:Brennand's garden.jpg","File:Brennand's entrance.jpg","File:Igreja da Ordem Terceira de São Franciso.jpg","File:Vista do porão da igreja.jpg","File:Igreja da Ordem terceira de São Franciso (com filtro).jpg","File:Instituto Brennand, parte interna do castelo.jpg","File:Lago dos cisnes.jpg","File:Lago interno.jpg","File:ForteSantaCatarina.jpg"]
editsummary = "Per undelete request at https://commons.wikimedia.org/w/index.php?title=User_talk%3ASealle&type=revision&diff=321746856&oldid=321695608"
remove = ["{{delete|reason=Last remaining files, small images without EXIF data, unlikely to be own works.|subpage=Files uploaded by PennyLane89075|year=2018|month=September|day=17}}"]
replace = []#[["[[Category:Drawing]]", "[[Category:Works by Gretchen Andrew]]"]]

def restoreimage(pagetitle, editmessage, texttoremove, texttoreplace):
    page = pywikibot.Page(commons, pagetitle)

    test = page.undelete(editmessage)

    text = page.get()
    for i in range(0,len(texttoremove)):
        text = text.replace(texttoremove[i], '')
    for i in range(0,len(texttoreplace)):
        print texttoreplace[i][0]
        print texttoreplace[i][1]
        text = text.replace(texttoreplace[i][0], texttoreplace[i][1])
    text = text.replace("\n\n", "\n")
    page.text = text.strip()
    try:
        page.save(editmessage)
        return 1
    except:
        print "That didn't work!"
        return 0

stop = 0
for j in range(0,len(to_undelete)):
    try:
        test = restoreimage(to_undelete[j], editsummary, remove, replace)
        print test
        stop = 1
    except:
        print j
        print "That didn't work"
    # if stop:
        # exit()