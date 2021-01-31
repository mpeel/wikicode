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
host = 'enwiki.analytics.db.svc.eqiad.wmflabs'
port = 3306

conn = pymysql.connect(
	host=host,
	user=user,
	password=password,
	port=port
)
languages = ['en']

for lang in languages:
	with conn.cursor() as cur:
		cur.execute('use '+lang+'wiki_p')
		cur.execute("SELECT page_title FROM page WHERE page_namespace=0 AND page_is_redirect=0 AND page_id NOT IN (SELECT page_id FROM page JOIN page_props ON page_id=pp_page WHERE page_namespace=0 AND pp_propname='wikibase_item')")
		vals = cur.fetchall()
		f = open("/data/project/pibot/"+lang+"wp_articles.csv", "w")
		if len(vals) > 0:
			[f.write(str(x[0])) for x in vals]
		else:
			run = False
		f.close()
		ftp = FTP('mikepeel.net',user=ftpuser,passwd=ftppass)
		ftp.cwd('wiki')
		file = open('/data/project/pibot/'+lang+'wp_articles.csv','rb')
		ftp.storbinary('STOR '+lang+'nwp_articles.csv', file)
		file.close()
		ftp.quit()
