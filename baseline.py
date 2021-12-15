"""
To use this script, place a sensor transcript/readout CSV file in the 'BASELINE' folder, rename the file to 'IN.csv' and
then run this script. It MUST be places in the 'BASELINE' folder and MUST be named 'IN.csv' exactly

If smoothing = 1, the program will make one pass through the data
If smoothing > 1, the program will make multiple passes through the data (each with different interval size) and take
the average of ALL of the calculated baseline lists
"""



import math
import csv

import numpy as np
import pandas as pd
from collections import deque
from configparser import ConfigParser

def string_to_list_interval(string_in):

    #define vars
    comma_index = 0
    lower=""
    upper=""
    result=[]

    #append to lower until comma is found
    for i in range(0,len(string_in)):
        if string_in[i] == ",":
            comma_index=i
            break
        else:
            lower+=string_in[i]

    #append to upper until end of string, starting from first index after comma
    for i in range(comma_index+1,len(string_in)):
        upper+=string_in[i]

    #return result as list
    result.append(int(lower))
    result.append(int(upper))
    return result

####################################### GLOBAL SETTINGS #######################################
parser = ConfigParser(allow_no_value=True)
parser.read('user_defined_settings.ini')

setting_window_size = parser.getint('baseline', 'window_size')
setting_smoothing = parser.getint('baseline', 'smoothing_index')
queue_size = parser.getint('baseline', 'chunk_size') #effectively "chunk size"
#is_formatted = parser.getboolean('baseline', 'is_formatted')
is_formatted = True #manual override
#col_interval = string_to_list_interval(parser.get('baseline','columns_with_data'))
#col_interval[0] -= 1

directory = parser.get('baseline', 'folder_directory')
if (directory[-1] != '/'):
    directory += '/'
filename = directory+(parser.get('baseline','input_filename'))
output_csv = directory+(parser.get('baseline','output_filename'))

col_names = ["Row","Time", "NO2 (ppb)", "WCPC (#/cm^3)", "O3 (ppb)", "CO (ppb)", "CO2 (ppm)",'NO (ppb)']
output_cols = ["Row","Time", "NO2 (ppb)", "WCPC (#/cm^3)", "O3 (ppb)", "CO (ppb)", "CO2 (ppm)",'NO (ppb)',"","NO2 baseline (ppb)", "WCPC baseline (#/cm^3)", "O3 baseline (ppb)", "CO baseline (ppb)", "CO2 baseline (ppm)",'NO baseline (ppb)']

current_chunk = 0 #global counter, DO NOT CHANGE, KEEP IT SET AT 0
###############################################################################################





#helper function to interpolate the "-" characters into numbers
def interpolate(input_pass):
    pair = deque([input_pass[0]], maxlen=2)
    dashes_between = 0

    for i in range(1,len(input_pass)):
        if type(input_pass[i]) == int or type(input_pass[i]) == float:

            #bring in the next number
            pair.append(input_pass[i])



            #compute slope increment
            slope = (pair[1] - pair[0]) / (dashes_between+1)

            #fill values
            inc = 1
            for f in range(i-dashes_between, i):
                input_pass[f] = round( (input_pass[i - dashes_between - 1 ] + (inc * slope)),2 )
                inc += 1


            dashes_between = 0
        else:
            dashes_between += 1

    return input_pass

#helper function to make our passes the same length of data_chunk
def fill_trailing_data(input_pass, data_chunk):
    while len(input_pass) < (len(data_chunk) - 1):
        input_pass.append("-")
    if len(input_pass) == (len(data_chunk) - 1):
        input_pass.append(data_chunk[-1])
    else:
        input_pass[-1] = data_chunk[-1]
    return input_pass

#helper function to compute our baseline assuming smoothing index = 1
def compute_baseline_no_smoothing(data_chunk, window_size):

    #lists storing each pass, these will be averaged out later
    pass1=[data_chunk[0]]
    pass2=[data_chunk[0]]
    pass3=[data_chunk[0]]

    #iterate through current data_chunk, starting at SECOND division of interval and iterating one interval at a time
    for i in range(window_size, len(data_chunk), window_size):
        working_window = data_chunk[(i-window_size+1):(i+1)]
        window_min = min(working_window)
        window_min_index = working_window.index(window_min)
        working_window = ["-"]*window_size
        working_window[window_min_index] = window_min
        pass1+=working_window
    #calling fill_trailing_data function to add trailing data to pass1
    pass1 = fill_trailing_data(pass1, data_chunk)


    #defining our offset and adding "-" characters to the start of passes 2 and 3
    offset = math.floor(window_size/3)
    for i in range(0,(offset)):
        pass2.append("-")
    for i in range(0,(offset*2)):
        pass3.append("-")

    #repeating the same process for passes 2 and 3, with an offset in start window
    for i in range(window_size + offset, len(data_chunk), window_size):
        working_window = data_chunk[(i-window_size+1):(i+1)]
        window_min = min(working_window)
        window_min_index = working_window.index(window_min)
        working_window = ["-"]*window_size
        working_window[window_min_index] = window_min
        pass2+=working_window
    pass2 = fill_trailing_data(pass2, data_chunk)
    for i in range(window_size + (2*offset), len(data_chunk), window_size):
        working_window = data_chunk[(i-window_size+1):(i+1)]
        window_min = min(working_window)
        window_min_index = working_window.index(window_min)
        working_window = ["-"]*window_size
        working_window[window_min_index] = window_min
        pass3+=working_window
    pass3 = fill_trailing_data(pass3, data_chunk)


    #call the interpolate function for each of the passes
    pass1 = interpolate(pass1)
    pass2 = interpolate(pass2)
    pass3 = interpolate(pass3)

    average_of_passes=[]

    for i in range(0,len(pass1)):
        average_of_passes.append  ( round(    ( (pass1[i] + pass2[i] + pass3[i]) / 3.0 ),3 ))


    #special_return = [[pass1],[pass2],[pass3],[average_of_passes]] #for debugging purposes
    #return special_return

    return average_of_passes

