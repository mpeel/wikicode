#!/bin/bash
source /home/pi/.profile
source /home/pi/.bashrc
export PYTHONPATH=/home/pi/Documents/git/core:$PYTHONPATH
cd /home/pi/Documents/git/wikicode/

/usr/bin/python3 permissions.py
/usr/bin/python3 guardian_obit.py
/usr/bin/python3 nyt_obit.py
/usr/bin/python3 wikidata_bad_p373.py
/usr/bin/python3 commons_defaultsort_conflicts.py
/usr/bin/python3 enwp_commonscat_import.py
/usr/bin/python3 commonscat_p910_tidy.py
/usr/bin/python3 commonscat_move_from_P910.py
/usr/bin/python3 commonscat_move_from_P1754.py
/usr/bin/python3 doublecheck_move.py
/usr/bin/python3 commonscat_check.py
/usr/bin/python3 wikidata_p301_inverse.py
/usr/bin/python3 wikidata_p910_inverse.py
/usr/bin/python3 wikidata_p1753_inverse.py
/usr/bin/python3 wikidata_p1754_inverse.py
