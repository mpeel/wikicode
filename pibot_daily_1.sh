#!/bin/bash
source /home/pi/.profile
export PYTHONPATH=/home/pi/Documents/core:$PYTHONPATH
cd /home/pi/Documents/wikicode/

/usr/bin/python permissions.py
/usr/bin/python guardian_obit.py
/usr/bin/python nyt_obit.py
/usr/bin/python wikidata_bad_p373.py
/usr/bin/python commons_defaultsort_conflicts.py
/usr/bin/python commonscat_move_from_P910.py
/usr/bin/python3 commonscat_move_from_P1754.py
/usr/bin/python doublecheck_move.py
/usr/bin/python commonscat_check.py
/usr/bin/python commonscat_p910_tidy.py
/usr/bin/python3 wikidata_p301_inverse.py
/usr/bin/python3 wikidata_p910_inverse.py
/usr/bin/python3 wikidata_p1753_inverse.py
/usr/bin/python3 wikidata_p1754_inverse.py
