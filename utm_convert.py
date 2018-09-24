#!/usr/bin/python
# -*- coding: utf-8  -*-
# Convert UTM coordinates to standard ones
# Mike Peel, 23 August 2018

import csv
import utm

infile = open('utm/Gothas Adressen 2018 - Tabelle1.csv', mode='r')
reader = csv.reader(infile)
i = 0
for row in reader:
	if i != 0:
		temp1 = str(row[4])[2:8]
		temp2 = str(row[5])[0:7]
		coord = utm.to_latlon(float(temp1), float(temp2), 32, 'U')
		print row[0]+","+row[1]+","+row[2]+','+row[3]+','+str(coord[0])+','+str(coord[1])+','+row[6]
	else:
		print row
	i+=1