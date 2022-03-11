from __future__ import unicode_literals
#!/usr/bin/python
# -*- coding: utf-8  -*-
# Compare the lists outputted by commons_photos.py and Lightroom_extract_filenames.py to get unique ones.
# Mike Peel		17-Jul-2016		v1 - initial version

import numpy as np
import time
import string
from pywikibot import pagegenerators
import codecs

text_file = codecs.open("commons_photos.txt", "r", encoding='utf-8')
commons = text_file.readlines()
text_file.close()

text_file = codecs.open('filenames.txt', "r", encoding='utf-8')
lightroom = text_file.readlines()
text_file.close()

commons_only = list(set(commons) - set(lightroom))

local_only = list(set(lightroom) - set(commons))


text_file = codecs.open('commons_only.txt', 'w', encoding='utf-8')
for item in commons_only:
  text_file.write("%s" % item)
text_file.close()


text_file = codecs.open('local_only.txt', 'w', encoding='utf-8')
for item in local_only:
  text_file.write("%s" % item)
text_file.close()
