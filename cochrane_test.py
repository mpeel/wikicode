import requests
import re

r2 = requests.get('https://pubmed.ncbi.nlm.nih.gov/27093058/', timeout=10.0)
res2 = r2.text
if '<title>WITHDRAWN' in res2:
    # The new one's been withdrawn: we don't want to report this as an update.
    print('Withdrawn')
else:
	print('OK')
print(re.search(r'<h3>Update in</h3><ul><li class="comments"><a href="/pubmed/\d+?"', res2))
pm = re.findall(r'<h3>Update in</h3><ul><li class="comments"><a href="/pubmed/(\d+?)"', res2)[0]
print(pm)
