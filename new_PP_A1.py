"""
To use this script, place a sensor transcript/readout CSV file in the 'PEAK' folder, rename the file to 'IN.csv' and
then run this script. It MUST be places in the 'PEAK' folder and MUST be named 'IN.csv' exactly

(this just runs A1 as a post processing algorithim)
"""



import math
import csv
import pandas as pd
from collections import deque
import statistics
from configparser import ConfigParser
import numpy as np


####################################### GLOBAL SETTINGS #######################################
parser = ConfigParser(allow_no_value=True)
parser.read('user_defined_settings.ini')

A1_coeff = {
    "no2": parser.getint('A1_coeff','NO2'),
    "wcpc": parser.getint('A1_coeff','WCPC'),
    "o3": parser.getint('A1_coeff','O3'),
    "co": parser.getint('A1_coeff','CO'),
    "co2": parser.getint('A1_coeff','CO2'),
    "no": parser.getint('A1_coeff','NO') }
A1_percentile = {
    "no2": parser.getint('A1_percentile','NO2'),
    "wcpc": parser.getint('A1_percentile','WCPC'),
    "o3": parser.getint('A1_percentile','O3'),
    "co": parser.getint('A1_percentile','CO'),
    "co2": parser.getint('A1_percentile','CO2'),
    "no": parser.getint('A1_percentile','NO')}
A1_thresh_bump_percentile = {
    "no2": parser.getint('A1_thresh_bump_percentile', 'NO2'),
    "wcpc": parser.getint('A1_thresh_bump_percentile', 'WCPC'),
    "o3": parser.getint('A1_thresh_bump_percentile', 'O3'),
    "co": parser.getint('A1_thresh_bump_percentile', 'CO'),
    "co2": parser.getint('A1_thresh_bump_percentile', 'CO2'),
    "no": parser.getint('A1_thresh_bump_percentile', 'NO')}
A1_thresh_dump = {
    "no2": parser.getboolean('A1_post_processing_thresh_dump', 'NO2'),
    "wcpc": parser.getboolean('A1_post_processing_thresh_dump', 'WCPC'),
    "o3": parser.getboolean('A1_post_processing_thresh_dump', 'O3'),
    "co": parser.getboolean('A1_post_processing_thresh_dump', 'CO'),
    "co2": parser.getboolean('A1_post_processing_thresh_dump', 'CO2'),
    "no": parser.getboolean('A1_post_processing_thresh_dump', 'NO') }
#base_thresh_only = parser.getboolean('A1_post_processing_thresh_dump', 'only_show_base_thresh')
base_thresh_only = False
#limit_thresh = parser.getboolean('A1_post_processing_thresh_dump', 'limit_thresh_to_just_above_max')
limit_thresh = False

A1_startup_bypass = parser.getint('A1_misc','startup_bypass')
queue_size = parser.getint('A1_misc', 'chunk_size')
trace_length = 60

directory = parser.get('A1_misc', 'folder_directory')
if (directory[-1] != '/'):
    directory += '/'
filename = directory+(parser.get('A1_misc','input_filename'))
output_csv = directory+(parser.get('A1_misc','output_filename'))

col_names = ["Row","Time", "NO2 (ppb)", "WCPC (#/cm^3)", "O3 (ppb)", "CO (ppb)", "CO2 (ppm)",'NO (ppb)']
output_cols = ["Row","Time", "NO2 (ppb)", "WCPC (#/cm^3)", "O3 (ppb)", "CO (ppb)", "CO2 (ppm)",'NO (ppb)',"","NO2 peak (ppb)"]
if A1_thresh_dump['no2']:
    output_cols.append('NO2 thresh')
output_cols.append('WCPC peak (#/cm^3)')
if A1_thresh_dump['wcpc']:
    output_cols.append('WCPC thresh')
output_cols.append('O3 peak (ppb)')
if A1_thresh_dump['o3']:
    output_cols.append('O3 thresh')
