# Get a list of users and check their gender setting, to see gender bias in permissions/user groups
# Mike Peel  22 November 2020  Start

import urllib
import urllib.request
import urllib.parse
import json
import pywikibot
from wir_newpages import *
import requests


def getURL(url='', retry=True, timeout=30):
	raw = ''
	req = urllib.request.Request(url, headers={ 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:55.0) Gecko/20100101 Firefox/55.0' })
	try:
		raw = urllib.request.urlopen(req, timeout=timeout).read().strip().decode('utf-8')
	except:
		sleep = 10 # seconds
		maxsleep = 900
		while retry and sleep <= maxsleep:
			print('Error while retrieving: %s' % (url))
			print('Retry in %s seconds...' % (sleep))
			time.sleep(sleep)
			try:
				raw = urllib.request.urlopen(req, timeout=timeout).read().strip().decode('utf-8')
			except:
				pass
			sleep = sleep * 2
	return raw


def getUserByStatus(status='', site='',useaurights=False):
	if useaurights:
		editcounturl = 'https://%s/w/api.php?action=query&list=allusers&aurights=%s&usprop=gender&format=json&aulimit=500' % (site, urllib.parse.quote(status))
	else:
		editcounturl = 'https://%s/w/api.php?action=query&list=allusers&augroup=%s&usprop=gender&format=json&aulimit=500' % (site, urllib.parse.quote(status))
	raw = getURL(editcounturl)
	json1 = json.loads(raw)
	# print(json1)
	returnarr = []
	for line in json1['query']['allusers']:
		print(line['name'])
		if line['name'] != '':
			returnarr.append(line['name'])
	return returnarr

def getUserGender(user='', site=''):
	if user and site:
		editcounturl = 'https://%s/w/api.php?action=query&list=users&ususers=%s&usprop=gender&format=json' % (site, urllib.parse.quote(user))
		raw = getURL(editcounturl)
		json1 = json.loads(raw)
		print(json1)
		if 'query' in json1 and 'users' in json1['query'] and 'gender' in json1['query']['users'][0]:
			return json1['query']['users'][0]['gender']
	return 0

users = getUserByStatus(status='autopatrol',site='en.wikipedia.org',useaurights=True)
# users = getUserByStatus(status='rollback',site='en.wikipedia.org',useaurights=True)
# users = getUserByStatus(status='sysop',site='en.wikipedia.org')
# users = getUserByStatus(status='bureaucrat',site='en.wikipedia.org')
print(users)

print(len(users))
male = 0
female = 0
unknown = 0

for user in users:
	val = getUserGender(user=user,site="en.wikipedia.org")
	if val == 'male':
		male += 1
	elif val == 'female':
		female += 1
	else:
		unknown += 1

print(male)
print(female)
print(unknown)
