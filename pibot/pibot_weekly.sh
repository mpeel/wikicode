#!/bin/bash
source /home/pi/.profile
source /home/pi/.bashrc
cd /home/pi/Documents/git/wikicode/pibot/

/home/pi/venv/bin/python3 enwp_commonscat_import.py
/home/pi/venv/bin/python3 enwp_commonscat_fix.py
/home/pi/venv/bin/python3 simplewp_commonscat_fix.py
/home/pi/venv/bin/python3 enwp_wikidata_import_shortdesc.py
/home/pi/venv/bin/python3 commonscat_check.py
/home/pi/venv/bin/python3 commonscat_copy_from_P373.py
/home/pi/venv/bin/python3 enwp_coords.py
/home/pi/venv/bin/python3 wikidata_brackets_in_biography_names.py
/home/pi/venv/bin/python3 wikidata_new_from_wikipedia_query_article_nocreate.py
/home/pi/venv/bin/python3 wikidata_new_from_wikipedia_query_category_nocreate.py

# Disabled due to mul
#/usr/bin/python3 wikidata_en_biography_names.py
#/usr/bin/python3 wikidata_pt_biography_names.py
