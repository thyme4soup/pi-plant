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
from flask import (
    Flask, render_template, Response,
    request, flash, send_from_directory,
    redirect, jsonify
)


path = sys.path[0] + '/' if sys.path[0] else ''
database = path + 'plant.db'
log = path + 'app.log'

metric_fields = ['moisture']

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

    con = lite.connect(database)
    moisture = []
    with con:
        cur = con.cursor()
        for row in cur.execute("select * from moisture order by timestamp DESC limit 50"):
            moisture.append(row)
    print(moisture)

    metrics = {
        'moisture': moisture
    }
    return metrics

def add_metrics(metrics):
    con = lite.connect(database)
    with con:
        for key, val in metrics.items():
            if key not in metric_fields:
                continue
            cur = con.cursor()
            cur.execute("insert into moisture (timestamp, value) values(datetime('now'), {})".format(val))
            app_log.info(f'stored field {key} with value {val}')

@app.route('/', methods=['POST', 'GET'])
def index():
    """Video streaming home page."""
    metrics = get_metrics()
    auto_enabled = True
    con = lite.connect(database)
    print(con)

    if request.method == 'POST':
        if request.form['action'] == 'water':
            os.system('python water.py manual &')

        elif request.form['action'] == 'auto-toggle-on':
            with con:
                # set db value
                cur = con.cursor()
                cur.execute("update auto set is_auto = 1")
                print("set true")

        elif request.form['action'] == 'auto-toggle-off':
            with con:
                # set db value
                cur = con.cursor()
                cur.execute("update auto set is_auto = 0")
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

@app.route('/status', methods=['GET'])
def get_status():
    return jsonify(get_metrics())

@app.route('/report/<datatype>', methods=['POST'])
def receive_report(datatype):
    if datatype == 'data':
        try:
            content = request.get_json()
            add_metrics(content['data'])
        except e:
            msg = "payload must be a valid json"
            return jsonify({"error": msg}), 400
    elif datatype == 'image':
        pass
    else:
        msg = "invalid report endpoint"
        return jsonify({"error": msg}), 404
    return Response(200)

@app.route('/video_feed', methods=['GET'])
def video_feed():
    return send_from_directory('resources/', 'plantgif.gif')

if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True, use_reloader=True, debug=True)
