"""
Created by Julian Fawkes, 2020 and Chris Kelly 2021

generates fake data or functions as a DAQ script for the CR1000X datalogger
"""

import redis
import threading
import random
import datetime
import json
import openpyxl
from pathlib import Path
import os
import sys
from pyModbusTCP.client import ModbusClient
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.constants import Endian
import csv
import redis
import json
from collections import deque
import redis
import threading
import random
import datetime
import json

def gen_fake_data():
    threading.Timer(1.0, gen_fake_data).start() #normally 1.0
    dataset1 = dict(NO2=random.randint(0, 100), time1=(datetime.datetime.now()).strftime("%H:%M:%S"))
    dataset2 = dict(concentration=random.randint(8000, 9000), time2=(datetime.datetime.now()).strftime("%H:%M:%S"))
    dataset3 = dict(Ozone=random.randint(0, 100), time3=(datetime.datetime.now()).strftime("%H:%M:%S"))
    dataset4 = dict(CO=random.randint(0, 100), time4=(datetime.datetime.now()).strftime("%H:%M:%S"))
    dataset5 = dict(CO2=random.randint(0, 100), time5=(datetime.datetime.now()).strftime("%H:%M:%S"))
    dataset6 = dict(NO=random.randint(0, 100), time6=(datetime.datetime.now()).strftime("%H:%M:%S"))
    conn.set('no2', json.dumps(dataset1))
    conn.set('wcpc', json.dumps(dataset2))
    conn.set('ozone', json.dumps(dataset3))
    conn.set('teledyne', json.dumps(dataset4))
    conn.set('licor', json.dumps(dataset5))
    conn.set('no', json.dumps(dataset6))

def get_cr1000x_data():
    cr1000x = ModbusClient(host="169.254.67.85", port=502)
    cr1000x.open()

    global use_real_data

    while True:

        if use_real_data['ozone']:
            ozone_regs = cr1000x.read_holding_registers(0, 2)  # o3 is 0,2
            ozone_decoder = BinaryPayloadDecoder.fromRegisters(ozone_regs, Endian.Big, wordorder=Endian.Big)
            ozone_data = dict(Ozone=ozone_decoder.decode_32bit_float(), time3=(datetime.datetime.now()).strftime("%H:%M:%S"))
        else:
            ozone_data = dict(Ozone=random.randint(0, 100), time3=(datetime.datetime.now()).strftime("%H:%M:%S"))
        conn.set('ozone', json.dumps(ozone_data))

        if use_real_data['no']:
            no_regs = cr1000x.read_holding_registers(3, 2)  # no is 3,2
            no_decoder = BinaryPayloadDecoder.fromRegisters(no_regs, Endian.Big, wordorder=Endian.Big)
            no_data = dict(NO=no_decoder.decode_32bit_float(), time6=(datetime.datetime.now()).strftime("%H:%M:%S"))
        else:
            no_data = dict(NO=random.randint(0, 100), time6=(datetime.datetime.now()).strftime("%H:%M:%S"))
        conn.set('no', json.dumps(no_data))

        if use_real_data['no2']:
            no2_regs = cr1000x.read_holding_registers(5, 2)  # no2 is 5,2
            no2_decoder = BinaryPayloadDecoder.fromRegisters(no2_regs, Endian.Big, wordorder=Endian.Big)
            no2_data = dict(NO2=no2_decoder.decode_32bit_float(), time1=(datetime.datetime.now()).strftime("%H:%M:%S"))
        else:
            no2_data = dict(NO2=random.randint(0, 100), time1=(datetime.datetime.now()).strftime("%H:%M:%S"))
        conn.set('no2', json.dumps(no2_data))



        if use_real_data['wcpc']:
            a=1 #dummy line
        else:
            wcpc_data = dict(concentration=random.randint(8000, 9000), time2=(datetime.datetime.now()).strftime("%H:%M:%S"))
        conn.set('wcpc', json.dumps(wcpc_data))

        if use_real_data['licor']:
            a=1 #dummy line
        else:
            licor_data = dict(CO2=random.randint(0, 100), time5=(datetime.datetime.now()).strftime("%H:%M:%S"))
        conn.set('licor', json.dumps(licor_data))

        if use_real_data['teledyne']:
            a=1 #dummy line
        else:
            teledyne_data = dict(CO=random.randint(0, 100), time4=(datetime.datetime.now()).strftime("%H:%M:%S"))
        conn.set('teledyne', json.dumps(teledyne_data))




if __name__ == "__main__":

    use_real_data = {
        'no2': False,
        'wcpc': False,
        'ozone': True,
        'teledyne': False,
        'licor': False,
        'no': True
    }

    conn = redis.Redis(host='localhost')


    gen_fake_data()
    #get_cr1000x_data()