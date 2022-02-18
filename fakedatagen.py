"""
Created by Julian Fawkes, 2020

fakedatagen.py - A program used to emulate the data that is output by the 'instrument-DAQ' scripts. Used for testing Dash components when you don't have instruments on hand.
"""

import redis
import threading
import random
import datetime
import json

def gendata():
    threading.Timer(1.0, gendata).start()
    dataset1 = dict(NO2=random.randint(0, 100), time1=(datetime.datetime.now()).strftime("%H:%M:%S"))
    dataset2 = dict(concentration=random.randint(8000, 9000), time2=(datetime.datetime.now()).strftime("%H:%M:%S"))
    #dataset3 = dict(Ozone=random.randint(0, 100), time3=(datetime.datetime.now()).strftime("%H:%M:%S"))
    dataset4 = dict(CO=random.randint(0, 100), time4=(datetime.datetime.now()).strftime("%H:%M:%S"))
    dataset5 = dict(CO2=random.randint(0, 100), time5=(datetime.datetime.now()).strftime("%H:%M:%S"))
    conn.set('no2', json.dumps(dataset1))
    conn.set('wcpc', json.dumps(dataset2))
    #conn.set('ozone', json.dumps(dataset3))
    conn.set('teledyne', json.dumps(dataset4))
    conn.set('licor', json.dumps(dataset5))

if __name__ == "__main__":
    conn = redis.Redis(host='localhost')
    gendata()