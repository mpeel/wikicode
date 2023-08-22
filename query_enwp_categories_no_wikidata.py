#!/usr/bin/python3
# -*- coding: utf-8  -*-
import pymysql
import os
from ftplib import FTP
from ftplogin import *


login_file = open("replica.my.cnf","r")
login = login_file.readlines()
user = login[1].replace('user = ','').strip()
password = login[2].replace('password = ','').strip()
port = 3306

languages = ['en', 'pt', 'de', 'simple','es','fr','it','nl','pl','sv','eo','dag']

for lang in languages:
	host = lang+'wiki.analytics.db.svc.wikimedia.cloud'
	conn = pymysql.connect(
		host=host,
		user=user,
		password=password,
		port=port
	)
	with conn.cursor() as cur:
		cur.execute('use '+lang+'wiki_p')
		cur.execute("SELECT page_title FROM page WHERE page_namespace=14 AND page_is_redirect=0"\
		" AND page_id NOT IN (SELECT page_id FROM page JOIN page_props ON page_id=pp_page WHERE page_namespace=14 AND pp_propname='wikibase_item')"\
		" AND page_id NOT IN (SELECT page_id FROM page JOIN page_props ON page_id=pp_page WHERE page_namespace=14 AND pp_propname='noindex')"\
		" AND page_id NOT IN (SELECT page_id FROM page JOIN page_props ON page_id=pp_page WHERE page_namespace=14 AND pp_propname='hiddencat')")
		# cur.execute("SELECT page_title FROM page JOIN page_props ON page_id = pp_page WHERE pp_propname = 'unexpectedUnconnectedPage' AND pp_sortkey = -14;")
		vals = cur.fetchall()
		f = open("/data/project/pibot/"+lang+"wp_categories.csv", "w", encoding='utf-8')
		if len(vals) > 0:
			[f.write(str(x[0])+'\n') for x in vals]
		else:
			run = False
		f.close()
		ftp = FTP('mikepeel.net',user=ftpuser,passwd=ftppass)
		ftp.cwd('wiki')
		file = open('/data/project/pibot/'+lang+'wp_categories.csv','rb')
		ftp.storbinary('STOR '+lang+'wp_categories.csv', file)
		file.close()
		ftp.quit()
