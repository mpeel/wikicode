import requests
import re

def get_update_pmid(text):
    checkstring = r'<divclass="linked-articles"id="linked-update">'
    if re.search(checkstring, rawtext):
        text = text.split(checkstring)[1]
        pm = re.findall(r'<aclass="docsum-title"href="/(\d+?)/"ref="article_id=', rawtext)[0]
        return pm
    else:
        return False


r = requests.get('https://pubmed.ncbi.nlm.nih.gov/27687114/', timeout=10.0)
res = r.text
# if 'WITHDRAWN' in res and re.search(r'<h3>Update in</h3><ul><li class="comments"><a href="/pubmed/\d+?"', res):
rawtext = re.sub(r'\s+', '', res)
# print(rawtext)
# print(rawtext)
print(get_update_pmid(rawtext))

# if '<title>WITHDRAWN' in res2:
#     # The new one's been withdrawn: we don't want to report this as an update.
#     print('Withdrawn')
# else:
# 	print('OK')
# print(re.search(r'<h3>Update in</h3><ul><li class="comments"><a href="/pubmed/\d+?"', res2))
# pm = re.findall(r'<h3>Update in</h3><ul><li class="comments"><a href="/pubmed/(\d+?)"', res2)[0]
# print(pm)
