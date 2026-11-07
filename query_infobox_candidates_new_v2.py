#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Find Commons categories with Wikidata items which do not
# currently use Wikidata Infobox.
#
# Updated for the Commons links database split (November 2026).
# Based on Bugreporter's suggestion in Phabricator T443973.

import pymysql
import configparser
import resource
from ftplib import FTP
from ftplogin import *

# --------------------------------------------------
# Configuration
# --------------------------------------------------

CORE_HOST = 'commonswiki.analytics.db.svc.wikimedia.cloud'
LINKS_HOST = 'links.commonswiki.analytics.db.svc.wikimedia.cloud'

DATABASE = 'commonswiki_p'
PORT = 3306

OUTPUT_FILE = '/data/project/pibot/commons_infobox_candidates_new.csv'
FTP_FILENAME = 'commons_infobox_candidates_new.txt'

# --------------------------------------------------
# Database credentials
# --------------------------------------------------

config = configparser.ConfigParser()
config.read('replica.my.cnf')

user = config['client']['user']
password = config['client']['password']

# --------------------------------------------------
# Database connections
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
# Helper function for page titles
# --------------------------------------------------

def decode_title(title):
    if isinstance(title, bytes):
        return title.decode('utf-8')
    return title

# --------------------------------------------------
# Query 2: Categories already using Wikidata Infobox
# --------------------------------------------------

infobox_pages = set()

try:

    print('Querying categories using Wikidata Infobox...')

    with links_conn.cursor(
        cursor=pymysql.cursors.SSCursor
    ) as cur:

        cur.execute("""
            SELECT DISTINCT
                tl.tl_from
            FROM templatelinks AS tl
            JOIN linktarget AS lt
                ON lt.lt_id = tl.tl_target_id
            WHERE tl.tl_from_namespace = 14
                AND lt.lt_namespace = 10
                AND lt.lt_title = 'Wikidata_Infobox'
        """)

        for row in cur:
            infobox_pages.add(row[0])

            if len(infobox_pages) % 1000000 == 0:
                memory = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss

                print(
                    'Found {:,} categories; peak memory: {:.2f} GB'.format(
                        len(infobox_pages),
                        memory / (1024 * 1024)
                    ),
                    flush=True
                )
    print(
        'Total categories using Wikidata Infobox: {:,}'
        .format(len(infobox_pages))
    )

    # --------------------------------------------------
    # Query 3: Subcategories of Category redirects
    # --------------------------------------------------

    redirect_pages = set()

    print('\nQuerying subcategories of Category redirects...')

    with links_conn.cursor(
        cursor=pymysql.cursors.SSCursor
    ) as cur:

        cur.execute("""
            SELECT DISTINCT
                cl.cl_from
            FROM categorylinks AS cl
            JOIN linktarget AS lt
                ON lt.lt_id = cl.cl_target_id
            WHERE cl.cl_type = 'subcat'
                AND lt.lt_namespace = 14
                AND lt.lt_title = 'Category_redirects'
        """)

        for row in cur:
            redirect_pages.add(row[0])

            if len(redirect_pages) % 100000 == 0:
                print(
                    'Found {:,} subcategories of Category redirects'
                    .format(len(redirect_pages))
                )

    print(
        'Total subcategories of Category redirects: {:,}'
        .format(len(redirect_pages))
    )

    # --------------------------------------------------
    # Combine exclusions
    # --------------------------------------------------

    exclusions = infobox_pages
    exclusions.update(redirect_pages)

    print(
        '\nTotal excluded page IDs: {:,}'.format(len(exclusions))
    )

    # Release the individual sets now that they are combined.
    del infobox_pages
    del redirect_pages

    # --------------------------------------------------
    # Query 1: Categories with Wikidata items
    # --------------------------------------------------

    print('\nQuerying Commons categories with Wikidata items...')

    total_candidates = 0
    total_written = 0

    with core_conn.cursor(
        cursor=pymysql.cursors.SSCursor
    ) as cur, open(
        OUTPUT_FILE, 'w', encoding='utf-8'
    ) as output:

        cur.execute("""
            SELECT DISTINCT
                p.page_id,
                p.page_title
            FROM page AS p
            JOIN page_props AS pp
                ON pp.pp_page = p.page_id
            WHERE pp.pp_propname = 'wikibase_item'
                AND p.page_namespace = 14
                AND p.page_is_redirect = 0
        """)

        for row in cur:

            page_id = row[0]
            page_title = row[1]

            total_candidates += 1

            if page_id not in exclusions:

                page_title = decode_title(page_title)

                output.write(page_title + '\n')
                total_written += 1

            if total_candidates % 1000000 == 0:
                print(
                    'Processed {:,} categories; '
                    'written {:,} candidates'
                    .format(total_candidates, total_written)
                )

    print('\nQuery complete.')
    print(
        'Total categories examined: {:,}'.format(total_candidates)
    )
    print(
        'Total exclusions: {:,}'.format(len(exclusions))
    )
    print(
        'Candidates written: {:,}'.format(total_written)
    )

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