output_cols.append('CO peak (ppb)')
if A1_thresh_dump['co']:
    output_cols.append('CO thresh')
output_cols.append('CO2 peak (ppm)')
if A1_thresh_dump['co2']:
    output_cols.append('CO2 thresh')
output_cols.append('NO peak (ppb)')
if A1_thresh_dump['no']:
    output_cols.append('NO thresh')

traces = dict(
    no2=deque([], maxlen=trace_length),
    wcpc=deque([], maxlen=trace_length),
    o3=deque([], maxlen=trace_length),
    co=deque([], maxlen=trace_length),
    co2=deque([], maxlen=trace_length),
    no=deque([], maxlen=trace_length),
)

A1_n = {
    "no2": 0,
    "wcpc": 0,
    "o3": 0,
    "co": 0,
    "co2": 0,
    "no": 0}
current_chunk=0

###############################################################################################



#returns the pollutant value if it's a peak, if not then it returns 0
def ispeak(pollutant):
    global A1_n
    global A1_coeff
    global A1_percentile
    global A1_thresh_bump_percentile
    global traces

    #compute list of points below our percentile, return 0 if there's an issue
    m = np.percentile(traces[pollutant], A1_percentile[pollutant])
    below_m = []
    for x in traces[pollutant]:
        if x<m:
            below_m.append(x)
    if len(below_m)<2:
        A1_n[pollutant] = 0
        return 0

    #calculating thresh
    sd = statistics.stdev(below_m)  # stdev will do sample sd and pstdev will do population sd
    thresh = A1_coeff[pollutant] * sd
    if A1_thresh_bump_percentile[pollutant] != 0:
        thresh += np.percentile(traces[pollutant], A1_thresh_bump_percentile[pollutant])

    #checking appropriate condition
    if traces[pollutant][-1] > thresh:
        if A1_n[pollutant] == 0:
            A1_n[pollutant] += 1
            return traces[pollutant][-1]
        else:
            if traces[pollutant][-1] > (thresh + sd * math.sqrt(A1_n[pollutant])):
                A1_n[pollutant] += 1
                return traces[pollutant][-1]
            else:
                A1_n[pollutant] = 0
                return 0
    else:
        A1_n[pollutant] = 0
        return 0

#same as ispeak but will return a list of length 2, first value is result of ispeak, second value is the thresh
def ispeakAndThresh(pollutant):
    global A1_n
    global A1_coeff
    global A1_percentile
    global A1_thresh_bump_percentile
    global traces
    global base_thresh_only

    #compute list of points below our percentile, return 0 if there's an issue
    m = np.percentile(traces[pollutant], A1_percentile[pollutant])
    below_m = []
    for x in traces[pollutant]:
        if x<m:
            below_m.append(x)
    if len(below_m)<2:
        A1_n[pollutant] = 0
        return [0, 0]

    #calculating thresh
    sd = statistics.stdev(below_m)  # stdev will do sample sd and pstdev will do population sd
    thresh = A1_coeff[pollutant] * sd
    if A1_thresh_bump_percentile[pollutant] != 0:
        thresh += np.percentile(traces[pollutant], A1_thresh_bump_percentile[pollutant])

    #checking appropriate condition
    if traces[pollutant][-1] > thresh:
        if A1_n[pollutant] == 0:
            A1_n[pollutant] += 1
            return [traces[pollutant][-1], thresh]
        else:
            if traces[pollutant][-1] > (thresh + sd * math.sqrt(A1_n[pollutant])):
                A1_n[pollutant] += 1
                if base_thresh_only:
                    return [traces[pollutant][-1], thresh]
                else:
                    return [traces[pollutant][-1], (thresh + sd * math.sqrt(A1_n[pollutant]))]
            else:
                A1_n[pollutant] = 0
                if base_thresh_only:
                    return [0,thresh]
                else:
                    return [0, (thresh + sd * math.sqrt(A1_n[pollutant]))]
    else:
        A1_n[pollutant] = 0
        return [0, thresh]

