#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# DUAL LICENSED: You are free to choose either or both of below licenses:
#
# 1.
#
# Published by zhuyifei1999 (https://wikitech.wikimedia.org/wiki/User:Zhuyifei1999)
# under the terms of Creative Commons Attribution-ShareAlike 3.0 Unported (CC BY-SA 3.0)
# https://creativecommons.org/licenses/by-sa/3.0/
#
# 2.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General License for more details.
#
# You should have received a copy of the GNU General License
# along with self program.  If not, see <http://www.gnu.org/licenses/>
#
import sys
sys.path.append("/home/pi/Documents/media-dubiety/")

import hashlib
import random
import re
import sys
import threading
import time
import traceback

import pywikibot
from pywikibot.diff import PatchManager

# from redis import Redis
# from redisconfig import KEYSIGN

# from media-dubiety
from threads import SSEClient, ThreadPool

SITE = pywikibot.Site(user='Pi bot')
SITE.login()

# REDIS = Redis(host='tools-redis')

threads = []

state = type(str('State'), (), {
    'useroptin': None,
    'useroptout': None,
    'excluderegex': None,
})()


def chance(c):
    return random.random() < c


def get_tags(event):
    req = SITE._simple_request(
        action='query',
        prop='revisions',
        titles=event['title'],
        rvprop='tags',
        rvstartid=event['revision']['new'],
        rvendid=event['revision']['new'],
        rvlimit=1
    )
    try:
        res = req.submit()
    except Exception as e:
        pywikibot.exception(e)
        return []
    else:
        try:
            p = res['query']['pages']
            r = p[next(iter(p.keys()))]['revisions']
            return r[0]['tags']
        except KeyError:
            return []


def locknotify(user, lock=True):
    if user.isAnonymous():
        return False
    reset = int(time.time()) + 86400
    key = KEYSIGN + ':' + 'lock' + ':'
    key += hashlib.md5(user.username.encode('utf-8')).hexdigest()
    # p = REDIS.pipeline()
    # p.exists(key)
    # if lock:
    #     p.set(key, '1')
    #     p.expireat(key, reset + 10)
    # else:
    #     p.delete(key)
    # return p.execute()[0]
    return 0


def checknotify(user):
    if user.isAnonymous():
        return False
    reset = int(time.time()) + 86400
    key = KEYSIGN + ':' + 'counter' + ':'
    key += hashlib.md5(user.username.encode('utf-8')).hexdigest()
    # p = REDIS.pipeline()
    # p.incr(key)
    # p.expireat(key, reset + 10)
    # return p.execute()[0] >= 3
    return 0

def get_signature(event, tosignstr, user):
    p = ''
    if tosignstr[-1] != ' ':
        p = ' '
    timestamp = pywikibot.Timestamp.utcfromtimestamp(
        event['timestamp']).strftime('%H:%M, %-d %B %Y')
    return p + '{{%s|%s|%s}}' % (
        'unsignedIP2' if user.isAnonymous() else 'unsigned2',
        timestamp,
        user.username
    )


def is_signed(user, tosignstr):
    for wikilink in pywikibot.link_regex.finditer(
            pywikibot.textlib.removeDisabledParts(tosignstr)):
        if not wikilink.group('title').strip():
            continue
        try:
            link = pywikibot.Link(wikilink.group('title'),
                                  source=SITE)
            link.parse()
        except pywikibot.Error:
            continue
        if user.isAnonymous():
            if link.namespace != -1:
                continue
            if link.title != 'Contributions/' + user.username:
                continue
        else:
            if link.namespace not in [2, 3]:
                continue
            if link.title != user.username:
                continue
        return True

    return False


def is_comment(line):
    # remove non-functional parts and categories
    tempstr = re.sub(r'\[\[[Cc]ategory:[^\]]+\]\]', '',
                     pywikibot.textlib.removeDisabledParts(line)).strip()
    # not empty
    if not tempstr:
        return False
    # not heading
    if tempstr.startswith('=') and tempstr.endswith('='):
        return False
    # not table/template
    if (
        tempstr.startswith('|') or
        tempstr.startswith('{|') or
        tempstr.endswith('|') or
        tempstr.count('{{') > tempstr.count('}}')
    ):
        return False
    # not horzontal line
    if tempstr.startswith('----'):
        return False
    # not magic words
    if re.match(r'^__[A-Z]+__$', tempstr):
        return False

    return True


def is_optout(user):
    # 0.25 chance of updating list
    if (
        state.useroptin is None or
        state.useroptout is None or
        chance(0.25)
    ):
        state.useroptin = list(
            pywikibot.Page(SITE, 'Template:YesAutosign')
            .getReferences(onlyTemplateInclusion=True))
        state.useroptout = list(
            pywikibot.Page(SITE, 'Template:NoAutosign')
            .getReferences(onlyTemplateInclusion=True))

    # Check for opt-in {{YesAutosign}} -> False
    if user in state.useroptin:
        return False
    # Check for opt-out {{NoAutosign}} -> True
    if user in state.useroptout:
        return True
    # Check for 800 user edits -> False
    # -> True
    return user.editCount(force=chance(0.25)) > 800


def is_discussion(page):
    # TODO: sandbox
    # TODO: opt-in

    # __NEWSECTIONLINK__ -> True
    if 'newsectionlink' in page.properties():
        return True

    if page.title().startswith('Commons:Deletion requests/'):
        if re.match(r'Commons:Deletion requests/[0-9/]*$', page.title()):
            return False
        if '{{Commons:Deletion requests/' in page.text:
            return False
        return True

    return False


