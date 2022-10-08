
# Use with ssh -L 4711:commonswiki.analytics.db.svc.eqiad.wmflabs:3306 tools-login.wmflabs.org
import pymysql  # We will use pymysql to connect to the database
import os
from ftplib import FTP
from ftplogin import *

login_file = open("replica.my.cnf","r")
login = login_file.readlines()
user = login[1].replace('user = ','').strip()
password = login[2].replace('password = ','').strip()
host = 'commonswiki.analytics.db.svc.wikimedia.cloud'
port = 3306

conn = pymysql.connect(
	host=host,
	user=user,
	password=password,
	port=port
)
start = 0
step = 10
run = True
with conn.cursor() as cur:
	cur.execute('use commonswiki_p')
	cur.execute("SELECT DISTINCT pp.pp_value, p1.page_title"\
	" FROM categorylinks AS c1"\
	" JOIN page AS p1 ON c1.cl_from=p1.page_id AND p1.page_namespace=14 AND p1.page_is_redirect=0"\
	" JOIN page_props AS pp ON pp.pp_page = p1.page_id AND pp.pp_propname = 'wikibase_item'"\
	" LEFT JOIN templatelinks AS tl ON tl.tl_from = p1.page_id AND tl.tl_from_namespace = 14 AND  tl_target_id = (SELECT lt_id FROM linktarget WHERE lt_namespace = 10 AND lt_title = 'Wikidata_Infobox')"\
	" WHERE tl.tl_target_id IS NULL"
	vals = cur.fetchall()
	f = open("/data/project/pibot/commons_infobox_candidates.csv", "w", encoding='utf-8')
	if len(vals) > 0:
		start += step
		[f.write(str(x[1])+'\n') for x in vals]
	else:
		run = False
	f.close()
	ftp = FTP('mikepeel.net',user=ftpuser,passwd=ftppass)
	ftp.cwd('wiki')
	file = open('/data/project/pibot/commons_infobox_candidates.csv','rb')
	ftp.storbinary('STOR commons_infobox_candidates.txt', file)
	file.close()
	ftp.quit()
