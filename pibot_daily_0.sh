#!/bin/bash
source /home/pi/.profile
source /home/pi/.bashrc
export PYTHONPATH=/home/pi/Documents/git/core:$PYTHONPATH
cd /home/pi/Documents/git/wikicode/

/usr/bin/python3 commons_wikidata_infobox.py
/usr/bin/python3 wikidata_new_from_wikipedia_query_article.py
/usr/bin/python3 wikidata_new_from_wikipedia_query_category.py
/usr/bin/python3 enwp_coords.py
#/usr/bin/python3 commons_category_coords.py