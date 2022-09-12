"""
This script will run A1 as a post processing algorithm on a sensor transcript CSV.

All of the settings related to A1 in 'user_defined_settings.ini' must be specified in order for this script to work.
"""



import math
import csv
import pandas as pd
from collections import deque
import statistics
from configparser import ConfigParser
import numpy as np
import sys
from os.path import exists

#used for grabbing bulk processing settings, will also keep the asterisk if there is one
def full_string_to_int_list(string_in):

    # remove all spaces from string_in
    string_in = string_in.replace(" ", "")

    crit = False
    if string_in[-1] == '*':
        string_in = string_in.strip('*')
        crit = True

    string_in += ','
    output=[]
    adding_to_result=''

    for i in range(0,len(string_in)):
        if string_in[i] == ',':
            output.append(int(adding_to_result))
            adding_to_result=''
        else:
            adding_to_result += string_in[i]

    if crit:
        output.append('*')
    return output

#fills in settings for smaller bulk processing list
def fill_smaller_bulk(smaller,target_length):
    while len(smaller) < target_length:
        smaller.append(smaller[-1])
    return smaller

####################################### GLOBAL SETTINGS #######################################

#check if user defined settings file exists
if exists('user_defined_settings.ini') == False:
    sys.exit("ERROR: \"user_defined_settings.ini\" config file not found, please run \"create_default_config.py\"")

#create config parser and read settings file
parser = ConfigParser(allow_no_value=True)
parser.read('user_defined_settings.ini')

#grabbing directory and filename, fixing formatting, checking if input file exists at that directory
directory = parser.get('A1_misc', 'folder_directory')
if directory == '':
    sys.exit("ERROR: please specify a directory for the [A1_misc] \"folder_directory\" setting")
if '\\' in directory:
    directory.replace("\\", "/")
if (directory[-1] != '/'):
    directory += '/'
filename = directory+(parser.get('A1_misc','input_filename'))
if exists(filename) == False:
    sys.exit('ERROR: \"'+filename+'\" file not found, please check [A1_misc] \"input_filename\" setting')
output_csv = directory + (parser.get('A1_misc', 'output_filename'))

bulk_processing = parser.getboolean('A1_bulk_processing','enable_bulk_processing')

A1_thresh_dump = {
        "no2": parser.getboolean('A1_post_processing_thresh_dump', 'NO2'),
        "wcpc": parser.getboolean('A1_post_processing_thresh_dump', 'WCPC'),
        "o3": parser.getboolean('A1_post_processing_thresh_dump', 'O3'),
        "co": parser.getboolean('A1_post_processing_thresh_dump', 'CO'),
        "co2": parser.getboolean('A1_post_processing_thresh_dump', 'CO2'),
        "no": parser.getboolean('A1_post_processing_thresh_dump', 'NO'),
        "ws": parser.getboolean('A1_post_processing_thresh_dump', 'WS'),
        "wd": parser.getboolean('A1_post_processing_thresh_dump', 'WD')
    }

#grabbing pollutant specific settings, either for bulk or normal
if bulk_processing == False:
    A1_coeff = {
        "no2": parser.getint('A1_coeff','NO2'),
        "wcpc": parser.getint('A1_coeff','WCPC'),
        "o3": parser.getint('A1_coeff','O3'),
        "co": parser.getint('A1_coeff','CO'),
        "co2": parser.getint('A1_coeff','CO2'),
        "no": parser.getint('A1_coeff','NO'),
        "ws": parser.getint('A1_coeff','WS'),
        "wd": parser.getint('A1_coeff','WD')
    }
    A1_percentile = {
        "no2": parser.getint('A1_percentile','NO2'),
        "wcpc": parser.getint('A1_percentile','WCPC'),
        "o3": parser.getint('A1_percentile','O3'),
        "co": parser.getint('A1_percentile','CO'),
        "co2": parser.getint('A1_percentile','CO2'),
        "no": parser.getint('A1_percentile','NO'),
        "ws": parser.getint('A1_percentile','WS'),
        "wd": parser.getint('A1_percentile','WD')
    }
    A1_thresh_bump_percentile = {
        "no2": parser.getint('A1_thresh_bump_percentile', 'NO2'),
        "wcpc": parser.getint('A1_thresh_bump_percentile', 'WCPC'),
        "o3": parser.getint('A1_thresh_bump_percentile', 'O3'),
        "co": parser.getint('A1_thresh_bump_percentile', 'CO'),
        "co2": parser.getint('A1_thresh_bump_percentile', 'CO2'),
        "no": parser.getint('A1_thresh_bump_percentile', 'NO'),
        "ws": parser.getint('A1_thresh_bump_percentile', 'WS'),
        "wd": parser.getint('A1_thresh_bump_percentile', 'WD')
    }
