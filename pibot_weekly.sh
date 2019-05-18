#!/bin/bash
source /home/pi/.profile
cd /home/pi/Documents/wikicode/

/usr/bin/python enwp_commonscat_fix.py
/usr/bin/python commons_wikidata_infobox_tidy.py
