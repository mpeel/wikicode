#!/bin/bash
source /home/pi/.profile
export PYTHONPATH=/home/pi/Documents/git/core:$PYTHONPATH
source /home/pi/.bashrc
cd /home/pi/Documents/git/wikicode/

/usr/bin/python3 touch_wlm_brazil.py
