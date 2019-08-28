
# https://www.tindie.com/products/tinovi/usb-soil-moisture-temperature-sensor/

def pump(duration = 1):
    # pump water
    print("watering! for {} second(s)".format(duration))
    return True

def read_moisture():
    print("reading!")
    return 0.5
