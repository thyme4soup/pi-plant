#!/usr/bin/env python
from importlib import import_module
import os
import json
import datetime
import random
import string
from flask import Flask, render_template, Response, request, flash

# import camera driver
if os.environ.get('PI_DEV'):
    from camera_test import Camera
else:
    from camera_pi import Camera


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

    if request.method == 'POST':
        if request.form['action'] == 'water':
            flash(Water.manual_water())
        elif request.form['action'] == 'auto-toggle-on':
            auto_enabled = Water.set_water(True)
        elif request.form['action'] == 'auto-toggle-off':
            auto_enabled = Water.set_water(False)

    return render_template('index.html', metrics=json.dumps(metrics), auto_enabled = auto_enabled)


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
