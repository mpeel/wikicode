# License: MIT
import pywikibot
import re
import requests
import datetime

from pywikibot import pagegenerators

debug = False
maxnum = 500

def update_report(page, old_pmid, new_pmid, ):
    report = pywikibot.Page(site, 'Wikipedia:WikiProject_Medicine/Cochrane_update')
    report_text = report.get()
    rep = u'\n*Article [[%s]] ([{{fullurl:%s|action=edit}} edit]) old review [https://pubmed.ncbi.nlm.nih.gov/%s PMID:%s] new review [https://pubmed.ncbi.nlm.nih.gov/%s PMID:%s]' % (page.title(), page.title(),old_pmid, old_pmid, new_pmid, new_pmid)
    if rep in report_text:
        return
    report.text = report_text + rep + u' - ~~~~~'
    report.save('Update report to include ' + page.title())

checkedpages = {}
reportpage = 'Wikipedia:WikiProject_Medicine/Cochrane_update'

site = pywikibot.Site('en', 'wikipedia')

# First clean up the report page
report = pywikibot.Page(site, reportpage)
report_text = report.get()
report_text = report_text.splitlines()
archive = pywikibot.Page(site, reportpage+"/Archive_1")
archive_text = archive.get()
report_text_new = ''
# print(report_text)
for line in report_text:
    print(line)
    # exit()
    if "{{done}}" in line:
        archive_text = archive_text + "\n" + line
    elif "{{Done}}" in line:
        archive_text = archive_text + "\n" + line
    else:
        report_text_new = report_text_new + "\n" + line
print(report_text_new)
print(archive_text)
if debug == False:
    archive.text = archive_text.strip()
    archive.save('Archiving old reports')
    report.text = report_text_new.strip()
    report.save('Archiving old reports')

regexes = ["insource:/\| journal =.+Cochrane/", "insource:/\| journal=.+Cochrane/", "insource:/\|journal =.+Cochrane/", "insource:/\|journal=.+Cochrane/","insource:/\| title =.+Cochrane/", "title:/\| title=.+Cochrane/", "insource:/\|title =.+Cochrane/", "insource:/\|title=.+Cochrane/"]
i = 0
nummodified = 0

todaysdate = datetime.datetime.now()
todaysdate.strftime("%B")
datestr = "|date = " + todaysdate.strftime("%B %Y")
print(datestr)

for regex in regexes:
    generator = pagegenerators.SearchPageGenerator(regex, site=site, namespaces=[0])
    gen = pagegenerators.PreloadingGenerator(generator)

    for page in gen:
        # print(checkedpages)
        # print(page)
        # page = pywikibot.Page(site, "Alzheimer's disease")
        i += 1
        try:
            text = page.get()
        except:
            continue
        pmids = re.findall(r'\|\s*?pmid\s*?\=\s*?(\d+?)\s*?\|', text)
        print(len(pmids))
        for pmid in pmids:
            # pmid = '27093058'
            if str(pmid) not in checkedpages:
                print('https://pubmed.ncbi.nlm.nih.gov/%s' % pmid)
                try:
                    r = requests.get('https://pubmed.ncbi.nlm.nih.gov/%s' % pmid, timeout=10.0)
                    res = r.text
                except:
                    continue
                # if 'WITHDRAWN' in res and re.search(r'<h3>Update in</h3><ul><li class="comments"><a href="/pubmed/\d+?"', res):
                rawtext = re.sub(r'\s+', '', res)
                # print(rawtext)
                if re.search(r'data-ga-category="comment_correction"data-ga-action="(\d+?)"data-ga-label="linked-update">', rawtext):
                    pm = re.findall(r'data-ga-category="comment_correction"data-ga-action="(\d+?)"data-ga-label="linked-update">', rawtext)[0]
                    print(pm)
                    checkedpages[str(pmid)] = pm
                    # Check to make sure that the new paper doesn't also have an updated version...
                    try:
                        r2 = requests.get('https://pubmed.ncbi.nlm.nih.gov/%s' % pm, timeout=10.0)
                        res2 = r2.text
                    except:
                        continue
                    if '<title>WITHDRAWN' in res2:
                        # The new one's been withdrawn: we don't want to report this as an update.
                        checkedpages[str(pmid)] = 0
                    rawtext2 = re.sub(r'\s+', '', res2)
                    if 'WITHDRAWN' in res2 and re.search(r'data-ga-category="comment_correction"data-ga-action="(\d+?)"data-ga-label="linked-update">', rawtext2):
                        pm2 = re.findall(r'data-ga-category="comment_correction"data-ga-action="(\d+?)"data-ga-label="linked-update">', rawtext2)[0]
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
                print('using cache for ' + str(pmid))
                exit()
            print(checkedpages[str(pmid)])
            if checkedpages[str(pmid)] != 0:
                if '<!-- No update needed: ' + str(pmid) + ' -->' not in text:
                    up = u'{{Update inline|reason=Updated version https://www.ncbi.nlm.nih.gov/pubmed/' + checkedpages[str(pmid)]
                    if not up in text:
                        # text = re.sub(ur'(\|\s*?pmid\s*?\=\s*?%s\s*?(?:\||\}\}).*?\< *?\/ *?ref *?\>)' % pmid,ur'\1%s}}' % (up+str(datestr)), text, re.DOTALL)
                        print('Would update report')
                        if debug == False:
                            update_report(page, pmid, checkedpages[str(pmid)])
        if text != page.text and debug == False:
            page.text = text
            page.save(u'Adding "update inline" template for Cochrane reference')
            nummodified += 1
            if nummodified > maxnum - 1:
                print('Reached the maximum of ' + str(maxnum) + ' pages modified, quitting!')
                exit()

print(str(i) + " pages checked, " + str(nummodified) + " tagged!")
