#!/bin/bash
source /home/pi/.profile
export PYTHONPATH=/home/pi/Documents/core:$PYTHONPATH
cd /home/pi/Documents/wikicode/

/usr/bin/python3 touch_wlm_brazil.py
