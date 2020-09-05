# !/usr/bin/python
# -*- coding: utf-8  -*-
# Generation of short descriptions, which writes them into a staging file/wikipage
# Mike Peel     08-Aug-2020     v1 - start
# Mike Peel     05-Sep-2020     v2 - rewrite to have more options, moving operational code into shortdesc_functions.py

# Import functions, ignore this and look at configuration below.
from shortdesc_functions import *

# This is the enwp category you want to look at
targetcat = 'Category:English footballers'

# The maximum number of new short descriptions to stage
maxnum = 100

# Set to 'False' to disable all page editing, 'True' otherwise
debug = True

# Start from a given point in a category. Set trip to 'True' to enable, then define startpoint to the page title in the next line, and an endpoint if you want. Note that this goes by the order in the category, it is not alphabetical!
trip = True
startpoint = ''
endpoint = ''

# If the articles must require an infobox (as defined by the next line)
require_infobox = False 
infobox_strings = ['nfobox']

# Options for what to include in the short description. Starts with a base string, with options that can be added afterwards.
description = 'English footballer'
add_birth_date = True
add_death_date = True

# Do you want to stage this on-wiki or in a local file? Set the onwiki_page to '' to use local_file.
onwiki_page = ''#'User:Mike Peel/shortdesc'
local_file = 'test.txt'

# Run staging code
shortdesc_stage(targetcat, maxnum, debug, trip, startpoint, endpoint, require_infobox, infobox_strings, description, add_birth_date, add_death_date,onwiki_page,local_file)

# Check if we want to make the edits
input('Check the staging output please, then press return to save the edits')

# Make the edits
shortdesc_add(debug,onwiki_page,local_file)

# EOF