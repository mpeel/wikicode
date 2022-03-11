#!/usr/bin/python
# -*- coding: utf-8  -*-
# Fetch a list of Commons filenames from Lightroom
# Mike Peel		17-Jul-2016		v1 - initial version

from __future__ import unicode_literals

import sqlite3
import numpy as np
import time
import string
import urlparse
import codecs
from libxmp.utils import *
import sys
import binascii
# sys.setdefaultencoding() does not exist, here!
reload(sys)  # Reload does the trick!
sys.setdefaultencoding('UTF8')

con = sqlite3.connect('/Volumes/Maxtor4TB/Photos/Lightroom/Lightroom-2.lrcat')
# con.text_factory = bytes
cursor = con.cursor()
f = codecs.open('Lightroom_filenames.txt',mode='w', encoding='utf-8')
# i = 0
databases = []
for row_tuple in cursor.execute("SELECT name FROM sqlite_master WHERE type='table';"):
	print row_tuple[0]
	databases.append(row_tuple[0])
		# exit()

for row_tuple in cursor.execute(u"SELECT * FROM Adobe_AdditionalMetadata;"):
	# if 'File:' in row_tuple:
	print row_tuple
	xmp = row_tuple[-1]
	print xmp

	# with open("Output.xml", "wb") as output_file:
		# output_file.write(row_tuple[14])

	# print binascii.hexlify(xmp)
	# print xmp.read()
	# print eval(str(xmp))
	# print xmp.decode('hex')
	# print object_to_dict(xmp)
	exit()
	# print str(row_tuple[14]).decode('utf-8')
	# for row in row_tuple[14]:
		# print row
	# print type(row_tuple[14])
	# try:
	# 	row = row_tuple[14]#.decode('unicode_escape').encode('utf-8',errors='replace')
	# 	# print type(row)
	# 	print row
	# except:
	# 	null = 1
	# print row
	# exit()

# 	startchar = row.find(u"<dc:title>")
# 	endchar = row.find(u"</dc:title>", startchar)
# 	selected = row[startchar:endchar]
# 	# print selected+"\n\n"
# 	if (selected != ""):
# 		# print "Hello!\n"
# 		startchar2 = selected.find(u"x-default")
# 		startchar2 += 11
# 		endchar2 = selected.find(u"</rdf:li>", startchar2)
# 		selected2 = selected[startchar2:endchar2]

# 		# f.write(selected2.decode('unicode_escape').encode('utf8','ignore')+"\n")
# 		# f.write(selected2.decode('unicode_escape','ignore')+"\n")
# 		if (selected2.find(u'</rdf:Alt>') == -1 and selected2 != u"&#xA;"):
# 			# print selected2
# 			# selected2 = selected2.replace("n\u0301",u'ń')
# 			# print selected2+"\n"
# 			# f.write(selected2.encode('utf8').decode('unicode_escape')+u"\n")
# 			f.write(selected2.replace(u'&amp;',u'&').replace(u'&#xA;',u'\n')+u"\n")
# 			# print r" "+selected2+r"\n"

# f.close()
