#!/usr/bin/python
# -*- coding: utf-8  -*-
# 
# Script to fetch the Google Spreadsheet with the info in, and write it to a meta page.
# Mike Peel        18 Feb 2017    Started
# Mike Peel        19 Feb 2017    Bug fixes, link to code location
# Mike Peel        01 Sep 2017    Encoding fixes
# Joe Sutherland   01 Sep 2017    Updating to match new sheet

import csv
import datetime
import pywikibot
import urllib2
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

# Fetch the spreadsheet
url = 'https://docs.google.com/spreadsheets/d/1DruVc7T9ZqTcfGwFAlxQrBMR4QBSD_DtjpDtGqMAAi0/pub?output=csv'
response = urllib2.urlopen(url)
cr = csv.reader(response)

# Get the page we want to save the table to
site = pywikibot.Site('meta', 'meta')
repo = site.data_repository()
page = pywikibot.Page(site, u"WMF Advanced Permissions")

now = datetime.datetime.now()
text = u'This table is a mirror of the Google spreadsheet [https://docs.google.com/spreadsheet/pub?key=0AvhjkTJIpW2zdDl1bVBuOU1jQUJwOHd5YmhmSzFaZHc here], please arrange changes to that spreadsheet rather than changing this page yourself. The table was last <abbr title="The data in this wikitable being identical to the Google spreadsheet data at that time, apart from formatting.">synchronized</abbr> at ' + str(datetime.date(now.year, now.month, now.day)) + '. The synchronisation code [[User:Mike Peel/WMF permissions script|is available on-wiki]]. For any maintenance issues, please leave a note for [[User talk:Mike Peel|the bot operator]].\n{| class="wikitable sortable"\n!Username !! Received !! Usecase !! Rights\n|-'

i = 0
for row in cr:
    if i > 0: # First row is header and example, which we don't want.
        date = row[2].split('/')
        if len(date) == 3:
            if len(date[0]) == 1:
                date[0] = '0' + str(date[0])
            if len(date[1]) == 1:
                date[1] = '0' + str(date[1])
            date = date[2] + '-' + date[0] + '-' + date[1]
        else:
            date = row[2]

        reason = row[4]
        reason = reason.replace('[[Category:','[[:Category:')
        reason = reason.replace('[[category:','[[:category:')
        text += u'\n|-\n| [[Special:CentralAuth/' + row[1] + '|' + row[1] + ']]\n| align="center" | ' + date + '\n| ' + reason + '\n| ' + row[3]
    i += 1

text = text + u"\n|}\n[[Category:User groups]]\n[[Category:Wikimedia Foundation staff| WMF Advanced Permissions]]"

# Test if it is the same (using splits to avoid update date changes triggering this)
# Also handle cases where the search text can't be found.
test1 = text.split('The synchronisation code [[User:Mike Peel')
test2 = page.text.split('The synchronisation code [[User:Mike Peel')
if len(test1) > 1:
    test1 = test1[1]
if len(test2) > 1:
    test2 = test2[1]
if (test1 != test2):
    page.text = text
    page.save(u"Updating")
else:
    print 'Not updating: page is identical'