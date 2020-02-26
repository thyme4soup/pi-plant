
import sys
import os
import time
from datetime import datetime
import sqlite3 as lite
import hardware
import logging
from logging.handlers import RotatingFileHandler

path = sys.path[0] + '/' if sys.path[0] else ''
database = path + 'plant.db'
log = path + 'water.log'

log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(funcName)s(%(lineno)d) %(message)s')
my_handler = RotatingFileHandler(log, mode='a', maxBytes=5*1024,
                                 backupCount=2, encoding=None, delay=0)
my_handler.setFormatter(log_formatter)
my_handler.setLevel(logging.INFO)
app_log = logging.getLogger()
app_log.setLevel(logging.INFO)
app_log.addHandler(my_handler)

if __name__ == '__main__':
    now = datetime.utcnow()

    # check program args, manual or auto
    if len(sys.argv) != 2 or (sys.argv[1] != 'auto' and sys.argv[1] != 'manual'):
        print('usage: python water.py auto or python water.py manual')
        print(sys.argv)

    # auto pumping, check for auto tag and timing
    elif sys.argv[1] == 'auto':
        con = lite.connect(database)
        with con:
            # grab data from db
            cur = con.cursor()
            cur.execute("select is_auto from auto")
            is_auto = cur.fetchone()[0]
            cur.execute("select hours from frequency")
            hours = cur.fetchone()[0]
            cur.execute("select max(timestamp) from waterings")
            last_entry = cur.fetchone()[0]
            if last_entry:
                last_watering = datetime.strptime(last_entry, '%Y-%m-%d %H:%M:%S')
                hours_since = (now - last_watering).total_seconds() / (60 * 60)
            else:
                hours_since = 10000

            # check if we're due for a watering
            if is_auto and hours <= hours_since:
                if hardware.pump():
                    cur.execute("insert into waterings (timestamp, type, succeeded) values(datetime('now'), 'auto', true)")
                    app_log.info('Pump success at {}'.format(now))
                else:
                    app_log.info('Pump failed at {}'.format(now))
            else:
                app_log.info('Auto polled unsuccessfully at {}'.format(now))

    # manual pumping, no checking
    elif sys.argv[1] == 'manual':
        if hardware.pump():
            app_log.info("manual pump at {} succeeded".format(now))
        else:
            app_log.info("manual pump at {} failed".format(now))
