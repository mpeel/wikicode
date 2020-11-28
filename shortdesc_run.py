# !/usr/bin/python
# -*- coding: utf-8  -*-
# Generation of short descriptions, which writes them into a staging file/wikipage
# Released under the GNU General Public License v3.
# Mike Peel     08-Aug-2020     v1 - start
# Mike Peel     05-Sep-2020     v2 - rewrite to have more options, moving operational code into shortdesc_functions.py
# Mike Peel     12-Sep-2020     v3 - expanding
# Mike Peel     28-Nov-2020     v4 - adding required_words, excluded_words, only_one_infobox options

# To run this code you need to have pywikibot, dateparser and re installed and in your python path. This is python3 code. Set the configuration options below, then run the script. You can select which part of the script you want to run by commenting/uncommenting shortdesc_stage and shortdesc_add. The first function prepares the new short descriptions and stages them, the second function saves them to enwp.

# Import functions, ignore this and look at configuration below.
import pywikibot
from shortdesc_functions import *

# This is the enwp category you want to look at
targetcat = 'Category:Spanish footballers'

# The maximum number of new short descriptions to stage. 'maxnum' is the number of articles to look through, 'maxnum_new' is the number of new short descriptions to stage, the code stops at whichever comes first.
maxnum = 100
maxnum_new = 1

# Set to 'True' to disable all automatic page editing, 'False' otherwise. If it is 'True' then you'll need to reply 'y' or 'n' to prompts.
debug = True

# Start from a given point in a category. Set trip to 'True' to enable, then define startpoint to the page title in the next line, and an endpoint if you want. Note that this goes by the order in the category, it is not alphabetical!
trip = True
startpoint = ''
endpoint = ''

# If the articles must require an infobox (as defined by the next line)
require_infobox = True 
infobox_strings = ['infobox']
only_one_infobox = True # Only use pages with one infobox

# Options for what to include in the short description. Starts with a base string, with options that can be added afterwards.
description = 'Spanish footballer'
add_birth_date = True
add_death_date = True

# Do you want to stage this on-wiki or in a local file? Set the onwiki_page to '' to use local_file.
onwiki_page = ''#'User:Mike Peel/shortdesc'
local_file = 'test.txt'

# Check the first sentence to make sure it has or hasn't got these words in it
required_words = ['foot']
excluded_words = ['blah']

# Here you can test individual articles if you want.
# wikipedia = pywikibot.Site('en', 'wikipedia')
# page = pywikibot.Page(wikipedia, 'Robert Dowland')
# print(shortdesc_generator(wikipedia, page, debug, trip, startpoint, endpoint, require_infobox, infobox_strings, only_one_infobox, description, add_birth_date, add_death_date, required_words, excluded_words))
# Comment out this next line to continue further
# exit()


# Run staging code
shortdesc_stage(targetcat, maxnum, maxnum_new, debug, trip, startpoint, endpoint, require_infobox, infobox_strings, only_one_infobox, description, add_birth_date, add_death_date,required_words,excluded_words,onwiki_page,local_file)

# Check if we want to make the edits
input('Check the staging output please, then press return to save the edits')

# Set a minimum wait time between edits. Time in seconds.
wait_time = 1.0

# Also save the descriptions to Wikidata if they don't already have a description? True/False.
also_wikidata = True

# Make the edits
shortdesc_add(debug,onwiki_page,local_file,wait_time,also_wikidata)

# EOF