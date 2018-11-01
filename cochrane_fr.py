#!/usr/bin/python
# -*- coding: utf-8  -*-
# License: MIT
import pywikibot
import re
import requests
import datetime

from pywikibot import pagegenerators

debug = False
maxnum = 500
reportpage = 'Utilisateur:Mike Peel/Brouillon'#'Wikipedia:WikiProject_Medicine/Cochrane_update'

def update_report(page, old_pmid, new_pmid, ):
    report = pywikibot.Page(site, reportpage)
    report_text = report.get()
    rep = u'\n*Article [[%s]] ([{{fullurl:%s|action=edit}} edit]) ancienne critique [https://www.ncbi.nlm.nih.gov/pubmed/%s PMID:%s] nouvelle critique [https://www.ncbi.nlm.nih.gov/pubmed/%s PMID:%s]' % (page.title(), page.title(),old_pmid, old_pmid, new_pmid, new_pmid)
    if rep in report_text:
        return
    report.text = report_text + rep + u' - ~~~~~'
    report.save(u'Rapport de mise à jour à inclure ' + page.title())

checkedpages = {}

site = pywikibot.Site('fr', 'wikipedia')

# First clean up the report page
report = pywikibot.Page(site, reportpage)
report_text = report.get()
report_text = report_text.splitlines()
archive = pywikibot.Page(site, reportpage+"/Archiver")
archive_text = archive.get()
report_text_new = ''
# print report_text
for line in report_text:
    print line
    # exit()
    if "{{Fait" in line:
        archive_text = archive_text + "\n" + line
    elif "{{fait" in line:
        archive_text = archive_text + "\n" + line
    else:
        report_text_new = report_text_new + "\n" + line
print report_text_new
print archive_text
if debug == False:
    archive.text = archive_text.strip()
    archive.save("Archivage d'anciens rapports")
    report.text = report_text_new.strip()
    report.save("Archivage d'anciens rapports")

regexes = ["insource:/\| périodique =.+Cochrane/", "insource:/\| périodique=.+Cochrane/", "insource:/\|périodique =.+Cochrane/", "insource:/\|périodique=.+Cochrane/","insource:/\| titre =.+Cochrane/", "titre:/\| title=.+Cochrane/", "insource:/\|titre =.+Cochrane/", "insource:/\|titre=.+Cochrane/"]
i = 0
nummodified = 0

todaysdate = datetime.datetime.now()
todaysdate.strftime("%B")
datestr = "|date = " + todaysdate.strftime("%B %Y")
print datestr

for regex in regexes:
    generator = pagegenerators.SearchPageGenerator(regex, site=site, namespaces=[0])
    gen = pagegenerators.PreloadingGenerator(generator)

    for page in gen:
        # print checkedpages
        # print page
        # page = pywikibot.Page(site, "Alzheimer's disease")
        i += 1
        try:
            text = page.get()
        except:
            continue
        pmids = re.findall(r'\|\s*?pmid\s*?\=\s*?(\d+?)\s*?\|', text)
        print len(pmids)
        for pmid in pmids:
            if str(pmid) not in checkedpages:
                print 'https://www.ncbi.nlm.nih.gov/pubmed/%s' % pmid
                try:
                    r = requests.get('https://www.ncbi.nlm.nih.gov/pubmed/%s' % pmid, timeout=10.0)
                    res = r.text
                except:
                    continue
                # if 'WITHDRAWN' in res and re.search(r'<h3>Update in</h3><ul><li class="comments"><a href="/pubmed/\d+?"', res):
                if re.search(r'<h3>Update in</h3><ul><li class="comments"><a href="/pubmed/\d+?"', res):
                    pm = re.findall(r'<h3>Update in</h3><ul><li class="comments"><a href="/pubmed/(\d+?)"', res)[0]
                    print pm
                    checkedpages[str(pmid)] = pm
                    # Check to make sure that the new paper doesn't also have an updated version...
                    try:
                        r2 = requests.get('https://www.ncbi.nlm.nih.gov/pubmed/%s' % pm, timeout=10.0)
                        res2 = r2.text
                    except:
                        continue
                    if '<title>WITHDRAWN' in res2:
                        # The new one's been withdrawn: we don't want to report this as an update.
                        checkedpages[str(pmid)] = 0
                    if 'WITHDRAWN' in res2 and re.search(r'<h3>Update in</h3><ul><li class="comments"><a href="/pubmed/\d+?"', res2):
                        pm2 = re.findall(r'<h3>Update in</h3><ul><li class="comments"><a href="/pubmed/(\d+?)"', res2)[0]
                        try:
                            r3 = requests.get('https://www.ncbi.nlm.nih.gov/pubmed/%s' % pm2, timeout=10.0)
                            res3 = r3.text
                            if '<title>WITHDRAWN' in res3:
                                # This new one has also been withdrawn, giving up.
                                checkedpages[str(pmid)] = 0
                            else:
                                checkedpages[str(pmid)] = pm2
                        except:
                            continue
                else:
                    checkedpages[str(pmid)] = 0
            else:
                print 'using cache for ' + str(pmid)
            print checkedpages[str(pmid)]
            if checkedpages[str(pmid)] != 0:
                if '<!-- No update needed: ' + str(pmid) + ' -->' not in text:
                    up = u'{{Update inline|reason=Updated version https://www.ncbi.nlm.nih.gov/pubmed/' + checkedpages[str(pmid)]
                    if not up in text:
                        text = re.sub(ur'(\|\s*?pmid\s*?\=\s*?%s\s*?(?:\||\}\}).*?\< *?\/ *?ref *?\>)' % pmid,ur'\1%s}}' % (up+str(datestr)), text, re.DOTALL)
                        if debug == False:
                            update_report(page, pmid, checkedpages[str(pmid)])
        if text != page.text and debug == False:
        #     page.text = text
        #     page.save(u'Adding "update inline" template for Cochrane reference')
            nummodified += 1
            if nummodified > maxnum - 1:
                print 'Reached the maximum of ' + str(maxnum) + ' pages modified, quitting!'
                exit()

print str(i) + " pages checked, " + str(nummodified) + " tagged!"
