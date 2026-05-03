#!/bin/bash
source /home/pi/.profile
source /home/pi/.bashrc
cd /home/pi/Documents/git/wikicode/pibot/

python3 enwp_commonscat_import.py
python3 enwp_commonscat_fix.py
python3 simplewp_commonscat_fix.py
python3 enwp_wikidata_import_shortdesc.py
python3 commonscat_check.py
python3 commonscat_copy_from_P373.py

# Come back to these
# # Disabled due to mul
# #/usr/bin/python3 wikidata_en_biography_names.py
# #/usr/bin/python3 wikidata_pt_biography_names.py
# /usr/bin/python3 wikidata_brackets_in_biography_names.py
# /usr/bin/python3 wikidata_new_from_wikipedia_query_article_nocreate.py
# /usr/bin/python3 wikidata_new_from_wikipedia_query_category_nocreate.py
