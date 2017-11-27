# License: MIT
import pywikibot
import re
import urllib2

from pywikibot import pagegenerators

checkedpages = {}

site = pywikibot.Site('en', 'wikipedia')
generator = pagegenerators.SearchPageGenerator('insource:/\| *journal *= *.+Cochrane/', site=site, namespaces=[0])
gen = pagegenerators.PreloadingGenerator(generator)

def update_report(page, old_pmid, new_pmid, ):
    report = pywikibot.Page(site, 'Wikipedia:WikiProject Medicine/Cochrane update/August 2017')
    report_text = report.get()
    rep = u'\n*Article [[%s]] ([{{fullurl:%s|action=edit}} edit]) old review [https://www.ncbi.nlm.nih.gov/pubmed/%s PMID:%s] new review [https://www.ncbi.nlm.nih.gov/pubmed/%s PMID:%s]' % (page.title(), page.title(),old_pmid, old_pmid, new_pmid, new_pmid)
    if rep in report_text:
        return
    report.text = report_text + rep + u' - ~~~~~'
    report.save('Bot: Update report to include ' + page.title())


for page in gen:
    # print checkedpages
    try:
        text = page.get()
    except:
        continue
    if '<!-- No update needed -->' in text:
        continue
    pmids = re.findall(r'\|\s*?pmid\s*?\=\s*?(\d+?)\s*?\|', text)
    print len(pmids)
    for pmid in pmids:
        if str(pmid) not in checkedpages:
            print 'https://www.ncbi.nlm.nih.gov/pubmed/%s' % pmid
            try:
                res = urllib2.urlopen('https://www.ncbi.nlm.nih.gov/pubmed/%s' % pmid).read().decode('utf-8')
            except:
                continue
            if 'WITHDRAWN' in res and re.search(r'<h3>Update in</h3><ul><li class="comments"><a href="/pubmed/\d+?"', res):
                pm = re.findall(r'<h3>Update in</h3><ul><li class="comments"><a href="/pubmed/(\d+?)"', res)[0]
                checkedpages[str(pmid)] = pm
            else:
                checkedpages[str(pmid)] = 0
        else:
            print 'using cache for ' + str(pmid)

        if checkedpages[str(pmid)] != 0:
            up = u'{{Update inline|reason=Updated version https://www.ncbi.nlm.nih.gov/pubmed/' + checkedpages[str(pmid)]
            if not up in text:
                text = re.sub(ur'(\|\s*?pmid\s*?\=\s*?%s\s*?(?:\||\}\}).*?\< *?\/ *?ref *?\>)' % pmid,ur'\1%s}}' % up, text, re.DOTALL)
            update_report(page, pmid, checkedpages[str(pmid)])
    if text != page.text:
        page.text = text
        page.save(u'Adding "update inline" template for Cochrane reference')
        exit()
