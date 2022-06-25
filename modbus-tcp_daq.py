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
from configparser import ConfigParser

#function for testing
def gen_fake_data():
    threading.Timer(1.0, gen_fake_data).start() #normally 1.0
    dataset1 = dict(NO2=random.randint(0, 1), time1=(datetime.datetime.now()).strftime("%H:%M:%S"))
    dataset2 = dict(concentration=random.randint(0, 1), time2=(datetime.datetime.now()).strftime("%H:%M:%S"))
    dataset3 = dict(Ozone=random.randint(0, 1), time3=(datetime.datetime.now()).strftime("%H:%M:%S"))
    dataset4 = dict(CO=random.randint(0, 1), time4=(datetime.datetime.now()).strftime("%H:%M:%S"))
    dataset5 = dict(CO2=random.randint(0, 1), time5=(datetime.datetime.now()).strftime("%H:%M:%S"))
    dataset6 = dict(NO=random.randint(0, 1), time6=(datetime.datetime.now()).strftime("%H:%M:%S"))
    dataset7 = dict(WS=random.randint(0, 1), time7=(datetime.datetime.now()).strftime("%H:%M:%S"))
    dataset8 = dict(WD=random.randint(0, 1), time8=(datetime.datetime.now()).strftime("%H:%M:%S"))

    conn.set('no2', json.dumps(dataset1))
    conn.set('wcpc', json.dumps(dataset2))
    conn.set('ozone', json.dumps(dataset3))
    conn.set('teledyne', json.dumps(dataset4))
    conn.set('licor', json.dumps(dataset5))
    conn.set('no', json.dumps(dataset6))
    conn.set('ws', json.dumps(dataset7))
    conn.set('wd', json.dumps(dataset8))

