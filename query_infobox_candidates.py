
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
	cur.execute("SELECT"\
	" page_title,"
	" (COUNT( eu_entity_id )) as ct"
	" FROM"
	"  page,"
	"  page_props,"
	"  wbc_entity_usage"
	" WHERE"
	"  pp_propname = \"unexpectedUnconnectedPage\""
	"  AND page_id = pp_page"
	"  AND page_namespace = 14"
	"      AND NOT EXISTS"
	"        ("
	"        SELECT  null "
	"        FROM    templatelinks"
	"        WHERE   page_id = tl_from"
	"        )  "
	"  AND page_id = eu_page_id"
	"  AND eu_aspect = \"S\""
	"  /* AND page_title = \"Naupliastraße_(München)\" */"
	" GROUP BY"
	"  page_title"
	" HAVING"
	"  ct = 1")
	vals = cur.fetchall()
	f = open("/data/project/pibot/commons_infobox_candidates.csv", "w", encoding='utf-8')
	if len(vals) > 0:
		start += step
		[f.write(str(x[0])+'\n') for x in vals]
	else:
		run = False
	f.close()
	ftp = FTP('mikepeel.net',user=ftpuser,passwd=ftppass)
	ftp.cwd('wiki')
	file = open('/data/project/pibot/commons_infobox_candidates.csv','rb')
	ftp.storbinary('STOR commons_infobox_candidates.txt', file)
	file.close()
	ftp.quit()
