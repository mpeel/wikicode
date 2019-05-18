#!/usr/bin/python
# -*- coding: utf-8  -*-
# 
# Script to fetch Guardian obit RSS feed, and cross-compare with Wikidata
# Mike Peel    26 Feb 2017    Started
# Mike Peel    18 Mar 2017    Bug fixes (catch more titles in nameattempt, unicode issue)
# Mike Peel    14 Apr 2017    Tweaks (split on ':')
# Mike Peel     2 Jul 2017    Bug fix (catch blank nameattempt)
import datetime
import feedparser
import pywikibot
import sys
import urllib2

reload(sys)
sys.setdefaultencoding('utf-8')

# Get the page we want to save the table to
site = pywikibot.Site('en', 'wikipedia')
repo = site.data_repository()
page = pywikibot.Page(site, u"User:Mike Peel/NYT obits")

now = datetime.datetime.now()
text = u'This page follows the [https://www.nytimes.com/section/obituaries New York Times] website (by its [https://www.nytimes.com/svc/collections/v1/publish/https://www.nytimes.com/section/obituaries/rss.xml RSS feed]), makes an attempt to identify names from the titles, and add links to possible articles and the corresponding Guardian obituary. It was last updated at ' + str(datetime.date(now.year, now.month, now.day)) + '. The code [[User:Mike Peel/Guardian obit script|is available on-wiki]]. For any maintenance issues, please leave a note for [[User talk:Mike Peel|the bot operator]].\n{| class="wikitable sortable"\n!Name !! Wikidata !! NYT obit !! Reference code !! Other sources\n'

# Independent RSS feed doesn't work!
rss_url = ["https://www.nytimes.com/svc/collections/v1/publish/https://www.nytimes.com/section/obituaries/rss.xml"]#, "http://www.independent.co.uk/news/obituaries/rss"]
entries = []
for i in range(0,len(rss_url)):
    feed = feedparser.parse(rss_url[i])
    entries = entries + feed["items"]

for item in entries:
    # Try to identify the name of the subject from the title of the page
    nameattempt = item['title'].decode('utf-8')
    nameattempt = nameattempt.replace('obituary','').replace('Letter:','').replace('Letters: ','').replace('Right Rev','').replace('Most Rev','').replace('Sir','').replace('Dame','').replace('Dr ','')
    nameattempt = nameattempt.split(u'–',1)[0]
    nameattempt = nameattempt.split(u':',1)[0]
    nameattempt = nameattempt.split(u',',1)[0]
    nameattempt = nameattempt.split(u"’s",1)[0]
    test = nameattempt.split(u"The",1)
    if len(test) == 2:
        nameattempt = test[1]
    test = nameattempt.split(' ')
    i = 0
    while i < len(test):
        if test[i].islower():
            nameattempt = nameattempt.split(test[i])[0]
            i = len(test)
        i += 1
    nameattempt = nameattempt.replace(' I ','')
    nameattempt = nameattempt.strip()
    print nameattempt
    # Reformat the date
    date = datetime.datetime.strptime(item['published'], '%a, %d %b %Y %H:%M:%S %Z').strftime('%d %b %Y')

    # Let's see if we can fetch the page from Wikidata
    if nameattempt != '':
        target_page = pywikibot.Page(site, nameattempt)
        wd_item = -1
        if target_page.exists() == True:
            # Is this a redirect?
            if target_page.isRedirectPage():
                print target_page.getRedirectTarget()
                target_page = target_page.getRedirectTarget()
                # Just in case we have a double-redirect
                if target_page.isRedirectPage():
                    target_page = target_page.getRedirectTarget()

            try:
                wd_item = pywikibot.ItemPage.fromPage(target_page)
                wd_item.get()
            except:
                print("Unexpected error:", sys.exc_info()[0])

            # Let's use the name of the actual page in place of the guess
            nameattempt = target_page.title()


        # Now write the page
        text = text + '|-\n| [[' + nameattempt + ']] || style="white-space: nowrap;" | '
        if wd_item != -1:
            wd_id = wd_item.getID()
            text = text + '[[:d:' + wd_id + '|' + wd_id + ']]'
            if 'P569' in wd_item.claims:
                birth_date = wd_item.claims['P569'][0].getTarget()
                birth_date2 = birth_date.toTimestr()
                birth_date2 = birth_date2.replace("+0000000",'').replace('T00:00:00Z','')
                text = text + "<br />b: " + birth_date2
            if 'P570' in wd_item.claims:
                death_date = wd_item.claims['P570'][0].getTarget()
                death_date2 = death_date.toTimestr()
                death_date2 = death_date2.replace("+0000000",'').replace('T00:00:00Z','')
                text = text + "<br />d: " + death_date2
        text = text + ' || [' + item['link'] + ' ' + item['title'] + '], ' + date +' || <nowiki>{{cite news | url = ' + item['link'] + ' | title = ' + item['title'] + ' | work = [[The New York Times]] | date = ' + date + '}}</nowiki> || {{Find sources|' + nameattempt + '}}\n'

text = text + u"\n|}\n"

# Test if it is the same (using splits to avoid update date changes triggering this)
# Also handle cases where the search text can't be found.
test1 = text.split('For any maintenance issues, please leave a note for')
test2 = page.text.split('For any maintenance issues, please leave a note for')
if len(test1) > 1:
    test1 = test1[1]
if len(test2) > 1:
    test2 = test2[1]
if (test1 != test2):
    page.text = text
    page.save(u"Updating")
else:
    print 'Not updating: page is identical'
