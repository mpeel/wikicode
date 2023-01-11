import pywikibot
site = pywikibot.Site("commons", "commons")

userlink = pywikibot.User(site,'Bot for Freedom')
last_timestamp = ''
for file in userlink.uploadedImages(total=10000000):
    print(file[0])
