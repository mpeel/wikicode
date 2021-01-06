import pywikibot
import re
import requests
import datetime

from pywikibot import pagegenerators

debug = True
maxnum = 5

site = pywikibot.Site('en', 'wikipedia')

regexes = ['insource:"Bloodstock.racingpost.com/stallionbook/"']
i = 0
nummodified = 0

for regex in regexes:
    generator = pagegenerators.SearchPageGenerator(regex, site=site, namespaces=[0])
    gen = pagegenerators.PreloadingGenerator(generator)

    for page in gen:
        i += 1
        try:
            text = page.get()
        except:
            continue
        print(text)
        findids = re.findall(r'stallion.sd\?horse_id\=\s*?(\d+?)\s*?\&', text)
        print(len(findids))
        print(findids)
        exit()
        for id_val in findids:
            print(id_val)
            exit()
#             if str(pmid) not in checkedpages:
#                 print('https://pubmed.ncbi.nlm.nih.gov/%s' % pmid)
#                 try:
#                     r = requests.get('https://pubmed.ncbi.nlm.nih.gov/%s' % pmid, timeout=10.0)
#                     res = r.text
#                 except:
#                     continue
#                 # if 'WITHDRAWN' in res and re.search(r'<h3>Update in</h3><ul><li class="comments"><a href="/pubmed/\d+?"', res):
#                 rawtext = re.sub(r'\s+', '', res)
#                 # print(rawtext)
#                 if re.search(r'data-ga-category="comment_correction"data-ga-action="(\d+?)"data-ga-label="linked-update">', rawtext):
#                     pm = re.findall(r'data-ga-category="comment_correction"data-ga-action="(\d+?)"data-ga-label="linked-update">', rawtext)[0]
#                     print(pm)
#                     checkedpages[str(pmid)] = pm
#                     # Check to make sure that the new paper doesn't also have an updated version...
#                     try:
#                         r2 = requests.get('https://pubmed.ncbi.nlm.nih.gov/%s' % pm, timeout=10.0)
#                         res2 = r2.text
#                     except:
#                         continue
#                     if '<title>WITHDRAWN' in res2:
#                         # The new one's been withdrawn: we don't want to report this as an update.
#                         checkedpages[str(pmid)] = 0
#                     rawtext2 = re.sub(r'\s+', '', res2)
#                     if 'WITHDRAWN' in res2 and re.search(r'data-ga-category="comment_correction"data-ga-action="(\d+?)"data-ga-label="linked-update">', rawtext2):
#                         pm2 = re.findall(r'data-ga-category="comment_correction"data-ga-action="(\d+?)"data-ga-label="linked-update">', rawtext2)[0]
#                         try:
#                             r3 = requests.get('https://www.ncbi.nlm.nih.gov/pubmed/%s' % pm2, timeout=10.0)
#                             res3 = r3.text
#                             if '<title>WITHDRAWN' in res3:
#                                 # This new one has also been withdrawn, giving up.
#                                 checkedpages[str(pmid)] = 0
#                             else:
#                                 checkedpages[str(pmid)] = pm2
#                         except:
#                             continue
#                 else:
#                     checkedpages[str(pmid)] = 0
#             else:
#                 print('using cache for ' + str(pmid))
#             print(checkedpages[str(pmid)])
#             if checkedpages[str(pmid)] != 0:
#                 if '<!-- No update needed: ' + str(pmid) + ' -->' not in text:
#                     up = u'{{Update inline|reason=Updated version https://www.ncbi.nlm.nih.gov/pubmed/' + checkedpages[str(pmid)]
#                     if not up in text:
#                         text = re.sub(ur'(\|\s*?pmid\s*?\=\s*?%s\s*?(?:\||\}\}).*?\< *?\/ *?ref *?\>)' % pmid,ur'\1%s}}' % (up+str(datestr)), text, re.DOTALL)
#                         print('Would update report')
#                         if debug == False:
#                             update_report(page, pmid, checkedpages[str(pmid)])
#         if text != page.text and debug == False:
#             page.text = text
#             page.save(u'Adding "update inline" template for Cochrane reference')
#             nummodified += 1
#             if nummodified > maxnum - 1:
#                 print('Reached the maximum of ' + str(maxnum) + ' pages modified, quitting!')
#                 exit()

# print(str(i) + " pages checked, " + str(nummodified) + " tagged!")