else:
    max_entries = 0
    all_A1_coeffs = {
        "no2": full_string_to_int_list(parser.get('A1_bulk_processing','no2_coeffs')),
        "wcpc": full_string_to_int_list(parser.get('A1_bulk_processing','wcpc_coeffs')),
        "o3": full_string_to_int_list(parser.get('A1_bulk_processing','o3_coeffs')),
        "co": full_string_to_int_list(parser.get('A1_bulk_processing','co_coeffs')),
        "co2": full_string_to_int_list(parser.get('A1_bulk_processing','co2_coeffs')),
        "no": full_string_to_int_list(parser.get('A1_bulk_processing','no_coeffs')),
        "ws": full_string_to_int_list(parser.get('A1_bulk_processing','ws_coeffs')),
        "wd": full_string_to_int_list(parser.get('A1_bulk_processing','wd_coeffs'))
    }
    coeff_crits = {
        "no2": False,
        "wcpc": False,
        "o3": False,
        "co": False,
        "co2": False,
        "no": False,
        "ws": False,
        "wd": False
    }
    for i in coeff_crits:
        if all_A1_coeffs[i][-1] == '*':
            coeff_crits[i] = True
            del all_A1_coeffs[i][-1]
    for i in all_A1_coeffs:
        if (len(all_A1_coeffs[i]) > max_entries):
            max_entries = len(all_A1_coeffs[i])

    all_A1_percentiles = {
        "no2": full_string_to_int_list(parser.get('A1_bulk_processing','no2_percentiles')),
        "wcpc": full_string_to_int_list(parser.get('A1_bulk_processing','wcpc_percentiles')),
        "o3": full_string_to_int_list(parser.get('A1_bulk_processing','o3_percentiles')),
        "co": full_string_to_int_list(parser.get('A1_bulk_processing','co_percentiles')),
        "co2": full_string_to_int_list(parser.get('A1_bulk_processing','co2_percentiles')),
        "no": full_string_to_int_list(parser.get('A1_bulk_processing','no_percentiles')),
        "ws": full_string_to_int_list(parser.get('A1_bulk_processing','ws_percentiles')),
        "wd": full_string_to_int_list(parser.get('A1_bulk_processing','wd_percentiles'))
    }
    percentile_crits = {
        "no2": False,
        "wcpc": False,
        "o3": False,
        "co": False,
        "co2": False,
        "no": False,
        "ws": False,
        "wd": False
    }
    for i in percentile_crits:
        if all_A1_percentiles[i][-1] == '*':
            percentile_crits[i] = True
            del all_A1_percentiles[i][-1]
    for i in all_A1_percentiles:
        if (len(all_A1_percentiles[i]) > max_entries):
            max_entries = len(all_A1_percentiles[i])

    all_A1_thresh_bump_percentiles = {
        "no2": full_string_to_int_list(parser.get('A1_bulk_processing','no2_thresh_bump_percentiles')),
        "wcpc": full_string_to_int_list(parser.get('A1_bulk_processing','wcpc_thresh_bump_percentiles')),
        "o3": full_string_to_int_list(parser.get('A1_bulk_processing','o3_thresh_bump_percentiles')),
        "co": full_string_to_int_list(parser.get('A1_bulk_processing','co_thresh_bump_percentiles')),
        "co2": full_string_to_int_list(parser.get('A1_bulk_processing','co2_thresh_bump_percentiles')),
        "no": full_string_to_int_list(parser.get('A1_bulk_processing','no_thresh_bump_percentiles')),
        "ws": full_string_to_int_list(parser.get('A1_bulk_processing','ws_thresh_bump_percentiles')),
        "wd": full_string_to_int_list(parser.get('A1_bulk_processing','wd_thresh_bump_percentiles'))
    }
    thresh_bump_crits = {
        "no2": False,
        "wcpc": False,
        "o3": False,
        "co": False,
        "co2": False,
        "no": False,
        "ws": False,
        "wd": False
    }
    for i in thresh_bump_crits:
        if all_A1_thresh_bump_percentiles[i][-1] == '*':
            thresh_bump_crits[i] = True
            del all_A1_thresh_bump_percentiles[i][-1]
    for i in all_A1_thresh_bump_percentiles:
        if (len(all_A1_thresh_bump_percentiles[i]) > max_entries):
            max_entries = len(all_A1_thresh_bump_percentiles[i])




    #filling in smaller bulk settings to meet max entries length
    for i in all_A1_coeffs:
        all_A1_coeffs[i] = fill_smaller_bulk(all_A1_coeffs[i],max_entries)

    for i in all_A1_percentiles:
        all_A1_percentiles[i] = fill_smaller_bulk(all_A1_percentiles[i],max_entries)

    for i in all_A1_thresh_bump_percentiles:
        all_A1_thresh_bump_percentiles[i] = fill_smaller_bulk(all_A1_thresh_bump_percentiles[i],max_entries)

    filename_no_extension = ''
    for i in range(0, len(output_csv)):
        if output_csv[(i):(i + 4)].lower() == '.csv':
            filename_no_extension = output_csv[0:i]

    #handling output names based on crit settings or if no crit settings are selected
    contains_crits = False
    for i in coeff_crits:
        if coeff_crits[i] == True:
            contains_crits = True
            break
        if percentile_crits[i] == True:
            contains_crits = True
            break
        if thresh_bump_crits[i] == True:
            contains_crits = True
            break

    output_names = []

    if contains_crits:
        for i in range(0,max_entries):
            working_output = filename_no_extension

            for x in coeff_crits:
                if coeff_crits[x]:
                    working_output+=', '+str(x)+'_coeff='+str(all_A1_coeffs[x][i])

            for x in percentile_crits:
                if percentile_crits[x]:
                    working_output+=', '+str(x)+'_percentile='+str(all_A1_percentiles[x][i])

            for x in thresh_bump_crits:
                if thresh_bump_crits[x]:
                    working_output+=', '+str(x)+'_thresh_bump_percentile='+str(all_A1_thresh_bump_percentiles[x][i])

            output_names.append(working_output+'.csv')
    else:
        for i in range(1, max_entries+1):
            output_names.append(filename_no_extension+'-'+str(i)+'.csv')

    #making sure none of the filenames exceed windows
    for i in output_names:
        if len(i)>255:
            sys.exit('ERROR: output filenames will be '+str(len(i))+' characters long, thus exceeding the windows limit of 255 characters. Please choose less critical settings')

