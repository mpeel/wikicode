#!/usr/bin/python3
# -*- coding: utf-8  -*-
# import pip
import os
import json
# pip.main(['list'])
import pywikibot
import mysql.connector
from database_login import *

GET={}
args=os.getenv("QUERY_STRING").split('&')
# print args

for arg in args:
	t=arg.split('=')
	if len(t)>1: k,v=arg.split('='); GET[k]=v

wikidata_site = pywikibot.Site("wikidata", "wikidata")
repo = wikidata_site.data_repository()  # this is a DataSite object
commons = pywikibot.Site('commons', 'commons')

mydb = mysql.connector.connect(
  host=database_host,
  user=database_user,
  passwd=database_password,
  database=database_database
)
mycursor = mydb.cursor()

print("Content-type: text/html\n\n")

mycursor.execute('SELECT decision, count(*) as NUM FROM newwikiquote GROUP BY decision ORDER BY NUM DESC')
myresult = mycursor.fetchall()
print('<table style="border:1px solid black;">')
total = 0
for val in myresult:
	print('<tr><td style="text-align:right;">' + str(val[1]) + "</td><td>")
	if val[0] == 0:
		print("Not done yet")
	elif val[0] == 1:
		print("No longer relevant")
	elif val[0] == 2:
		print("No")
	elif val[0] == 3:
		print("Yes")
	elif val[0] == 4:
		print("Excluded")
	else:
		print(str(val[0]))
	print("</td></tr>")
	total += int(val[1])
print("<tr><td>" + str(total) + "</td><td>Total</td></tr>")
print("</table>")


mycursor.execute('SELECT user, count(*) as NUM FROM newwikiquote GROUP BY user ORDER BY NUM DESC')
myresult = mycursor.fetchall()
print('<table style="border:1px solid black;">')
for val in myresult:
	print('<tr><td style="text-align:right;">' + str(val[1]) + "</td><td>")
	if val[0] == "NA":
		print("(Done outside of game)")
	elif val[0] == "":
		print("Not done yet")
	else:
		print(str(val[0]))
	print("</td></tr>")
print("</table>")

mycursor.execute('SELECT site, count(*) as NUM FROM newwikiquote WHERE done=0 GROUP BY site ORDER BY NUM DESC')
myresult = mycursor.fetchall()
print('<table style="border:1px solid black;">')
total = 0
for val in myresult:
	print('<tr><td style="text-align:right;">' + str(val[1]) + "</td><td>")
	print(str(val[0]))
	print("</td></tr>")
	total += int(val[1])
print("<tr><td>" + str(total) + "</td><td>Total</td></tr>")
print("</table>")
