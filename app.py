#!/usr/bin/env python
from importlib import import_module
import os
import sys
import json
import datetime
import random
import string
import sqlite3 as lite
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template, Response, request, flash

# import camera driver
if os.environ.get('PI_DEV'):
    from camera_test import Camera
else:
    from camera_pi import Camera

path = sys.path[0] + '/' if sys.path[0] else ''
database = path + 'plant.db'
log = path + 'app.log'

log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(funcName)s(%(lineno)d) %(message)s')
my_handler = RotatingFileHandler(log, mode='a', maxBytes=5*1024,
                                 backupCount=2, encoding=None, delay=0)
my_handler.setFormatter(log_formatter)
my_handler.setLevel(logging.INFO)
app_log = logging.getLogger()
app_log.setLevel(logging.INFO)
app_log.addHandler(my_handler)


app = Flask(__name__)
app.secret_key = ''.join(random.choice(string.ascii_lowercase) for i in range(random.randrange(8, 15)))

def get_metrics():
    moisture = []
    cur = 0.
    for i in range(20):
        moisture.append({'x': i, 'y': cur})
        cur = random.random() + cur - 0.5
    metrics = {
        'moisture': moisture
    }
    return metrics

@app.route('/', methods=['POST', 'GET'])
def index():
    """Video streaming home page."""
    metrics = get_metrics()
    auto_enabled = True
    con = lite.connect(database)

    if request.method == 'POST':
        if request.form['action'] == 'water':
            os.system('python water.py manual &')

        elif request.form['action'] == 'auto-toggle-on':
            with con:
                # set db value
                cur = con.cursor()
                cur.execute("update auto set is_auto = true")
                print("set true")

        elif request.form['action'] == 'auto-toggle-off':
            with con:
                # set db value
                cur = con.cursor()
                cur.execute("update auto set is_auto = false")
                print("set false")

    with con:
        # set db value
        cur = con.cursor()
        cur.execute("select is_auto from auto")
        auto_enabled = False if cur.fetchone()[0] == 0 else True
        cur.execute("select hours from frequency")
        hours = cur.fetchone()[0]

    return render_template('index.html',
                            metrics=json.dumps(metrics),
                            auto_enabled = auto_enabled,
                            hours = hours)


def gen(camera):
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True, use_reloader=True, debug=True)
