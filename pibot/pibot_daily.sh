#!/bin/bash
source /home/pi/.profile
source /home/pi/.bashrc
cd /home/pi/Documents/git/wikicode/pibot/

/home/pi/venv/bin/python3 permissions.py
/home/pi/venv/bin/python3 guardian_obit.py
/home/pi/venv/bin/python3 nyt_obit.py
/home/pi/venv/bin/python3 commons_qi_by_user.py
/home/pi/venv/bin/python3 commons_fi_by_user.py
/home/pi/venv/bin/python3 commons_vi_by_user.py
/home/pi/venv/bin/python3 qic_count_nom_vote.py



# Not working
#python3 wir_newpages_duplicity.py
#python3 wir_newpages_category.py
#python3 wir_newpages_special.py

# To check
# /usr/bin/python3 wikidata_import_infobox_qid.py
# /usr/bin/python3 commons_wikidata_infobox_tidy.py
# /usr/bin/python3 commons_wikidata_infobox_new.py
# /usr/bin/python3 commons_wikidata_infobox.py
# /usr/bin/python3 wikidata_bot_requests.py
# /usr/bin/python3 wikidata_new_from_wikipedia_query_article.py
# /usr/bin/python3 wikidata_new_from_wikipedia_query_category.py
# /usr/bin/python3 wikidata_new_from_wikiquote_query.py
# /usr/bin/python3 commons_category_coords.py
# /usr/bin/python3 commons_category_coords_from_cat.py

# /usr/bin/python3 wikidata_bad_p373.py
# /usr/bin/python3 commons_defaultsort_conflicts.py
# /usr/bin/python3 enwp_commonscat_import.py
# /usr/bin/python3 commonscat_p910_tidy.py
# /usr/bin/python3 commonscat_move_from_P910.py
# /usr/bin/python3 commonscat_move_from_P1754.py
# /usr/bin/python3 doublecheck_move.py
# /usr/bin/python3 wikidata_p301_inverse.py
# /usr/bin/python3 wikidata_p910_inverse.py
# /usr/bin/python3 wikidata_p1753_inverse.py
# /usr/bin/python3 wikidata_p1754_inverse.py
# /usr/bin/python3 astrocoords_fix_globe.py
# /usr/bin/python3 astrocoords_copy_to_P376.py

# Disabled due to mul
#/usr/bin/python3 wikidata_import_labels_from_commons.py
