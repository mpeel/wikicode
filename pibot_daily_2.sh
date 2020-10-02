#!/bin/bash
source /home/pi/.profile
export PYTHONPATH=/home/pi/Documents/core:$PYTHONPATH
cd /home/pi/Documents/wikicode/

/usr/bin/python3 wir_newpages_duplicity.py
/usr/bin/python3 wir_newpages_category.py
/usr/bin/python3 wir_newpages_special.py
