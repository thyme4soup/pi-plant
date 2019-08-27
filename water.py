
import sys
import os
import time
from datetime import datetime
import sqlite3 as lite

def pump():
    # pump water
    print("watering!")
    return True

if __name__ == '__main__':
    now = datetime.utcnow()

    # check program args, manual or auto
    if len(sys.argv) != 2 or (sys.argv[1] != 'auto' and sys.argv[1] != 'manual'):
        print('usage: python water.py auto or python water.py manual')
        print(sys.argv)

    # auto pumping, check for auto tag and timing
    elif sys.argv[1] == 'auto':
        con = lite.connect('plant.db')
        with con:
            # grap data from db
            cur = con.cursor()
            cur.execute("select is_auto from auto")
            is_auto = cur.fetchone()[0]
            cur.execute("select hours from frequency")
            hours = cur.fetchone()[0]
            cur.execute("select max(timestamp) from waterings")
            last_watering = datetime.strptime(cur.fetchone()[0], '%Y-%m-%d %H:%M:%S')
            hours_since = (now - last_watering).total_seconds() / (60 * 60)

            # check if we're due for a watering
            if is_auto and hours <= hours_since:
                if pump():
                    cur.execute("insert into waterings values(datetime('now'))")
                else:
                    print('pump unsuccessful')
            else:
                print('Auto polled unsuccessfully at {}'.format(now))

    # manual pumping, no checking
    elif sys.argv[1] == 'manual':
        pump()
        print("manual pump at {}".format(now))
