
#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Find Commons categories with Wikidata items which do not yet use
Wikidata Infobox, excluding category redirects and subcategories
of Category redirects.

Updated for the September 2026 Commons links database split.
"""

import os
import configparser
import pymysql
from ftplib import FTP
from ftplogin import *

# --------------------------------------------------
# Configuration
# --------------------------------------------------

CORE_HOST = 'commonswiki.analytics.db.svc.wikimedia.cloud'
LINKS_HOST = 'links.commonswiki.analytics.db.svc.wikimedia.cloud'

DATABASE = 'commonswiki_p'
PORT = 3306

BATCH_SIZE = 1000

OUTPUT_FILE = '/data/project/pibot/commons_infobox_candidates_new.csv'
FTP_FILENAME = 'commons_infobox_candidates_new.txt'

# --------------------------------------------------
# Read replica credentials
# --------------------------------------------------

config = configparser.ConfigParser()
config.read('replica.my.cnf')

user = config['client']['user']
password = config['client']['password']

# --------------------------------------------------
# Connect to both databases
# --------------------------------------------------

core_conn = pymysql.connect(
    host=CORE_HOST,
    user=user,
    password=password,
    database=DATABASE,
    port=PORT,
    charset='utf8mb4'
)

links_conn = pymysql.connect(
    host=LINKS_HOST,
    user=user,
    password=password,
    database=DATABASE,
    port=PORT,
    charset='utf8mb4'
)

# --------------------------------------------------
# SQL queries
# --------------------------------------------------

# Find Commons categories with Wikidata items.
# These tables are on the core database.

candidate_query = """
SELECT DISTINCT
    p.page_id,
    p.page_title
FROM page AS p
JOIN page_props AS pp
    ON pp.pp_page = p.page_id
WHERE pp.pp_propname = 'wikibase_item'
    AND p.page_namespace = 14
    AND p.page_is_redirect = 0
"""

# Find candidates which already use Wikidata Infobox.
# templatelinks and linktarget are on the links database.

infobox_query = """
SELECT DISTINCT
    tl.tl_from
FROM templatelinks AS tl
JOIN linktarget AS lt
    ON lt.lt_id = tl.tl_target_id
WHERE tl.tl_from IN ({})
    AND tl.tl_from_namespace = 14
    AND lt.lt_namespace = 10
    AND lt.lt_title = %s
"""

# Find candidates which are subcategories of Category redirects.
# categorylinks and linktarget are on the links database.

redirect_query = """
SELECT DISTINCT
    cl.cl_from
FROM categorylinks AS cl
JOIN linktarget AS lt
    ON lt.lt_id = cl.cl_target_id
WHERE cl.cl_from IN ({})
    AND cl.cl_type = 'subcat'
    AND lt.lt_namespace = 15
    AND lt.lt_title = %s
"""

# --------------------------------------------------
# Process candidates in batches
# --------------------------------------------------

total_candidates = 0
total_infobox = 0
total_redirects = 0
total_written = 0

os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

try:

    with core_conn.cursor(
        cursor=pymysql.cursors.SSCursor
    ) as core_cur, \
         links_conn.cursor() as links_cur, \
         open(OUTPUT_FILE, 'w', encoding='utf-8') as output:

        print('Starting Commons category query...')

        core_cur.execute(candidate_query)

        while True:

            # Fetch the next batch from the core database.
            candidates = core_cur.fetchmany(BATCH_SIZE)

            if not candidates:
                break

            total_candidates += len(candidates)

            page_ids = [row[0] for row in candidates]

            # Generate placeholders for the SQL IN clauses.
            placeholders = ','.join(['%s'] * len(page_ids))

            # ------------------------------------------
            # Check for existing Wikidata Infobox usage
            # ------------------------------------------

            links_cur.execute(
                infobox_query.format(placeholders),
                page_ids + ['Wikidata_Infobox']
            )

            infobox_pages = {
                row[0] for row in links_cur.fetchall()
            }

            total_infobox += len(infobox_pages)

            # ------------------------------------------
            # Check for Category redirects subcategories
            # ------------------------------------------

            links_cur.execute(
                redirect_query.format(placeholders),
                page_ids + ['Category_redirects']
            )

            redirect_pages = {
                row[0] for row in links_cur.fetchall()
            }

            total_redirects += len(redirect_pages)

            # ------------------------------------------
            # Write remaining candidates
            # ------------------------------------------

            for page_id, page_title in candidates:

                if page_id in infobox_pages:
                    continue

                if page_id in redirect_pages:
                    continue

                if isinstance(page_title, bytes):
                    page_title = page_title.decode('utf-8')

                output.write(page_title + '\n')
                total_written += 1

            print(
                'Processed: {:,} | Candidates: {:,} | '
                'With infobox: {:,} | Redirect subcategories: {:,} | '
                'Written: {:,}'.format(
                    total_candidates,
                    total_candidates,
                    total_infobox,
                    total_redirects,
                    total_written
                )
            )

    print('\nQuery complete.')
    print('Total categories examined: {:,}'.format(total_candidates))
    print('Already using Wikidata Infobox: {:,}'.format(total_infobox))
    print('Subcategories of Category redirects: {:,}'.format(total_redirects))
    print('Candidates written: {:,}'.format(total_written))

finally:

    core_conn.close()
    links_conn.close()

# --------------------------------------------------
# Upload results to FTP
# --------------------------------------------------

print('\nUploading results to FTP...')

ftp = FTP('mikepeel.net', user=ftpuser, passwd=ftppass)

try:

    ftp.cwd('wiki')

    with open(OUTPUT_FILE, 'rb') as file:
        ftp.storbinary(
            'STOR ' + FTP_FILENAME,
            file
        )

finally:

    ftp.quit()

print('FTP upload complete.')