#computes the peak list to be written to the CSV
def compute_peak_list(input_list, pollutant):
    global A1_startup_bypass
    global traces
    global A1_thresh_dump
    global thresh_dict
    output_list=[]

    for i in input_list:
        traces[pollutant].append(i)
        if len(traces[pollutant])<A1_startup_bypass:
            output_list.append(0)
            if A1_thresh_dump[pollutant]:
                thresh_dict[pollutant].append(0)
        else:
            if A1_thresh_dump[pollutant]:
                eval = ispeakAndThresh(pollutant)
                output_list.append(eval[0])
                thresh_dict[pollutant].append(eval[1])
            else:
                output_list.append(ispeak(pollutant))

    return output_list




while True:
    # read in the current chunk
    data = pd.read_csv(filename, names=col_names, skiprows=(1 + current_chunk * queue_size), nrows=queue_size)

    # convert current chunk to lists
    no2_list = data["NO2 (ppb)"].to_list()
    wcpc_list = data["WCPC (#/cm^3)"].to_list()
    o3_list = data["O3 (ppb)"].to_list()
    co_list = data["CO (ppb)"].to_list()
    co2_list = data["CO2 (ppm)"].to_list()
    no_list = data['NO (ppb)'].to_list()
    row_list = data["Row"].to_list()
    time_list = data["Time"].to_list()

    #create thresh lists
    thresh_dict = {
        'no2': [],
        'wcpc': [],
        'o3': [],
        'co': [],
        'co2': [],
        'no': []
    }

    # compute peaks for current chunk and save as it's own list
    no2_peaks = compute_peak_list(no2_list,'no2')
    wcpc_peaks = compute_peak_list(wcpc_list,'wcpc')
    o3_peaks = compute_peak_list(o3_list,'o3')
    co_peaks = compute_peak_list(co_list,'co')
    co2_peaks = compute_peak_list(co2_list,'co2')
    no_peaks = compute_peak_list(no_list,'no')

    #limiting thresh if necessary
    if limit_thresh:
        maxes_dict = {
            'no2': (max(no2_list)),
            'wcpc': (max(wcpc_list)),
            'o3': (max(o3_list)),
            'co': (max(co_list)),
            'co2': (max(co2_list)),
            'no': (max(no_list))
        }
        for pollutant in thresh_dict:
            for i in range(0,len(thresh_dict[pollutant])):
                if thresh_dict[pollutant][i] > maxes_dict[pollutant]:
                    thresh_dict[pollutant][i] = maxes_dict[pollutant]

    #write current chunk to CSV
    with open(output_csv, "a", newline='') as f:
        w = csv.writer(f)

        #write headers if we're on the first chunk
        if current_chunk == 0:
            w.writerow(output_cols)

        #write data to CSV
        for i in range(0, len(row_list)):
            row = [row_list[i], time_list[i], no2_list[i], wcpc_list[i], o3_list[i], co_list[i], co2_list[i], no_list[i],"", no2_peaks[i]]

            if A1_thresh_dump['no2']:
                row.append(thresh_dict['no2'][i])

            row.append(wcpc_peaks[i])
            if A1_thresh_dump['wcpc']:
                row.append(thresh_dict['wcpc'][i])

            row.append(o3_peaks[i])
            if A1_thresh_dump['o3']:
                row.append(thresh_dict['o3'][i])

            row.append(co_peaks[i])
            if A1_thresh_dump['co']:
                row.append(thresh_dict['co'][i])

            row.append(co2_peaks[i])
            if A1_thresh_dump['co2']:
                row.append(thresh_dict['co2'][i])

            row.append(no_peaks[i])
            if A1_thresh_dump['no']:
                row.append(thresh_dict['no'][i])

            w.writerow(row)

    # break loop if we're on the last chunk, otherwise go to next chunk
    if len(no2_list) < queue_size:
        print("chunk " + str(current_chunk + 1) + " written")
        break
    else:
        print("chunk " + str(current_chunk + 1) + " written")
        current_chunk += 1