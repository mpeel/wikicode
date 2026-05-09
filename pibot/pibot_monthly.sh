#!/bin/bash
source /home/pi/.profile
source /home/pi/.bashrc
cd /home/pi/Documents/git/wikicode/pibot/

/home/pi/venv/bin/python3 cochrane.py
/home/pi/venv/bin/python3 cochrane_fr.py
/home/pi/venv/bin/python3 wikidata_enwiki_mismatch_run.py
# Run this twice to catch cases where the IMO category was moved
/home/pi/venv/bin/python3 wikidata_newshipname.py
/home/pi/venv/bin/python3 wikidata_newshipname.py
/home/pi/venv/bin/python3 wikidata_viewof.py
/home/pi/venv/bin/python3 commonscat_redirects.py
/home/pi/venv/bin/python3 commons_date_find.py
