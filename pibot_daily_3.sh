#!/bin/bash
source /home/pi/.profile
source /home/pi/.bashrc
export PYTHONPATH=/home/pi/Documents/git/core:$PYTHONPATH
cd /home/pi/Documents/git/wikicode/

/usr/bin/python3 commons_qi_by_user.py
/usr/bin/python3 commons_fi_by_user.py
/usr/bin/python3 commons_vi_by_user.py
/usr/bin/python3 enwp_commonscat_import.py
/usr/bin/python3 commonscat_copy_from_P373.py
/usr/bin/python3 wikidata_import_labels_from_commons.py
