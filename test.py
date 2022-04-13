# Example bot for T301735 (https://phabricator.wikimedia.org/T301735) task
# (C) Feliciss, task completed on 03-April-2022

from pywikibot import exception, ItemPage, Site, User, PropertyPage
from pywikibot.site import DataSite
from pywikibot.exceptions import OtherPageSaveError, InvalidTitleError


# get_property_values_from_an_item
def get_property_values_from_an_item(data_site, item, prop, label, language) -> list:
	# get item page
	item_page = ItemPage(data_site, item)
	# construct list of multiple property values
	values = []
	for item in item_page.claims[prop]:
		target = item.getTarget()
		title = target.title()
		itm_page = ItemPage(data_site, title)
		value = itm_page.get()[label][language]
		values.append(value)
	return values


# get_qualifiers_from_a_claim
def get_qualifiers_from_a_claim(data_site, claim, label, language) -> (list, list):
	qualifiers = claim.qualifiers
	names = []
	targets = []
	for qualifier in qualifiers:
		for claim in qualifiers[qualifier]:
			claim_id = claim.getID()
			property_page = PropertyPage(data_site, claim_id)
			name = property_page.get()[label][language]
			target = claim.getTarget()
			names.append(name)
			targets.append(target)
	return names, targets


class T301735Bot:

	def __init__(self, source, user):
		self.source = source
		self.user = user

	# get_data_site: get and connect data site
	def get_data_site(self) -> DataSite:
		# connect site
		site = Site(self.source, self.source)
		repo = site.data_repository()
		return repo

	# get_user: get a user from a data site
	def get_user(self) -> User:
		# get data site
		data_site = self.get_data_site()
		# get user
		user = User(data_site, self.user)
		# return user
		return user

	# get_user_content: get the content from the user page
	def get_content_of_the_user(self) -> str:
		# get user
		user = self.get_user()
		# get the content of the user page
		content = user.get()
		# return content
		return content

	# print_user_page: print the user content from source
	def print_content_of_the_user(self) -> None:
		# get the content of the user page
		content = self.get_content_of_the_user()
		# print the content
		print(content)

	# add_content_to_a_user: add content to the end of the user page
	def add_content_to_a_user(self, text, summary) -> None:
		# get user
		user = self.get_user()
		# get the content of the user page
		content = self.get_content_of_the_user()
		# add text to the end of the content
		target = content.__add__(text)
		# put target content to a user if logged in
		try:
			user.put(target, summary)
		except OtherPageSaveError:
			exception()

	# search_data_from_a_user: search keywords of data items on Wikidata from a user
	def search_data_from_a_user(self, wikidata_data_type) -> list:
		# get user
		user = self.get_user()

		# get wikidata pages from the user
		pages = user.linkedPages()

		# list of page titles
		page_titles = []

		# search title of the data type on wikidata
		for page in pages:
			title = page.title()
			if title.startswith(wikidata_data_type):
				# add title if it's not an empty title
				if len(title) > 1:
					page_titles.append(title)

		return page_titles

	# print_property_value_from_a_page: now only supports printing author names on Wikidata items page
	def print_property_value_from_a_page(self, items, properties, label,
										 language) -> None:
		# get data site
		data_site = self.get_data_site()
		# code refers to https://www.wikidata.org/wiki/Wikidata:Creating_a_bot#Example_11:_Get_values_of_sub-properties
		# and https://github.com/mpeel/wikicode/blob/master/example.py
		for item in items:
			item_page = ItemPage(data_site, item)
			for prop in properties:
				if prop in item_page.claims:
					for claim in item_page.claims[prop]:
						target = claim.getTarget()
						names, targets = get_qualifiers_from_a_claim(data_site, claim, label, language)
						try:
							given_name_property = 'P735'
							family_name_property = 'P734'
							title = target.title()
							given_name = get_property_values_from_an_item(data_site, title, given_name_property, label,
																		  language)
							family_name = get_property_values_from_an_item(data_site, title, family_name_property,
																		   label,
																		   language)
							for name, target in zip(names, targets):
								print('Given Name:', *given_name, 'Family Name:', *family_name, (name, target))
						except InvalidTitleError:
							print(target, (*names, *targets))


def main(*args: str) -> None:
	# set source
	source = input('Please enter your source from, example: wikidata, wikipedia: ')

	# set user
	user = input('Please enter your username from that source: ')

	# init T301735 bot
	bot = T301735Bot(source, user)

	# print content of the user
	bot.print_content_of_the_user()

	# set text
	text = input('\nPlease enter the text you want to add onto that user: ')

	# set submit summary
	summary = input('\nPlease leave the summary you would like to submit (default: submit by script): ') or 'submit by ' \
																											'script '

	# add content to a user
	bot.add_content_to_a_user(text, summary)

	# set data type on Wikidata
	wikidata_data_type = input('\nPlease enter a data type on Wikidata, example: Q, P (default: Q): ') or 'Q'

	# determine if the user wants to import user page
	select = str(input('\nImport the user\'s Wikidata page to find items (y/n)? ').lower().strip()) or 'y'
	items = []
	if select == 'y':
		# search data from a user
		page_titles = bot.search_data_from_a_user(wikidata_data_type)
		items.extend(page_titles)
	else:
		# input custom items
		items.extend([str(i) for i in (
			input('\nPlease enter custom item(s) on Wikidata, example: Q106200605 Q56943026: ').split())])

	# print the items
	print(items)

	# set properties as keys to find the values on page
	properties = [str(i) for i in (input(
		'\nPlease enter the properties you wish to find, example (default): P2093 P50: ') or 'P2093 P50').split()]

	# print the properties
	print(properties)

	# set label as a key to find the values on page
	label = input('\nPlease enter the label you wish to find, example (default): labels: ') or 'labels'

	# set language as key to find the values on page
	language = input('\nPlease enter language as key used on Wikidata, example (default): en: ') or 'en'

	# print property value from a page
	bot.print_property_value_from_a_page(items, properties, label, language)


if __name__ == '__main__':
	main()
