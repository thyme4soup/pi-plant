
import hardware

import sys
import sqlite3 as lite
import logging
from logging.handlers import RotatingFileHandler

path = sys.path[0] + '/' if sys.path[0] else ''
database = path + 'plant.db'
log = path + 'sensor.log'


log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(funcName)s(%(lineno)d) %(message)s')
my_handler = RotatingFileHandler(log, mode='a', maxBytes=5*1024,
                                 backupCount=2, encoding=None, delay=0)
my_handler.setFormatter(log_formatter)
my_handler.setLevel(logging.INFO)
app_log = logging.getLogger()
app_log.setLevel(logging.INFO)
app_log.addHandler(my_handler)


if __name__ == '__main__':
    # get a value from hardware.read_moisture then put the value in the database
    val = hardware.read_moisture()
    app_log.info('read value {}'.format(val))
    if val:
        con = lite.connect(database)
        with con:
            # set db value
            cur = con.cursor()
            cur.execute("insert into moisture (timestamp, value) values(datetime('now'), {})".format(val))
        app_log.info('stored value {}'.format(val))
