#!/usr/bin/python
# -*- coding: utf-8  -*-
# Capture the proposed sessions for Wikimania and put them into a spreadsheet
# Mike Peel     12-Jun-2019     Initial version

from __future__ import unicode_literals
import pywikibot
import numpy as np
import time
import string
from pywikibot import pagegenerators
import time
import sys
import string
import datetime
import re

# Make sure we have the right encoding
reload(sys)
sys.setdefaultencoding('utf-8')

site = pywikibot.Site('wikimania', 'wikimania')
repo = site.data_repository()


targetcat = 'Category:2019:Submissions'
cat = pywikibot.Category(site, targetcat)
groups = pagegenerators.SubCategoriesPageGenerator(cat, recurse=False);
count = 0
seen = []
multispace = []
for group in groups:
    if group.title() != "Category:2019:Open submissions" and group.title() != "Category:2019:Accepted submissions":
        print(group.title())
        pages = pagegenerators.CategorizedPageGenerator(group, recurse=False);
        for page in pages:
            if page.title() not in seen:
                print(page.title())
                seen.append(page.title())
                count = count + 1
            else:
                if page.title() not in multispace:
                    multispace.append(page.title())
        # text = page.get()
        # print(text)
        # exit()
print(count)
for line in multispace:
    print line
# print(multispace)
multispace = list(multispace)
groups = pagegenerators.SubCategoriesPageGenerator(cat, recurse=False);
# file = open('2019_submissions.csv','w')
# file.write('Status, Reviewer comment, URL, Space, Title, Description, Theme, Outcomes, Proposers, Type, Requirements, Multispace\n')


# Check for submissions that aren't in the space categories
print(len(multispace))
groups = pagegenerators.SubCategoriesPageGenerator(cat, recurse=False);
for group in groups:
    if group.title() == "Category:2019:Open submissions":
        print(group.title())
        pages = pagegenerators.CategorizedPageGenerator(group, recurse=False);
        for page in pages:
            if page.title() not in seen:
                print(page.title())
                seen.append(page.title())
                count = count + 1
print(count)
exit()

