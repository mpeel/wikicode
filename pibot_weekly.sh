#!/bin/bash
source /home/pi/.profile
source /home/pi/.bashrc
export PYTHONPATH=/home/pi/Documents/git/core:$PYTHONPATH
cd /home/pi/Documents/git/wikicode/

/usr/bin/python3 enwp_commonscat_fix.py
/usr/bin/python3 simplewp_commonscat_fix.py
/usr/bin/python3 enwp_wikidata_import_shortdesc.py
/usr/bin/python3 commonscat_check.py
/usr/bin/python3 wikidata_en_biography_names.py
/usr/bin/python3 wikidata_pt_biography_names.py
/usr/bin/python3 wikidata_brackets_in_biography_names.py
/usr/bin/python3 wikidata_new_from_wikipedia_query_article_nocreate.py
/usr/bin/python3 wikidata_new_from_wikipedia_query_category_nocreate.py
