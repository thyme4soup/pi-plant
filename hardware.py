
from datetime import datetime
from noise import pnoise1
# https://www.tindie.com/products/tinovi/usb-soil-moisture-temperature-sensor/

def pump(duration = 1):
    # pump water
    print("watering! for {} second(s)".format(duration))
    return True

def read_moisture():
    print("reading!")

    # 1 week
    cycle_time = 604800
    epoch = datetime.utcfromtimestamp(0)
    def unix_time_millis(dt):
        return (dt - epoch).total_seconds()

    input = unix_time_millis(datetime.utcnow()) % cycle_time / cycle_time
    output = pnoise1(input)

    return output
