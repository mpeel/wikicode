#!/usr/bin/python
# -*- coding: utf-8  -*-
# 
# Script to fetch Guardian obit RSS feed, and cross-compare with Wikidata
# Mike Peel    13 Jun 2018    Started
import datetime
import pywikibot
import sys
import urllib2
import csv
import numpy as np
import datetime

reload(sys)
sys.setdefaultencoding('utf-8')

def fixdates(datestring):
    # Split the multiple dates
    datestrings = datestring.split(",")
    print datestrings
    numdates = np.shape(datestrings)[0]
    # Reformat each of them
    dates = []
    for i in range(0,numdates):
        try:
            newdate = datetime.datetime.strptime(datestrings[i], '%m/%d/%Y %I:%M%p')
        except:
            newdate = datetime.datetime.strptime(datestrings[i], '%m/%d/%Y %I:%M %p')
        dates.append(newdate)
        if i == 0:
            firstdate = newdate
        else:
            if newdate < firstdate:
                firstdate = newdate

    # print dates
    # print firstdate
    # print firstdate.strftime('%A %d %B, %H:%M')
    # exit()
    return firstdate.strftime('%A %d %B, %H:%M')

def fixusernames(userstring):
    # Split the multiple dates
    userstrings = userstring.replace(';',',').split(",")
    numusers = np.shape(userstrings)[0]
    output = ''
    for i in range(0,numusers):
        # Strip out existing formatting
        userstrings[i] = userstrings[i].replace('[[','').replace(']]','').replace('User:','').replace('user:','').replace('_',' ')
        # Add the new formatting
        if 'TBC' not in userstrings[i]:
            userstrings[i] = "[[User:"+userstrings[i].strip()+"]]"
        userstrings[i] = "* " + userstrings[i]
        if i != numusers-1:
            output += userstrings[i] + "<br />\n"
        else:
            output += userstrings[i]
    return output

# Get the page we want to save the table to
site = pywikibot.Site('wikimania2018', 'wikimania2018')
repo = site.data_repository()

# Get the extra info
infile = open('/Users/mpeel/Desktop/Wikimania/Wikimania 2018_data_2018-06-13 (1).xlsx - Submissions.csv', mode='r')
reader = csv.reader(infile)
extras = []
for row in reader:
    test = row[5].split('(Outcomes)', 1)[-1]
    test = test.split('(Topic)', 1)[0]
    test = test.replace('•', '*')
    extras.append([row[0], row[1], row[6], test.strip()])
numextras = np.shape(extras)[0]
# print extras
# exit()
# print numextras
# exit()
# print extras
# print '297' in extras
# print extras[np.where()]
# exit()

# Read in the CSV
infile = open('/Users/mpeel/Desktop/Wikimania/Conference Program-Entire Schedule.csv - Conference Program-Entire Schedule.csv.csv', mode='r')
reader = csv.reader(infile)

i = 0
page = pywikibot.Page(site, u"User:Mike Peel/Test")
text = '__NOTOC__'
for row in reader:
    i+=1
    if i < 2:
        continue
    # print row
    # page = pywikibot.Page(site, u"Program/" + row[0])
    #text = ''
    text += "{{Session\n"
    text += "| title = " + row[0] + "\n"
    text += "| slides = Placeholder.png\n"
    if 'Workshop' in row[10]:
        text += "| workshop=yes\n"
    if 'Panel' in row[10]:
        text += "| panel=yes\n"
    if 'Roundtable' in row[10]:
        text += "| roundtable=yes\n"
    if 'Presentation' in row[10]:
        text += "| presentation=yes\n"
    if 'Poster' in row[1]:
        text += "| poster=yes\n"
    for j in range(0,numextras):
        if extras[j][0] == row[6]:
            text += "| keywords=\n* " + extras[j][2].replace("\n", "<br />\n* ") + "\n"
    if row[11] != '':
        text += "| datetime = " + fixdates(row[11]) + "\n"
        text += "| location = montreal\n"
    if row[12] != '':
        text += "| datetime = " + fixdates(row[12]) + "\n"
        text += "| location = mexico\n"
    if row[13] != '':
        text += "| datetime = " + fixdates(row[13]) + "\n"
        text += "| location = esino\n"
    if row[14] != '':
        text += "| datetime = " + fixdates(row[14]) + "\n"
        text += "| location = london\n"
    if row[15] != '':
        text += "| datetime = " + fixdates(row[15]) + "\n"
        text += "| location = hongkong\n"
    if row[1] != 'Poster':
        text += "| duration = " + row[1].replace('90','85').replace('60','55').replace('30','25') + "\n"
    else:
        text += "| duration = \n"
        text += "| datetime = Friday 20 July, 20:00 - 21:30\n"
        text += "| location = plenary\n"
    if row[3] != '':
        text += "| presenters = " + fixusernames(row[3]) + "\n"
    else:
        text += "| presenters = " + row[2] + "\n"

    if 'Advocacy' in row[7]:
        text += '| advocacy=yes\n'
    if 'Communities &' in row[7]:
        text += '| collaboration=yes\n'
    if 'GLAM' in row[7]:
        text += '| glam=yes\n'
    if 'Governance' in row[7]:
        text += '| governance=yes\n'
    if 'Research' in row[7]:
        text += '| research=yes\n'
    if 'Science' in row[7]:
        text += '| science=yes\n'
    if 'Technology' in row[7]:
        text += '| technology=yes\n'
    if 'Other' in row[7]:
        text += '| other=yes\n'

    if 'Language' in row[8]:
        text += "| language=yes\n"
    if 'Quality' in row[8]:
        text += "| quality=yes\n"
    if 'Access' in row[8]:
        text += "| access=yes\n"
    if 'Legal' in row[8]:
        text += "| legal=yes\n"
    if 'Participation' in row[8]:
        text += "| participation=yes\n"
    if 'Knowledge' in row[8]:
        text += "| knowledge=yes\n"
    if 'Community' in row[8]:
        text += "| community=yes\n"
    text += "| abstract = " + row[5].encode('utf-8') + "\n"
    for j in range(0,numextras):
        if extras[j][0] == row[6]:
            text += "| outcomes=" + extras[j][3] + "\n"
    text += "| related = \n"
    text += "}}\n"
    text += "==Signup==\n"
    text += "* <add your username here if you are interested in attending>\n"

    text += '</div><br style="clear:both;" />\n\n'
    # page.text = text
    # page.save(u"Test edit")

print text
page.text = text
page.save(u"Test edit")


