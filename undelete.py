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

to_undelete = ["File:Powerful-person-17.jpg", "File:Powerful-person-18.jpg", "File:Powerful-person-16.jpg", "File:Powerful-person-15.jpg", "File:Powerful-person-14.jpg", "File:Powerful-person-13.jpg", "File:Powerful-person-12.jpg", "File:Powerful-person-11.jpg", "File:Powerful-person-10.jpg", "File:Powerful-person-8.jpg", "File:Powerful-person-9.jpg", "File:Powerful-person-7.jpg", "File:Powerful-person-6.jpg", "File:Powerful-person-5.jpg", "File:Powerful-person-4.jpg", "File:Powerful-person-2.jpg", "File:Powerful-person-3.jpg", "File:Powerful-person-1.jpg", "File:Female-conception-14.jpg", "File:Female-conception-13.jpg", "File:Female-conception-12.jpg", "File:Female-conception-11.jpg", "File:Female-conception-10.jpg", "File:Female-conception-9.jpg", "File:Female-conception-8.jpg", "File:Female-conception-7.jpg", "File:Female-conception-4.jpg", "File:Female-conception-5.jpg", "File:Female-conception-1.jpg", "File:Female-conception-2.jpg", "File:Female-conception-3.jpg", "File:Bow-new-hampshire-48.jpg", "File:Bow-new-hampshire-47.jpg", "File:Bow-new-hampshire-46.jpg", "File:Bow-new-hampshire-44.jpg", "File:Bow-new-hampshire-45.jpg", "File:Bow-new-hampshire-43.jpg", "File:Bow-new-hampshire-42.jpg", "File:Bow-new-hampshire-41.jpg", "File:Bow-new-hampshire-39.jpg", "File:Bow-new-hampshire-40.jpg", "File:Bow-new-hampshire-38.jpg", "File:Bow-new-hampshire-37.jpg", "File:Bow-new-hampshire-36.jpg", "File:Bow-new-hampshire-35.jpg", "File:Bow-new-hampshire-33.jpg", "File:Bow-new-hampshire-34.jpg", "File:Bow-new-hampshire-30.jpg", "File:Bow-new-hampshire-32.jpg", "File:Bow-new-hampshire-31.jpg", "File:Displacement-8.jpg", "File:Displacement-9.jpg", "File:Displacement-7.jpg", "File:Displacement-3.jpg", "File:Displacement-6.jpg", "File:Displacement-4.jpg", "File:Displacement-5.jpg", "File:Displacement-2.jpg", "File:Displacement-1.jpg", "File:Displacement-0.jpg"]
editsummary = "Per undelete request at https://commons.wikimedia.org/w/index.php?title=Commons:Undeletion_requests/Current_requests&diff=320165883&oldid=320161477"
remove = ["{{delete|reason=Self-created artwork without obvious educational uses, out of [[COM:SCOPE]]. See [[Commons:Project scope/Summary]].|subpage=Files uploaded by Gretchenandrew|year=2018|month=February|day=6}}"]
replace = [["[[Category:Drawing]]", "[[Category:Works by Gretchen Andrew]]"]]

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
    page.text = text
    try:
        page.save(editmessage)
        return 1
    except:
        print "That didn't work!"
        return 0

for j in range(0,len(to_undelete)):
    test = restoreimage(to_undelete[j], editsummary, remove, replace)
    print test
