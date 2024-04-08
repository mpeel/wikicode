import pywikibot
import re
import datetime

commons = pywikibot.Site('commons', 'commons')

pagenames = ['Commons:Quality images candidates/candidate list']
reportpagename = 'Commons:Quality images candidates/statistics'

for i in range(0,7):
	pagenames.append((datetime.datetime.utcnow()-datetime.timedelta(days=i)).strftime("Commons:Quality images candidates/Archives %B %d %Y"))

userRE = re.compile("\[\[[Uu]ser:([^\|\]]+)[^\]]*\]\]")
nominators = {}
reviewers = {}
for pagename in pagenames:
	page = pywikibot.Page(commons, pagename)
	text = page.get()
	inGallery = False
	inConsensual = 0
	for line in text.split("\n"):
		if line[:8] == "<gallery" and inGallery == False:
			inGallery = True
		elif line == "</gallery>" and inGallery == True:
			inGallery = False
		elif line == "= Consensual review =" and inConsensual == 0:
			inConsensual = 1

		if inGallery and line[:8] != "<gallery" and len(line) > 0:
			line = line.replace('By [[User', '')
			line = line.replace('by [[User', '')
			line_parts = line.split("|")
			# print(line_parts)
			user = userRE.search(line)
			# print(user)
			try:
				nominator = user.group(1)
				try:
					nominators[nominator] = nominators[nominator] + 1
					# print(nominators[nominator])
				except:
					nominators[nominator] = 1
				# print(nominators)
				next_test = line.split(user.group(1))[-1]
				# print(next_test)
				searchresult = userRE.search(next_test)
				if searchresult != None:
					reviewer = searchresult.group(1)
					try:
						reviewers[reviewer] = reviewers[reviewer] + 1
						# print(reviewers[reviewer])
					except:
						reviewers[reviewer] = 1
					# print(user2.group(1))
			except:
				pass

		if inConsensual:
			if "{{/" in line:
				line = line.replace('By [[User', '')
				line_parts = line.split("|")
				# print(line_parts)
				user = userRE.search(line)
				# print(user)
				nominator = user.group(1)
				try:
					nominators[nominator] = nominators[nominator] + 1
					# print(nominators[nominator])
				except:
					nominators[nominator] = 1
			else:
				searchresult = userRE.search(line)
				if searchresult != None:
					reviewer = searchresult.group(1)
					try:
						reviewers[reviewer] = reviewers[reviewer] + 1
						# print(reviewers[reviewer])
					except:
						reviewers[reviewer] = 1

report_page = "This page reports statistics for [[Commons:Quality images candidates/candidate list]] (including the last 7 archived days). It is automatically maintained by [[User:Pi bot]], please do not edit it as the bot will overwrite any changes tomorrow!\n\n{| class=\"wikitable sortable\"\n!User!!Nominations!!Reviews!!Nominations-Reviews"

users_done = []
for key, value in nominators.items():
	print(key + " " + str(value))
	users_done.append(key)
	try:
		review_count = reviewers[key]
	except:
		review_count = 0
	if review_count >= value:
		report_page = report_page + '\n|- style="background-color:lightgreen'
	else:
		report_page = report_page + '\n|-'
	report_page = report_page + '\n| ' + key + ' || ' + str(value) + ' || ' + str(review_count) + ' || '+ str(review_count-value)
for key, value in reviewers.items():
	if key not in users_done:
		report_page = report_page + '\n|- style="background-color:lightgreen'
		report_page = report_page + '\n| ' + key + ' || 0 || ' + str(value) + '||' + str(value)
		# print(key + " " + str(value))
# print(nominators)
# print(reviewers)
report_page = report_page + '\n|}\n[[Category:Quality images]]'
print(report_page)
reportingpage = pywikibot.Page(commons, reportpagename)
reportingpage.text = report_page
reportingpage.save('Updating')

