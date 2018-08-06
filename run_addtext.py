from __future__ import unicode_literals
#!/usr/bin/python
# -*- coding: utf-8  -*-
# Add some text to a wiki page
# Mike Peel     11-Jul-2017     v1 - initial version

from addtext import addtext
import sys
sys.setdefaultencoding('utf-8')

file = open('torecat.txt', 'r') 
toedit = file.readlines() 

text = "[[Category:Images from Wiki Loves Earth Biosphere Reserves 2017]]"
othertext = "{{Wiki Loves Earth 2017|unesco}}"
addtext('commons','commons', toedit, text, othertext,trialrun=0)