base_thresh_only = False #manual override
limit_thresh = False #manual override

#grabbing more misc settings and defining trace length
A1_startup_bypass = parser.getint('A1_misc','startup_bypass')
queue_size = parser.getint('A1_misc', 'chunk_size')
trace_length = 60

#handling output csv and which columns it should contain
col_names = ["Row","Time", "NO2 (ppb)", "WCPC (#/cm^3)", "O3 (ppb)", "CO (ppb)", "CO2 (ppm)",'NO (ppb)','WS (m/s)','WD (degrees)']
output_cols = ["Row","Time", "NO2 (ppb)", "WCPC (#/cm^3)", "O3 (ppb)", "CO (ppb)", "CO2 (ppm)",'NO (ppb)','WS (m/s)','WD (degrees)',"","NO2 peak (ppb)"]
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
output_cols.append('WS peak (m/s)')
if A1_thresh_dump['ws']:
    output_cols.append('WS thresh')
output_cols.append('WD peak (degrees)')
if A1_thresh_dump['wd']:
    output_cols.append('WD thresh')

#handling settings in output settings

settings_in_output = {
    'coeff': False,
    'percentile': False,
    'thresh_bump_percentile': False,
    'misc': False
}

#defining traces
traces = dict(
    no2=deque([], maxlen=trace_length),
    wcpc=deque([], maxlen=trace_length),
    o3=deque([], maxlen=trace_length),
    co=deque([], maxlen=trace_length),
    co2=deque([], maxlen=trace_length),
    no=deque([], maxlen=trace_length),
    ws=deque([], maxlen=trace_length),
    wd=deque([], maxlen=trace_length)
)

#global counting variables
A1_n = {
    "no2": 0,
    "wcpc": 0,
    "o3": 0,
    "co": 0,
    "co2": 0,
    "no": 0,
    "ws": 0,
    "wd": 0
}
current_chunk=0

#print warning
print("NOTE: this script can sometimes take quite some time to run (typically about 10 seconds for every 5000 rows depending on the user's computer)")
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



