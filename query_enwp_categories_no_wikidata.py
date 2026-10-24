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

languages = ['en', 'pt', 'de', 'simple','es','fr','it','nl','pl','sv','eo','dag','ml','af','cy','et','ab', 'ace', 'ady', 'ak', 'als', 'alt', 'ami', 'am', 'ang', 'ann', 'anp', 'an', 'arc', 'ar', 'ary', 'arz', 'ast', 'as', 'atj', 'avk', 'av', 'awa', 'ay', 'azb', 'az', 'ban', 'bar', 'bat_smg', 'ba', 'bbc', 'bcl', 'bdr', 'be_x_old', 'be', 'bew', 'bg', 'bh', 'bi', 'bjn', 'blk', 'bm', 'bn', 'bol', 'bo', 'bpy', 'br', 'bs', 'btm', 'bug', 'bxr', 'ca', 'cbk_zam', 'cdo', 'ceb', 'ce', 'cho', 'chr', 'ch', 'chy', 'ckb', 'co', 'crh', 'csb', 'cs', 'cu', 'cv', 'da', 'dga', 'din', 'diq', 'dsb', 'dtp', 'dty', 'dv', 'dz', 'ee', 'el', 'eml', 'eu', 'ext', 'fat', 'fa', 'ff', 'fiu_vro', 'fi', 'fj', 'fon', 'fo', 'frp', 'frr', 'fur', 'fy', 'gag', 'gan', 'ga', 'gcr', 'gd', 'glk', 'gl', 'gn', 'gom', 'gor', 'got', 'gpe', 'guc', 'gur', 'gu', 'guw', 'gv', 'hak', 'ha', 'haw', 'he', 'hif', 'hi', 'ho', 'hr', 'hsb', 'ht', 'hu', 'hy', 'hyw', 'ia', 'iba', 'id', 'ie', 'igl', 'ig', 'ik', 'ilo', 'inh', 'io', 'isv', 'is', 'iu', 'jam', 'ja', 'jbo', 'jv', 'kaa', 'kab', 'kai', 'kaj', 'ka', 'kbd', 'kbp', 'kcg', 'kge', 'kg', 'ki', 'kk', 'km', 'knc', 'kn', 'koi', 'ko', 'krc', 'ksh', 'ks', 'kus', 'ku', 'kv', 'kw', 'ky', 'lad', 'la', 'lb', 'lez', 'lfn', 'lg', 'lij', 'li', 'lld', 'lmo', 'ln', 'lo', 'ltg', 'lt', 'lv', 'mad', 'mag', 'mai', 'map_bms', 'mdf', 'mg', 'mhr', 'min', 'mi', 'mk', 'mni', 'mn', 'mnw', 'mos', 'mo', 'mrj', 'mr', 'ms', 'mt', 'mwl', 'myv', 'my', 'mzn', 'nah', 'nap', 'nds_nl', 'nds', 'ne', 'new', 'ng', 'nia', 'nn', 'nov', 'no', 'nqo', 'nrm', 'nr', 'nso', 'nup', 'nv', 'ny', 'oc', 'olo', 'om', 'or', 'os', 'pag', 'pam', 'pap', 'pa', 'pcd', 'pcm', 'pdc', 'pfl', 'pi', 'pms', 'pnb', 'pnt', 'ppl', 'ps', 'pwn', 'qu', 'rki', 'rm', 'rmy', 'rn', 'roa_rup', 'roa_tara', 'ro', 'rsk', 'rue', 'ru', 'rw', 'sah', 'sat', 'sa', 'scn', 'sco', 'sc', 'sd', 'se', 'sg', 'shi', 'shn', 'sh', 'si', 'skr', 'sk', 'sl', 'smn', 'sm', 'sn', 'so', 'sq', 'srn', 'sr', 'ss', 'stq', 'st', 'su', 'sw', 'syl', 'szl', 'szy', 'ta', 'tay', 'tcy', 'tdd', 'tet', 'te', 'tg', 'th', 'tig', 'ti', 'tk', 'tl', 'tly', 'tn', 'tok', 'to', 'tpi', 'trv', 'tr', 'ts', 'tt', 'tum', 'tw', 'tyv', 'ty', 'udm', 'ug', 'uk', 'ur', 'uz', 'vec', 'vep', 've', 'vi', 'vls', 'vo', 'war', 'wa', 'wo', 'wuu', 'xal', 'xh', 'xmf', 'yi', 'yo', 'za', 'zea', 'zgh', 'zh_classical', 'zh_min_nan', 'zh_yue', 'zh', 'zu']

for lang in languages:
	try:
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
	except:
		continue
	