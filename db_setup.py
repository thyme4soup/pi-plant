
import sqlite3 as lite
import logging
from logging.handlers import RotatingFileHandler

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

if __name__ == '__main__':
    con = lite.connect(database)
    with con:
        # set db value
        cur = con.cursor()

        # setup auto table
        cur.execute("create table auto(is_auto boolean)")
        cur.execute("insert into auto (is_auto) VALUES (true)")

        # setup watering frequency auto_enabled
        cur.execute("create table frequency(hours numeric)")
        cur.execute("insert into frequency (hours) VALUES (1.5)")

        # setup waterings tracking
        cur.execute("create table waterings(timestamp datetime, type varchar(255), succeeded boolean)")
    print("plant.db created and formatted")