if bulk_processing == False:
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
        ws_list = data['WS (m/s)'].to_list()
        wd_list = data['WD (degrees)'].to_list()
        row_list = data["Row"].to_list()
        time_list = data["Time"].to_list()

        #create thresh lists
        thresh_dict = {
            'no2': [],
            'wcpc': [],
            'o3': [],
            'co': [],
            'co2': [],
            'no': [],
            'ws': [],
            'wd': []
        }

        # compute peaks for current chunk and save as it's own list
        no2_peaks = compute_peak_list(no2_list,'no2')
        wcpc_peaks = compute_peak_list(wcpc_list,'wcpc')
        o3_peaks = compute_peak_list(o3_list,'o3')
        co_peaks = compute_peak_list(co_list,'co')
        co2_peaks = compute_peak_list(co2_list,'co2')
        no_peaks = compute_peak_list(no_list,'no')
        ws_peaks = compute_peak_list(ws_list, 'ws')
        wd_peaks = compute_peak_list(wd_list, 'wd')

        #limiting thresh if necessary
        if limit_thresh:
            maxes_dict = {
                'no2': (max(no2_list)),
                'wcpc': (max(wcpc_list)),
                'o3': (max(o3_list)),
                'co': (max(co_list)),
                'co2': (max(co2_list)),
                'no': (max(no_list)),
                'ws': (max(ws_list)),
                'wd': (max(wd_list))
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

                #writing settings to output file
                if settings_in_output['coeff']:
                    w.writerow(['[A1_coeff]'])
                    for i in A1_coeff:
                        w.writerow([i+': ',A1_coeff[i]])
                    w.writerow(['',''])

                if settings_in_output['percentile']:
                    w.writerow(['[A1_percentile]'])
                    for i in A1_percentile:
                        w.writerow([i+': ',A1_percentile[i]])
                    w.writerow(['',''])

                if settings_in_output['thresh_bump_percentile']:
                    w.writerow(['[A1_thresh_bump_percentile]'])
                    for i in A1_thresh_bump_percentile:
                        w.writerow([i+': ',A1_thresh_bump_percentile[i]])
                    w.writerow(['',''])

                if settings_in_output['misc']:
                    w.writerow(['startup_bypass: ', A1_startup_bypass])
                    w.writerow(['chunk_size: ', queue_size])
                    w.writerow(['',''])


                w.writerow(output_cols)

            #write data to CSV
            for i in range(0, len(row_list)):
                row = [row_list[i], time_list[i], no2_list[i], wcpc_list[i], o3_list[i], co_list[i], co2_list[i], no_list[i], ws_list[i], wd_list[i], "", no2_peaks[i]]

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

                row.append(ws_peaks[i])
                if A1_thresh_dump['ws']:
                    row.append(thresh_dict['ws'][i])

                row.append(wd_peaks[i])
                if A1_thresh_dump['wd']:
                    row.append(thresh_dict['wd'][i])

                w.writerow(row)

        # break loop if we're on the last chunk, otherwise go to next chunk
        if len(no2_list) < queue_size:
            print("chunk " + str(current_chunk + 1) + " written")
            break
        else:
            print("chunk " + str(current_chunk + 1) + " written")
            current_chunk += 1
else:
    print('Bulk processing ENABLED')
    for i in range(0,max_entries):

        print('\nComputing peaks ' + str(i + 1) + ' of ' + str(max_entries))

        #reseting all counters
        traces = dict(
            no2=deque([], maxlen=trace_length),
            wcpc=deque([], maxlen=trace_length),
            o3=deque([], maxlen=trace_length),
            co=deque([], maxlen=trace_length),
            co2=deque([], maxlen=trace_length),
            no=deque([], maxlen=trace_length),
            ws=deque([], maxlen=trace_length),
            wd=deque([], maxlen=trace_length)
        )
        A1_n = {
            "no2": 0,
            "wcpc": 0,
            "o3": 0,
            "co": 0,
            "co2": 0,
            "no": 0,
            "ws": 0,
            "wd": 0
        }
        current_chunk = 0

        #grabbing settings for this run
        A1_coeff = {
            "no2": all_A1_coeffs['no2'][i],
            "wcpc": all_A1_coeffs['wcpc'][i],
            "o3": all_A1_coeffs['o3'][i],
            "co": all_A1_coeffs['co'][i],
            "co2": all_A1_coeffs['co2'][i],
            "no": all_A1_coeffs['no'][i],
            "ws": all_A1_coeffs['ws'][i],
            "wd": all_A1_coeffs['wd'][i]
        }
        A1_percentile = {
            "no2": all_A1_percentiles['no2'][i],
            "wcpc": all_A1_percentiles['wcpc'][i],
            "o3": all_A1_percentiles['o3'][i],
            "co": all_A1_percentiles['co'][i],
            "co2": all_A1_percentiles['co2'][i],
            "no": all_A1_percentiles['no'][i],
            "ws": all_A1_percentiles['ws'][i],
            "wd": all_A1_percentiles['wd'][i]
        }
        A1_thresh_bump_percentile = {
            "no2": all_A1_thresh_bump_percentiles['no2'][i],
            "wcpc": all_A1_thresh_bump_percentiles['wcpc'][i],
            "o3": all_A1_thresh_bump_percentiles['o3'][i],
            "co": all_A1_thresh_bump_percentiles['co'][i],
            "co2": all_A1_thresh_bump_percentiles['co2'][i],
            "no": all_A1_thresh_bump_percentiles['no'][i],
            "ws": all_A1_thresh_bump_percentiles['ws'][i],
            "wd": all_A1_thresh_bump_percentiles['wd'][i]
        }
        output_csv=output_names[i]





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
            ws_list = data['WS (m/s)'].to_list()
            wd_list = data['WD (degrees)'].to_list()
            row_list = data["Row"].to_list()
            time_list = data["Time"].to_list()

            # create thresh lists
            thresh_dict = {
                'no2': [],
                'wcpc': [],
                'o3': [],
                'co': [],
                'co2': [],
                'no': [],
                'ws': [],
                'wd': []
            }

            # compute peaks for current chunk and save as it's own list
            no2_peaks = compute_peak_list(no2_list, 'no2')
            wcpc_peaks = compute_peak_list(wcpc_list, 'wcpc')
            o3_peaks = compute_peak_list(o3_list, 'o3')
            co_peaks = compute_peak_list(co_list, 'co')
            co2_peaks = compute_peak_list(co2_list, 'co2')
            no_peaks = compute_peak_list(no_list, 'no')
            ws_peaks = compute_peak_list(ws_list, 'ws')
            wd_peaks = compute_peak_list(wd_list, 'wd')

            # limiting thresh if necessary
            if limit_thresh:
                maxes_dict = {
                    'no2': (max(no2_list)),
                    'wcpc': (max(wcpc_list)),
                    'o3': (max(o3_list)),
                    'co': (max(co_list)),
                    'co2': (max(co2_list)),
                    'no': (max(no_list)),
                    'ws': (max(ws_list)),
                    'wd': (max(wd_list))
                }
                for pollutant in thresh_dict:
                    for i in range(0, len(thresh_dict[pollutant])):
                        if thresh_dict[pollutant][i] > maxes_dict[pollutant]:
                            thresh_dict[pollutant][i] = maxes_dict[pollutant]

            # write current chunk to CSV
            with open(output_csv, "a", newline='') as f:
                w = csv.writer(f)

                # write headers if we're on the first chunk
                if current_chunk == 0:

                    # writing settings to output file
                    if settings_in_output['coeff']:
                        w.writerow(['[A1_coeff]'])
                        for i in A1_coeff:
                            w.writerow([i + ': ', A1_coeff[i]])
                        w.writerow(['', ''])

                    if settings_in_output['percentile']:
                        w.writerow(['[A1_percentile]'])
                        for i in A1_percentile:
                            w.writerow([i + ': ', A1_percentile[i]])
                        w.writerow(['', ''])

                    if settings_in_output['thresh_bump_percentile']:
                        w.writerow(['[A1_thresh_bump_percentile]'])
                        for i in A1_thresh_bump_percentile:
                            w.writerow([i + ': ', A1_thresh_bump_percentile[i]])
                        w.writerow(['', ''])

                    if settings_in_output['misc']:
                        w.writerow(['startup_bypass: ', A1_startup_bypass])
                        w.writerow(['chunk_size: ', queue_size])
                        w.writerow(['', ''])

                    w.writerow(output_cols)

                # write data to CSV
                for i in range(0, len(row_list)):
                    row = [row_list[i], time_list[i], no2_list[i], wcpc_list[i], o3_list[i], co_list[i], co2_list[i],
                           no_list[i], ws_list[i], wd_list[i], "", no2_peaks[i]]

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

                    row.append(ws_peaks[i])
                    if A1_thresh_dump['ws']:
                        row.append(thresh_dict['ws'][i])

                    row.append(wd_peaks[i])
                    if A1_thresh_dump['wd']:
                        row.append(thresh_dict['wd'][i])

                    w.writerow(row)

            # break loop if we're on the last chunk, otherwise go to next chunk
            if len(no2_list) < queue_size:
                print("chunk " + str(current_chunk + 1) + " written")
                break
            else:
                print("chunk " + str(current_chunk + 1) + " written")
                current_chunk += 1