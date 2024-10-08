import os
import datetime
from ftplogin import *

now = datetime.datetime.today()
today = now.strftime('%Y-%m-%d')
nextmonth = ((now.replace(day=1) + datetime.timedelta(days=32)).replace(day=1)).strftime('%Y-%m-%d')
print(today)
print(nextmonth)

os.system("python3 wikidata_enwiki_mismatch.py > wikidata_enwiki_mismatch_"+today+"_log.csv")

os.system(' curl -X POST "https://mismatch-finder.toolforge.org/api/imports" \
-H "Accept: application/json" \
-H "Authorization: Bearer '+mismatch_bearer_token+'" \
-F "mismatch_file=@wikidata_enwiki_mismatch_'+today+'.csv" \
-F "description=Mismatches between authority control links identified through templates comparing English Wikipedia and Wikidata" \
-F "external_source=English Wikipedia" \
-F "external_source_url=https://en.wikipedia.org/wiki/Category:Wikipedia_categories_tracking_Wikidata_differences" \
-F "expires='+nextmonth+'"')
