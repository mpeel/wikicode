#!/bin/bash
source /home/pi/.profile
source /home/pi/.bashrc
export PYTHONPATH=/home/pi/Documents/git/core:$PYTHONPATH
cd /home/pi/Documents/git/wikicode/

/usr/bin/python3 enwp_commonscat_fix.py
/usr/bin/python3 simplewp_commonscat_fix.py
/usr/bin/python3 wikidata_import_infobox_qid.py
/usr/bin/python3 commons_wikidata_infobox_tidy.py
/usr/bin/python3 enwp_wikidata_import_shortdesc.py
/usr/bin/python3 commonscat_check.py
/usr/bin/python3 wikidata_en_biography_names.py
/usr/bin/python3 wikidata_brackets_in_biography_names.py