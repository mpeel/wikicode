#!/bin/bash
source /home/pi/.profile
source /home/pi/.bashrc
export PYTHONPATH=/home/pi/Documents/git/core:$PYTHONPATH
cd /home/pi/Documents/git/wikicode/

/usr/bin/python3 wir_newpages_duplicity.py
/usr/bin/python3 wir_newpages_category.py
/usr/bin/python3 wir_newpages_special.py
/usr/bin/python3 wikidata_new_from_wikipedia.py