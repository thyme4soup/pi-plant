#!/bin/bash
cd /home/pi/pi-plant/ && /usr/bin/git pull && /usr/bin/pip3 install -r requirements.txt
/usr/bin/python3 /home/pi/pi-plant/app.py &