#main DAQ functions
def get_modbus_data(ip, port, enable_pollutant, holding_regs, disabled_behaviour):
    cr1000x = ModbusClient(host=ip, port=port)
    cr1000x.open()

    while True:

        print('i')
        if enable_pollutant['o3']:
            ozone_regs = cr1000x.read_holding_registers(holding_regs['o3'][0], holding_regs['o3'][1])  # o3 is 0,2
            ozone_decoder = BinaryPayloadDecoder.fromRegisters(ozone_regs, Endian.Big, wordorder=Endian.Big)
            ozone_data = dict(Ozone=round(ozone_decoder.decode_32bit_float(),2), time3=(datetime.datetime.now()).strftime("%H:%M:%S"))
        elif disabled_behaviour == 'random':
            ozone_data = dict(Ozone=random.randint(0, 100), time3=(datetime.datetime.now()).strftime("%H:%M:%S"))
        else:
            ozone_data = dict(Ozone=0, time3=(datetime.datetime.now()).strftime("%H:%M:%S"))
        conn.set('ozone', json.dumps(ozone_data))

        if enable_pollutant['no']:
            no_regs = cr1000x.read_holding_registers(holding_regs['no'][0], holding_regs['no'][1])  # no is 3,2
            no_decoder = BinaryPayloadDecoder.fromRegisters(no_regs, Endian.Big, wordorder=Endian.Big)
            no_data = dict(NO=round(no_decoder.decode_32bit_float(),2), time6=(datetime.datetime.now()).strftime("%H:%M:%S"))
        elif disabled_behaviour == 'random':
            no_data = dict(NO=random.randint(0, 100), time6=(datetime.datetime.now()).strftime("%H:%M:%S"))
        else:
            no_data = dict(NO=0, time6=(datetime.datetime.now()).strftime("%H:%M:%S"))
        conn.set('no', json.dumps(no_data))

        if enable_pollutant['no2']:
            no2_regs = cr1000x.read_holding_registers(holding_regs['no2'][0], holding_regs['no2'][1])  # no2 is 5,2
            no2_decoder = BinaryPayloadDecoder.fromRegisters(no2_regs, Endian.Big, wordorder=Endian.Big)
            no2_data = dict(NO2=round(no2_decoder.decode_32bit_float(),2), time1=(datetime.datetime.now()).strftime("%H:%M:%S"))
        elif disabled_behaviour == 'random':
            no2_data = dict(NO2=random.randint(0, 100), time1=(datetime.datetime.now()).strftime("%H:%M:%S"))
        else:
            no2_data = dict(NO2=0, time1=(datetime.datetime.now()).strftime("%H:%M:%S"))
        conn.set('no2', json.dumps(no2_data))

        if enable_pollutant['wcpc']:
            wcpc_regs = cr1000x.read_holding_registers(holding_regs['wcpc'][0], holding_regs['wcpc'][1])
            wcpc_decoder = BinaryPayloadDecoder.fromRegisters(wcpc_regs, Endian.Big, wordorder=Endian.Big)
            wcpc_data = dict(concentration=round(wcpc_decoder.decode_32bit_float(),2), time2=(datetime.datetime.now()).strftime("%H:%M:%S"))
        elif disabled_behaviour == 'random':
            wcpc_data = dict(concentration=random.randint(8000, 9000), time2=(datetime.datetime.now()).strftime("%H:%M:%S"))
        else:
            wcpc_data = dict(concentration=0, time2=(datetime.datetime.now()).strftime("%H:%M:%S"))
        conn.set('wcpc', json.dumps(wcpc_data))

        if enable_pollutant['co2']:
            co2_regs = cr1000x.read_holding_registers(holding_regs['co2'][0], holding_regs['co2'][1])
            co2_decoder = BinaryPayloadDecoder.fromRegisters(co2_regs, Endian.Big, wordorder=Endian.Big)
            co2_data = dict(CO2=round(co2_decoder.decode_32bit_float(),2), time5=(datetime.datetime.now()).strftime("%H:%M:%S"))
        elif disabled_behaviour == 'random':
            co2_data = dict(CO2=random.randint(0, 100), time5=(datetime.datetime.now()).strftime("%H:%M:%S"))
        else:
            co2_data = dict(CO2=0, time5=(datetime.datetime.now()).strftime("%H:%M:%S"))
        conn.set('licor', json.dumps(co2_data))

        if enable_pollutant['co']:
            co_regs = cr1000x.read_holding_registers(holding_regs['co'][0], holding_regs['co'][1])
            co_decoder = BinaryPayloadDecoder.fromRegisters(co_regs, Endian.Big, wordorder=Endian.Big)
            co_data = dict(CO=round(co_decoder.decode_32bit_float(),2), time4=(datetime.datetime.now()).strftime("%H:%M:%S"))
        elif disabled_behaviour == 'random':
            co_data = dict(CO=random.randint(0, 100), time4=(datetime.datetime.now()).strftime("%H:%M:%S"))
        else:
            co_data = dict(CO=0, time4=(datetime.datetime.now()).strftime("%H:%M:%S"))
        conn.set('teledyne', json.dumps(co_data))

        if enable_pollutant['ws']:
            ws_regs = cr1000x.read_holding_registers(holding_regs['ws'][0], holding_regs['ws'][1])
            ws_decoder = BinaryPayloadDecoder.fromRegisters(ws_regs, Endian.Big, wordorder=Endian.Big)
            ws_data = dict(WS=round(ws_decoder.decode_32bit_float(),2), time7=(datetime.datetime.now()).strftime("%H:%M:%S"))
        elif disabled_behaviour == 'random':
            ws_data = dict(WS=random.randint(0, 100), time7=(datetime.datetime.now()).strftime("%H:%M:%S"))
        else:
            ws_data = dict(WS=0, time7=(datetime.datetime.now()).strftime("%H:%M:%S"))
        conn.set('ws', json.dumps(ws_data))

        if enable_pollutant['wd']:
            wd_regs = cr1000x.read_holding_registers(holding_regs['wd'][0], holding_regs['wd'][1])
            wd_decoder = BinaryPayloadDecoder.fromRegisters(wd_regs, Endian.Big, wordorder=Endian.Big)
            wd_data = dict(WD=round(wd_decoder.decode_32bit_float(),2), time8=(datetime.datetime.now()).strftime("%H:%M:%S"))
        elif disabled_behaviour == 'random':
            wd_data = dict(WD=random.randint(0, 100), time8=(datetime.datetime.now()).strftime("%H:%M:%S"))
        else:
            wd_data = dict(WD=0, time8=(datetime.datetime.now()).strftime("%H:%M:%S"))
        conn.set('wd', json.dumps(wd_data))