def match_exclude_regex(line):
    # 0.05 chance of updating list
    if state.excluderegex is None or chance(0.05):
        # We do not directly assign to state.excluderegex right
        # now to avoid issues with multi-threading
        lst = []

        repage = pywikibot.Page(SITE, 'User:SignBot/exclude_regex')
        for line in repage.get(force=True).split('\n'):
            line = line.strip()
            if line and not line.startswith('#'):
                lst.append(re.compile(line, re.I))

        state.excluderegex = lst

    line = line.replace('_', ' ')
    for regex in state.excluderegex:
        reobj = regex.search(line)
        if reobj is not None:
            return reobj.group(0)
    return None


def userlink(user):
    if user.isAnonymous():
        return '[[Special:Contributions/%s|%s]]' % (
            user.username, user.username)
    else:
        return '[[User:%s|%s]]' % (user.username, user.username)


def handler(event):
    if (
        event['wiki'] != SITE.dbName() or
        event['bot'] or
        not (event['namespace'] == 4 or event['namespace'] % 2 == 1) or
        event['type'] not in {'edit', 'new'} or
        '!nosign!' in event['comment']
    ):
        return

    page = pywikibot.Page(SITE, event['title'], ns=event['namespace'])

    def output(info):
        pywikibot.output('%s: %s' % (page, info))

    output('Handling')

    if page.isRedirectPage():
        output('Redirect')
        return
    if page.namespace() == 4:
        # Project pages needs attention (__NEWSECTIONLINK__)
        if not is_discussion(page):
            output('Not a discussion')
            return

    if {'mw-undo', 'mw-rollback'}.intersection(get_tags(event)):
        output('undo / rollback')
        return

    user = pywikibot.User(SITE, event['user'])
    if is_optout(user):
        output('%s opted-out' % user)
        return

    # diff-reading.
    if event['type'] == 'new':
        old_text = ''
    else:
        old_text = page.getOldVersion(event['revision']['old'])

    new_text = page.getOldVersion(event['revision']['new'])

    if '{{speedy' in new_text.lower():
        output('{{speedy -- ignored')
        return

    diff = PatchManager(old_text.split('\n') if old_text else [],
                        new_text.split('\n'),
                        by_letter=True)
    diff.print_hunks()

    tosignstr = False
    tosignnum = False

    for block in diff.blocks:
        if block[0] < 0:
            continue
        hunk = diff.hunks[block[0]]
        group = hunk.group

        for tag, i1, i2, j1, j2 in group:
            if tag == 'insert':
                for j in range(j1, j2):
                    line = hunk.b[j]
                    if (
                        page == user.getUserTalkPage() or
                        page.title().startswith(
                            user.getUserTalkPage().title() + '/')
                    ):
                        if '{{' in line.lower():
                            output('User adding templates to their '
                                   'own talk page -- ignored')
                            return

                    excluderegextest = match_exclude_regex(line)
                    if excluderegextest is not None:
                        output('%s -- ignored' % excluderegextest)
                        return

                    if is_comment(line):
                        tosignnum = j
                        tosignstr = line
                        if is_signed(user, tosignstr):
                            output('Signed')
                            return

    if tosignstr is False:
        output('No inserts')
        return
    if is_signed(user, tosignstr):
        output('Signed')
        return

    # Frequent page list not implemented
    # if not isFreqpage(page):

    pending_notify = locknotify(user, lock=True)

    def do_process():
        output('Waiting')
        if page.title() != 'User talk:SignBot/sandbox':
            time.sleep(60 * 10)

        currenttext = page.get(force=True)
        savetext = currenttext.split('\n')
        sig = get_signature(event, tosignstr, user)
        if savetext[tosignnum] == tosignstr:
            savetext[tosignnum] += sig
        elif savetext.count(tosignstr) == 1:
            savetext[savetext.index(tosignstr)] += \
                get_signature(event, tosignstr, user)
        else:
            output('Line no longer found, probably signed')
            return

        summary = "Signing comment by %s - '%s'" % (
            userlink(user), event['comment'])

        page.text = '\n'.join(savetext)
        if page.text != currenttext:
            pywikibot.output('\n\n>>> \03{lightpurple}%s\03{default} <<<'
                             % page.title(asLink=True))
            pywikibot.showDiff(currenttext, page.text)

            page.save(summary)

        # {{subst:Please sign}} -- ignore {{bots}}
        if not pending_notify and checknotify(user):
            output('Notifying %s' % user)
            talk = user.getUserTalkPage()
            if talk.isRedirectPage():
                talk = talk.getRedirectTarget()

            if talk.text:
                talk.text += '\n\n'

            talk.text += '{{subst:Please sign}} --~~~~'

            talk.save('Added {{subst:[[Template:Please sign|Please sign]]}} note.',
                      minor=False, force=True)

        locknotify(user, lock=False)

    threading.Thread(target=do_process).start()


def main():
    pywikibot.handleArgs()

    pool = ThreadPool(16)
    sse = SSEClient(lambda event: pool.process(lambda: handler(event)))
    threads[:] = pool, sse

    [thread.start() for thread in threads]

    try:
        while all(thread.isAlive() for thread in threads):
            time.sleep(1)
    except BaseException:
        traceback.print_exc()
        sys.exit(1)
    finally:
        [thread.stop() for thread in threads]

        for thread in threading.enumerate():
            if thread.daemon:
                pywikibot.output('Abandoning daemon thread %s' % thread.name)

        [thread.join() for thread in threads]


if __name__ == '__main__':
    try:
        main()
    finally:
        pywikibot.stopme()