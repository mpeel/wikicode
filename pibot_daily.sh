#!/bin/bash
source /home/pi/.profile
cd /home/pi/Documents/wikicode/
/usr/bin/python permissions.py
/usr/bin/python guardian_obit.py
/usr/bin/python nyt_obit.py
/usr/bin/python commons_defaultsort_conflicts.py
/usr/bin/python commonscat_copy_from_P373.py
/usr/bin/python commonscat_move_from_P910.py
/usr/bin/python commonscat_check.py
