#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Look at random galleries to see if they are worth keeping or not
# Mike Peel     01-Mar-2018      v1 - start
import pywikibot
from pywikibot import pagegenerators

# import sys
# # sys.setdefaultencoding() does not exist, here!
# reload(sys)  # Reload does the trick!
# sys.setdefaultencoding('UTF8')

commons = pywikibot.Site('commons', 'commons')
repo = commons.data_repository()  # this is a DataSite object

maxnum = 100

numchecked = 0
seen = []
good = []
bad_0 = []
bad_1 = []
bad_2 = []
bad_3 = []
bad_4 = []
bad_5 = []
while numchecked < maxnum:
	targets = pagegenerators.RandomPageGenerator(total=120, site=commons, namespaces='0')
	for target in targets:
		print(target.title())
		if target.title() not in seen:
			numchecked += 1
			seen.append(target.title())
			text = target.get()
			text = text.lower()

			# Check for unmarked files

			lines = text.splitlines()
			trip = 0
			for i in range(0,len(lines)):
				if '</gallery' in lines[i]:
					trip = 0
				if trip == 1:
					if 'file:' not in lines[i] and 'image:' not in lines[i]:
						lines[i] = 'file:'+lines[i]
				if '<gallery' in lines[i]:
					trip = 1
			text = "\n".join(lines)
			text = text.replace(':file:','').replace(':image:','')

			count = text.count('file:')
			count = count + text.count('image:')

			# print(text)
			# print(count)
			# test = input('Continue?')

			if count == 0:
				bad_0.append(target.title())
			elif count == 1:
				bad_1.append(target.title())
			elif count == 2:
				bad_2.append(target.title())
			elif count == 3:
				bad_3.append(target.title())
			elif count == 4:
				bad_4.append(target.title())
			elif count == 5:
				bad_5.append(target.title())
			else:
				good.append(target.title())

		if numchecked >= maxnum:
			print('Reached the maximum of ' + str(maxnum) + ' entries checked, quitting!')
			break

print('== Bad (0 files) ==')
for line in bad_0:
	print('* [['+line+']]')
print('== Bad (1 file) ==')
for line in bad_1:
	print('* [['+line+']]')
print('== Bad (2 files) ==')
for line in bad_2:
	print('* [['+line+']]')
print('== Bad (3 files) ==')
for line in bad_3:
	print('* [['+line+']]')
print('== Bad (4 files) ==')
for line in bad_4:
	print('* [['+line+']]')
print('== Bad (5 files) ==')
for line in bad_5:
	print('* [['+line+']]')
print('== Good ==')
for line in good:
	print('* [['+line+']]')

# EOF