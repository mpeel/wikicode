import os
import datetime
from ftplogin import *

os.system(' curl -X POST "https://mismatch-finder.toolforge.org/api/imports" \
-H "Accept: application/json" \
-H "Authorization: Bearer '+mismatch_bearer_token+'" \
-F "mismatch_file=@wikidata_enwiki_mismatch_'+today+'.csv" \
-F "description=Mismatches between authority control links identified through templates comparing English Wikipedia and Wikidata" \
-F "external_source=English Wikipedia" \
-F "external_source_url=https://en.wikipedia.org/wiki/Category:Wikipedia_categories_tracking_Wikidata_differences" \
-F "expires='+nextmonth+'"')
