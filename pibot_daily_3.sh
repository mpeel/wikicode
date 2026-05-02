#!/bin/bash
source /home/pi/.profile
source /home/pi/.bashrc
cd /home/pi/Documents/git/wikicode/

python3 commons_qi_by_user.py
python3 commons_fi_by_user.py
python3 commons_vi_by_user.py
python3 qic_count_nom_vote.py
# Come back to these...
#/usr/bin/python3 enwp_commonscat_import.py
#/usr/bin/python3 commonscat_copy_from_P373.py

# Disabled due to mul
#/usr/bin/python3 wikidata_import_labels_from_commons.py
