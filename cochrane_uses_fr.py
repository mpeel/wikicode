#!/usr/bin/python
# -*- coding: utf-8  -*-
# License: MIT
import pywikibot
import re
import requests
import datetime

from pywikibot import pagegenerators

debug = False
maxnum = 5e9

checkedpages = []
reportpage = 'Utilisateur:Mike Peel/Cochrane used'
pageschecked = []

site = pywikibot.Site('fr', 'wikipedia')
report = pywikibot.Page(site, reportpage)

regexes = ["insource:/\| périodique =.+Cochrane/", "insource:/\| périodique=.+Cochrane/", "insource:/\|périodique =.+Cochrane/", "insource:/\|périodique=.+Cochrane/","insource:/\| titre =.+Cochrane/", "titre:/\| title=.+Cochrane/", "insource:/\|titre =.+Cochrane/", "insource:/\|titre=.+Cochrane/"]
i = 0
nummodified = 0

reporttext = "The following Cochrane review PMIDs (and probably other non-Cochrane PMIDs mixed in...) are used in Wikipedia articles:\n\n"
for regex in regexes:
    generator = pagegenerators.SearchPageGenerator(regex, site=site, namespaces=[0])
    gen = pagegenerators.PreloadingGenerator(generator)

    for page in gen:
        # print checkedpages
        if page in pageschecked:
            continue

        print page
        pageschecked.append(page)
        i += 1
        try:
            text = page.get()
        except:
            continue
        pmids = re.findall(r'\|\s*?pmid\s*?\=\s*?(\d+?)\s*?\|', text)
        print len(pmids)
        for pmid in pmids:
            if "* " + str(pmid) + " -" not in checkedpages:
                checkedpages.append("* " + str(pmid) + " - [[" + page.title() + "]]")
            else:
                index = [idx for idx, s in enumerate(checkedpages) if "* " + str(pmid) + " -" in s][0]
                checkedpages[index] += ", [[" + page.title() + "]]"

        if len(checkedpages) > maxnum:
            print 'Reached the maximum of ' + str(maxnum) + ' pages loaded, saving!'
            break
    if len(checkedpages) > maxnum:
        print 'Reached the maximum of ' + str(maxnum) + ' pages loaded, saving!'
        break
            
print str(i) + " pages checked, " + str(len(checkedpages)) + " recorded!"
checkedpages.sort()
for i in range(0,len(checkedpages)):
    reporttext += checkedpages[i] + "\n"
report.text = reporttext
print reporttext
report.save('Update')