if __name__ == "__main__":

    #setup config parser
    parser = ConfigParser(allow_no_value=True)
    parser.read('user_defined_settings.ini')

    #pull settings from config file
    enable_pollutant_setting = {
        'no2': parser.getboolean('modbus-tcp_settings','enable_no2'),
        'wcpc': parser.getboolean('modbus-tcp_settings','enable_wcpc'),
        'o3': parser.getboolean('modbus-tcp_settings','enable_o3'),
        'co': parser.getboolean('modbus-tcp_settings','enable_co'),
        'co2': parser.getboolean('modbus-tcp_settings','enable_co2'),
        'no': parser.getboolean('modbus-tcp_settings','enable_no'),
        'ws': parser.getboolean('modbus-tcp_settings','enable_ws'),
        'wd': parser.getboolean('modbus-tcp_settings','enable_wd')
    }
    ip_setting = parser.get('modbus-tcp_settings','ip_address')
    port_setting = parser.getint('modbus-tcp_settings','port')

    holding_regs_setting = dict(
        no2=[0,0],
        wcpc=[0,0],
        o3=[0,0],
        co=[0,0],
        co2=[0,0],
        no=[0,0],
        ws=[0,0],
        wd=[0,0]
    )

    for pollutant in enable_pollutant_setting:
        if enable_pollutant_setting[pollutant]:
            holding_regs_setting[pollutant][0] = parser.getint('modbus-tcp_settings', (pollutant + '_modbus_hr'))
            holding_regs_setting[pollutant][1] = parser.getint('modbus-tcp_settings', (pollutant + '_hr_length'))

    #disabled_behaviour_setting = parser.get('modbus-tcp_settings', 'random_or_flat_if_disabled')
    disabled_behaviour_setting = 'flat' #manual override
    disabled_behaviour_setting = 'random'
    if not (disabled_behaviour_setting == 'random' or disabled_behaviour_setting == 'flat'):
        if not (enable_pollutant_setting['no2'] and enable_pollutant_setting['wcpc'] and enable_pollutant_setting['o3'] and enable_pollutant_setting['co'] and enable_pollutant_setting['co2'] and enable_pollutant_setting['no'] and enable_pollutant_setting['ws'] and enable_pollutant_setting['wd']):
            sys.exit('ERROR: the setting \'random_or_flat_if_disabled\' must be set to either \'random\' or \'flat\'')

    #establish redis connection
    conn = redis.Redis(host='localhost')

    #printing information
    print('ip address: '+ip_setting)
    print('port: '+str(port_setting)+'\n')
    for pollutant in enable_pollutant_setting:
        if enable_pollutant_setting[pollutant]:
            print(pollutant+': enabled on holding register '+str(holding_regs_setting[pollutant][0])+', reading '+str(holding_regs_setting[pollutant][1])+' register(s)')
        else:
            #print(pollutant+": disabled using \'"+disabled_behaviour_setting+'\' behaviour')
            print(pollutant + ": disabled")


    all_disabled = True
    for pollutant in enable_pollutant_setting:
        if enable_pollutant_setting[pollutant]:
            all_disabled = False
            break

    if all_disabled:
        gen_fake_data()
    else:
        get_modbus_data(ip_setting, port_setting, enable_pollutant_setting, holding_regs_setting, disabled_behaviour_setting)