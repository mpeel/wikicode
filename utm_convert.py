#!/usr/bin/python
# -*- coding: utf-8  -*-
import csv
import utm
infile = open('utm/Gothas Adressen 2018 - Tabelle1.csv', mode='r')
reader = csv.reader(infile)
    # items = {[rows] for rows in reader}

print utm.to_latlon(340000, 5710000, 32, 'U')

i = 0
for row in reader:
	if i != 0:
		# print row[4]
		# print row[5]
		temp1 = str(row[4])[2:8]
		temp2 = str(row[5])[0:7]
		# print temp1
		# print temp2
		coord = utm.to_latlon(float(temp1), float(temp2), 32, 'U')
		# print coord
# 
		print row[0]+","+row[1]+","+row[2]+','+row[3]+','+str(coord[0])+','+str(coord[1])+','+row[6]
	else:
		print row
	i+=1
	