#function that computes the final baseline, uses all of the above helper functions
def compute_baseline(data_chunk, window_size, smoothing):
    output_list = compute_baseline_no_smoothing(data_chunk, window_size)

    if smoothing > 1:
        for i in range(2, smoothing+1):
            average_with = compute_baseline_no_smoothing(data_chunk, window_size*i)
            for f in range(0,len(output_list)):
                output_list[f] = (output_list[f] + average_with[f])/2.0

    #set all values to actual if the baseline value is above actual and round to 6 places
    for i in range(0, len(output_list)):
        if output_list[i] > data_chunk[i]:
            output_list[i] = data_chunk[i]
        output_list[i] = round(output_list[i],6)

    return output_list

if (is_formatted == True): #this is the code to use, the else part is not working
    while True:
        #read in the current chunk
        data = pd.read_csv(filename, names=col_names, skiprows=(1 + current_chunk * queue_size), nrows=queue_size)

        #convert current chunk to lists
        no2_list = data["NO2 (ppb)"].to_list()
        wcpc_list = data["WCPC (#/cm^3)"].to_list()
        o3_list = data["O3 (ppb)"].to_list()
        co_list = data["CO (ppb)"].to_list()
        co2_list = data["CO2 (ppm)"].to_list()
        no_list = data['NO (ppb)'].to_list()
        row_list = data["Row"].to_list()
        time_list = data["Time"].to_list()

        #compute baseline for current chunk and save as it's own list
        no2_baseline = compute_baseline(no2_list,setting_window_size,setting_smoothing)
        wcpc_baseline = compute_baseline(wcpc_list, setting_window_size, setting_smoothing)
        o3_baseline = compute_baseline(o3_list, setting_window_size, setting_smoothing)
        co_baseline = compute_baseline(co_list, setting_window_size, setting_smoothing)
        co2_baseline = compute_baseline(co2_list, setting_window_size, setting_smoothing)
        no_baseline = compute_baseline(no_list, setting_window_size, setting_smoothing)

        with open(output_csv,"a",newline='') as f:
            w = csv.writer(f)

            if current_chunk == 0:
                w.writerow(output_cols)

            for i in range(0,len(row_list)):
                w.writerow([row_list[i], time_list[i], no2_list[i], wcpc_list[i], o3_list[i], co_list[i], co2_list[i], no_list[i],"", no2_baseline[i], wcpc_baseline[i], o3_baseline[i], co_baseline[i], co2_baseline[i],no_baseline[i] ])

        # break loop if we're on the last chunk, otherwise go to next chunk
        if len(no2_list) < queue_size:
            print("chunk "+str(current_chunk+1)+" written")
            break
        else:
            print("chunk "+str(current_chunk+1)+" written")
            current_chunk += 1
else:
    #populate col_names
    pandas_col_names = pd.read_csv(filename, nrows=1, header=0)
    col_names = list(pandas_col_names.columns)
    # non_data_leading_cols = col_names[0:(col_interval[0]+1)]
    col_names = col_names[(col_interval[0]):(col_interval[1])]
    for i in range(0,len(col_names)):
        col_names[i] = str(col_names[i])

    #populate output cols
    output_cols = []
    for i in col_names:
        output_cols.append(i)
    output_cols.append('')
    for i in col_names:
        output_cols.append(i+' baseline')

    while True:
        # read in the current chunk
        data = pd.read_csv(filename, names=col_names, skiprows=(1 + current_chunk * queue_size), nrows=queue_size)

        # convert current chunk to matrix
        in_mat=[]
        for i in col_names:
            in_mat.append(data[i].to_list())

        #calculate baseline and save as matrix
        out_mat = []
        for i in range(0,len(in_mat)):
            out_mat.append(compute_baseline(in_mat[i], setting_window_size, setting_smoothing))

        #transpose in_mat and out_mat so each entry is a row to be written
        arr = np.array(out_mat)
        arr = arr.transpose()
        out_mat = arr.tolist()
        arr = np.array(in_mat)
        arr = arr.transpose()
        in_mat = arr.tolist()

        #write chunk to CSV
        with open(output_csv, "a", newline='') as f:
            w = csv.writer(f)

            if current_chunk == 0:
                w.writerow(output_cols)

            for i in range(0, len(out_mat)):
                current_row=[]
                for a in in_mat[i]:
                    current_row.append(a)
                current_row.append('')
                for a in out_mat[i]:
                    current_row.append(a)
                w.writerow(current_row)

        # break loop if we're on the last chunk, otherwise go to next chunk
        if len(out_mat) < queue_size:
            print("chunk " + str(current_chunk + 1) + " written")
            break
        else:
            print("chunk " + str(current_chunk + 1) + " written")
            current_chunk += 1


