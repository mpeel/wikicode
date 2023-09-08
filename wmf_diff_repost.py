#!/usr/bin/python
# -*- coding: utf-8  -*-
#
# Script to post diff updates via RSS on-wiki
# Mike Peel    08 Sep 2023    Started
import datetime
import feedparser
import pywikibot

# Get the page we want to save the table to
site = pywikibot.Site('en', 'wikipedia')
repo = site.data_repository()
page = pywikibot.Page(site, u"User:Mike Peel/Sandbox")

now = datetime.datetime.now()
text = u'Here are the latest posts from [https://diff.wikimedia.org/ Wikimedia Diff] as of ' + str(datetime.date(now.year, now.month, now.day)) + '!\n'

feed = feedparser.parse("https://diff.wikimedia.org/feed/")
entries = feed["items"]

for item in entries:
	date = datetime.datetime.strptime(item['published'].replace('+0000','').strip(), '%a, %d %b %Y %H:%M:%S').strftime('%d %b %Y')
	text = text + "* [" + item['links'][0]['href'] + ' ' + item['title'] + "] (" + date + ")\n"
print(text)
page.text = text
page.save(u"Updating")
