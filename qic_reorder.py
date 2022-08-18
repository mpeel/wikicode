#!/usr/bin/python
# -*- coding: utf-8  -*-
# Test for rearranging QIC nominations by status

import pywikibot
import numpy as np
import time
import string
from pywikibot import pagegenerators
from pywikibot.data import api
import urllib
import random

commons = pywikibot.Site('commons', 'commons')

# Get the list of open candidates -
listpage = pywikibot.Page(commons, 'Commons:Quality images candidates/candidate list')
split_text = "== May 19, 2022 ==\n<gallery>\n"
split_text2 = "</gallery>"
candidates_before = listpage.text.split(split_text)[1].split(split_text2)[0]
candidates = candidates_before.splitlines()
candidates_pending = []
candidates_done = []
for candidate in candidates:
	if candidate != '':
		# print(candidate)
		usercount = 0
		if '/Promotion' in candidate or '/Decline' in candidate:
			candidates_done.append(candidate)
		else:
			candidates_pending.append(candidate)
rebuild = ''
for candidate in candidates_pending:
	rebuild += candidate + '\n\n'
for candidate in candidates_done:
	rebuild += candidate + '\n\n'
# print(rebuild)
listpage.text = listpage.text.replace(candidates_before,rebuild)
listpage.save('Testing reordering to move reviewed to the end of the gallery for the day, please give feedback at  [[Commons_talk:Quality_images_candidates#Re-ordering_nominations?]]')