for group in groups:
    if group.title() != "Category:2019:Open submissions" and group.title() != "Category:2019:Accepted submissions":
        print(group.title().replace('Category:','').replace(':','_').replace(' submissions','') + ".csv")
        file = open(group.title().replace('Category:','').replace(':','_').replace(' submissions','') + ".csv",'w')
        file.write('Status, Reviewer comment, URL, Space, Title, Description, Theme, Outcomes, Proposers, Type, Requirements, Multispace\n')
        space = group.title().replace('Category:','').replace(':',' ').replace(' submissions','')
        pages = pagegenerators.CategorizedPageGenerator(group, recurse=False);
        for page in pages:
            print(page.title())
            text = page.get()
            # print(text)
            try:
                text = text.split('The submission form starts at the "Description" subheading. -->')[1]
            except:
                text = text.split('__NOTOC__')[1]
            text = text.replace('<!-- Instructions: Provide a short, useful title that will describe exactly what the session will be about when it appears in the programming grid. Most folks will only use the title to determine if they will attend, so choose wisely! -->','')
            title = text.split('===')[1].strip()
            if title == "Title":
                title = text.split('===')[2].strip()
            if title == 'Description' or title == '':
                title = page.title().split('/')[1].strip()
            if page.title() in multispace:
                ismultispace = "yes"
            else:
                ismultispace = ""
            try:
                description = text.split('Description')[1].split('===')[1]
                description = description.replace('<!-- Instructions: Describe the topic of this session, the problem it is identifying or attempting to solve, or the lesson it is attempting to teach Included images and links if you wish. -->','').strip()
                description = description.replace('<!-- Instructions: Using 100-300 words, describe the topic of this session, the problem it is identifying or attempting to solve, or the lesson it is attempting to teach. Including images and links are encouraged. There is also a section for links below. -->','').strip()
                description = description.replace('<!-- Instructions: Describe the topic of this poster, the problem it is identifying or attempting to solve, or the lesson it is attempting to teach. Included images and links if you wish. -->','').strip()
                description = description.replace('<!-- Instructions: Describe the topic of this session, the problem it is identifying or attempting to solve, or the lesson it is attempting to teach Include images and links if you wish. -->','').strip()
                description = description.replace('"',"'")
            except:
                try:
                    description = text.split(title)[1].split('===')[1]
                    description = description.replace('<!-- Instructions: Describe the topic of this session, the problem it is identifying or attempting to solve, or the lesson it is attempting to teach Included images and links if you wish. -->','').strip()
                    description = description.replace('<!-- Instructions: Using 100-300 words, describe the topic of this session, the problem it is identifying or attempting to solve, or the lesson it is attempting to teach. Including images and links are encouraged. There is also a section for links below. -->','').strip()
                    description = description.replace('<!-- Instructions: Describe the topic of this poster, the problem it is identifying or attempting to solve, or the lesson it is attempting to teach. Included images and links if you wish. -->','').strip()
                    description = description.replace('<!-- Instructions: Describe the topic of this session, the problem it is identifying or attempting to solve, or the lesson it is attempting to teach Include images and links if you wish. -->','').strip()
                    description = description.replace('"',"'")
                except:
                    description = ''
            try:
                theme = text.split('Relationship to the theme')[1].split('===')[1].strip()
                theme = theme.replace("<small>This session will address the conference theme — ''[[Theme|Wikimedia, Free Knowledge and the Sustainable Development Goals]]'' — in the following manner:</small>",'').strip()
                theme=  theme.replace('<!-- Instructions: Describe how your session relates to at least one of the 17 SDGs, and helps address at least one of their respective targets. You can learn about these targets on the official website https://sustainabledevelopment.un.org/sdgs and an explanation of how Wikimedia relates to these targets on the conference website: https://wikimania.wikimedia.org/wiki/2019:Theme/FAQ#Is_Wikimedia_really_contributing_to_all_the_goals?  -->','').strip()
                theme = theme.replace('<!-- Instructions: Describe how your session relates to at least one of the 17 UN SDGs, and helps address at least one of their respective targets. You can learn about these targets on the official website https://sustainabledevelopment.un.org/sdgs and an explanation of how Wikimedia relates to these targets on the conference website: https://wikimania.wikimedia.org/wiki/2019:Theme/FAQ#Is_Wikimedia_really_contributing_to_all_the_goals?  -->','').strip()
                theme = theme.replace('"',"'")
            except:
                theme = ''
            try:
                outcomes = text.split('Session outcomes')[1].split('===')[1].strip()
                outcomes = outcomes.replace('<small>At the end of the session, the following will have been achieved:</small>','').strip()
                outcomes = outcomes.replace('<!-- Instructions: Feel free to use a bullet list or a paragraph. -->','').strip()
                outcomes = outcomes.replace('*','').strip()
                outcomes = outcomes.replace('"',"'")
            except:
                outcomes = ''
            try:
                leaders = text.split('Session leader(s)')[1].split('===')[1].strip()
                leaders = leaders.replace('<!-- Instructions: Write/sign your name here. Optionally, you may include your affiliation, role, and/or website.','').strip()
                leaders = leaders.replace('<!-- Instructions: Please add your contact info below. Note that full name and email address are mandatory. Please also add your username (if you have one you can simply sign), your affiliation, country and any other personal detail you feel relevant for us to address you when contacting you, such as role, website etc. If there are more than 3 leaders to the session, please add more lines. Please note -- submissions without complete details will not be considered. If for any reason you cannot have your details shared publicly, please send the information privately to shani.even{{@}}gmail.com, stating the name of your submission.','').strip()
                leaders = leaders.replace('Add more lines, as required. -->','').strip()
                leaders = leaders.replace('Please do not forget to enable e-mails from other wiki users in your settings, or alternatively, please provide an e-mail address where you can be reached.','').strip()
                leaders = leaders.replace('*','').strip()
                leaders = leaders.replace('\n ','\n').strip()
                leaders = leaders.replace('"',"'")
            except:
                try:
                    leaders = text.split('Author(s)')[1].split('===')[1].strip()
                    leaders = leaders.replace('<!-- Instructions: Write/sign your name here. Optionally, you may include your affiliation, role, and/or website.','').strip()
                    leaders = leaders.replace('Add more lines, as required. -->','').strip()
                    leaders = leaders.replace('*','').strip()
                    leaders = leaders.replace('\n ','\n').strip()
                    leaders = leaders.replace('"',"'")
                except:
                    leaders = ''
            try:
                sessiontype = text.split('Session type')[1].split('===')[1].strip()
                sessiontype = sessiontype.replace("<small>Each ''Space'' at Wikimania 2019 will have specific format requests. The [[2019:Program design|program design]] prioritises submissions which are future-oriented and directly engage the audience. The format of this submission is a:</small>",'').strip()
                sessiontype = sessiontype.replace('<!-- Instructions: From the following list, delete the lines which are NOT appropriate to your session. -->','').strip()
                sessiontype = sessiontype.replace('<!-- Instructions: Please describe -->','').strip()
                sessiontype = sessiontype.replace('"',"'")
                sessiontype = sessiontype.replace('*','').strip()
                sessiontype = sessiontype.replace('<br>','').strip()
                sessiontype = sessiontype.replace('<br />','').strip()
                sessiontype = sessiontype.replace('\n ','\n').strip()
            except:
                sessiontype = ''
            try:
                requirements = text.split('Requirements')[1].split('===')[1].strip()
                requirements = requirements.replace('<small>The session will work best with these conditions:</small>','').strip()
                requirements = requirements.replace('<!-- Instructions: Describe what kind of physical setup is most appropriate for your session (for example: a small classroom, a lecture hall, a projector + screen, round-table seating...)  -->','').strip()
                requirements = requirements.replace('<!-- Instructions: How many people would be appropriate to attend/participate in this session? Would they need to have prior knowledge/skills? -->','').strip()
                requirements = requirements.replace('<!-- Instructions: Describe whether format, and content, of this session is appropriate for filming by a single fixed-location camera, sharable on the internet, with a free-licence. The answer to this question is affected equally by the subject (for privacy, participant comfort, or copyright) or format (e.g. if multiple conversations are happening simultaneously). -->','').strip()
                requirements = requirements.replace('*','').strip()
                requirements = requirements.replace('"',"'")
                requirements = requirements.replace("\n\n","\n")
                requirements = requirements.replace("\n\n","\n")
            except:
                requirements = ''
            try:
                requirements = requirements.split('<!--Instructions: If you are making a submission')[0]
            except:
                null = 0

            file.write(',,"https://wikimania.wikimedia.org/wiki/'+page.title()+'", "'+space.replace('2019','').strip()+'", "'+title+'", "'+description+'", "'+theme+'", "'+outcomes+'", "'+leaders+'", "'+sessiontype+'", "'+requirements+'", "'+ismultispace+'"\n')
        file.close()
exit()
