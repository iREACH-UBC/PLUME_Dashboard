import pandas as pd
import csv
from datetime import datetime
from dateutil import tz
from dateutil.relativedelta import relativedelta
import re
import numpy as np
from configparser import ConfigParser
import os

parser = ConfigParser(allow_no_value=True)
parser.read('user_defined_settings.ini')


directory = parser.get('GPS_merge_data', 'folder_directory')
if (directory[-1] != '/'):
    directory += '/'
GPXfile = directory+(parser.get('GPS_merge_data','gpx_input_filename'))
#GPXfile = 'input\GL770.gpx'

CSVinput = directory+(parser.get('GPS_merge_data','sensor_transcript_input_filename'))

output_file = directory+(parser.get('GPS_merge_data','output_filename'))

lags = {
  'no2': abs(parser.getint('GPS_merge_data','no2_lag')),
  'wcpc': abs(parser.getint('GPS_merge_data','wcpc_lag')),
  'o3': abs(parser.getint('GPS_merge_data','o3_lag')),
  'co': abs(parser.getint('GPS_merge_data','co_lag')),
  'co2': abs(parser.getint('GPS_merge_data','co2_lag')),
  'no': abs(parser.getint('GPS_merge_data','no_lag'))
  }

max_lag=0
for pollutant in lags:
  if lags[pollutant] > max_lag:
    max_lag = lags[pollutant]

Dash_start_time = parser.get('GPS_merge_data','dashboard_start_time')
Dash_end_time = parser.get('GPS_merge_data','dashboard_end_time')

Dash_end_time = datetime.strptime(Dash_end_time, "%Y-%m-%d %H:%M:%S")
Dash_end_time = Dash_end_time - relativedelta(seconds=max_lag)
Dash_end_time = Dash_end_time.strftime("%Y-%m-%d %H:%M:%S")




############################################# Code for GL770 GPS #############################################

############### Converting from GPX to csv ###############


data = open(GPXfile).read()

lat = np.array(re.findall(r'lat="([^"]+)', data), dtype = float)
lon = np.array(re.findall(r'lon="([^"]+)', data), dtype = float)
time = re.findall(r'<time>([^\<]+)', data)

combined = np.array(list(zip(lat, lon, time)))
print(combined)

df = pd.DataFrame(combined)
df.columns = ['latitude', 'longitude', 'time']
df.to_csv('aux_files\GL770.csv')

############### Changing from UTC time to Pacific time ###############

with open('aux_files\GL770.csv', 'r') as csv_file:
  csv_reader = csv.DictReader(csv_file)

  times = []

  for col in csv_reader:
    times.append(col['time'])

print('time', times)

from_zone = tz.tzutc()
to_zone = tz.tzlocal()

for i in range(len(times)):
  t = str(times[i]).split(".")[0]
  t = str(t).split("Z")[0]
  utc_dt = datetime.strptime(t, "%Y-%m-%dT%H:%M:%S")
  utc_dt = utc_dt.replace(tzinfo=from_zone)
  pst_dt = utc_dt.astimezone(to_zone)
  times[i] = pst_dt.strftime("%Y-%m-%d %H:%M:%S")

print('time', times)

times.sort()

############### Writing the new times (plus lat and long) back to a csv ###############

all_data = np.array(list(zip(lat, lon, times)))
all_data_df = pd.DataFrame(all_data)
all_data_df.columns = ['latitude', 'longitude', 'time']
all_data_df.to_csv('aux_files\\new_GL770.csv') #Edited/Inserted 29-6-22

############### Convert to datetime so that it can merge with dashboard data ###############

new_GL770 = pd.read_csv('aux_files\\new_GL770.csv') #Edited/Inserted 29-6-22
new_GL770['time'] = pd.to_datetime(new_GL770['time'], errors = 'coerce')

############### Import dashboard data ###############
data_table = pd.read_csv(CSVinput) #Edited/Inserted 29-6-22
data_table.rename(columns={'Time': 'time'}, inplace=True) # Edited/Inserted 29-6-22
data_table['time'] = pd.to_datetime(data_table['time'], errors = 'coerce')

############### Merge dashboard and GL770 GPS data ###############

gl770_data = pd.merge_asof(new_GL770, data_table, on = 'time', direction = 'nearest')

####### Fixing time-lag ####### Edited/Inserted 29-6-22
# For mobile air quality monitoring, one needs to account the lag between air entering the inlet and concentration read by the instruments
# Below one can insert as variables the 'lag time' for each instrument
# What follows can be cut or added for every new pollutant



gl770_data['NO2 (ppb)'] = gl770_data['NO2 (ppb)'].shift((-1)*lags['no2'])  # Finds column with name '...' and shift its values down by a lag. If desired to shift up, include minus sign
gl770_data['O3 (ppb)'] = gl770_data['O3 (ppb)'].shift((-1)*lags['o3'])
gl770_data['CO (ppm)'] = gl770_data['CO (ppm)'].shift((-1)*lags['co'])
gl770_data['NO (ppb)'] = gl770_data['NO (ppb)'].shift((-1)*lags['no'])
gl770_data['CO2 (ppm)'] = gl770_data['CO2 (ppm)'].shift((-1)*lags['co2'])
gl770_data['WCPC (#/cm^3)'] = gl770_data['WCPC (#/cm^3)'].shift((-1)*lags['wcpc'])

#### Cut-off first and last rows of obsolete data #### Edited/Inserted 29-6-22
# Because GPS should be started before running the Dashboard, it will be logging first
# When finding the nearest time to merge the Air Quality Data, the program will keep repeating the first data row form the Dashboard log until the Dash time hits
# Below one can filter the specific time to account both Dash and GPS data


gl770_data = gl770_data[~(gl770_data['time'] < Dash_start_time)]
gl770_data = gl770_data[~(gl770_data['time'] > Dash_end_time)]

############### Export as a csv ###############

gl770_data.to_csv(output_file) #Edited/Inserted 29-6-22

os.remove('aux_files\\new_GL770.csv')
os.remove('aux_files\GL770.csv')

"""
### Garmin GPS stuff comment out for now ### GL770 has better time resolution ###

############################################# Code for Garmin GPS #############################################

############### Converting from GPX to csv ###############

Garmin_GPXfile = 'input\Garmin.gpx'
data = open(Garmin_GPXfile).read()

lat = np.array(re.findall(r'lat="([^"]+)', data), dtype = float)
lon = np.array(re.findall(r'lon="([^"]+)', data), dtype = float)
time = re.findall(r'<time>([^\<]+)', data)

Garmin_combined = np.array(list(zip(lat, lon, time)))
Garmin_df = pd.DataFrame(Garmin_combined)
Garmin_df.columns = ['latitude', 'longitude', 'time']
Garmin_df.to_csv('output\Garmin.csv')

############### putting time column in the correct format ###############

with open('output\Garmin.csv', 'r') as Garmin_csv_file:
  csv_reader = csv.DictReader(Garmin_csv_file)

  Garmin_times = []

  for col in csv_reader:
    Garmin_times.append(col['time'])

del Garmin_times[0]
print(Garmin_times)

for i in range(len(Garmin_times)):
  t = str(Garmin_times[i]).split("-")[0]
  t = str(Garmin_times[i]).split("Z")[0]
  Garmin_dt_times = datetime.strptime(t, "%Y-%m-%dT%H:%M:%S-%f:00")
  Garmin_times[i] = Garmin_dt_times.strftime("%Y-%m-%d %H:%M:%S")

print('time', Garmin_times)

Garmin_times.sort()

############### Writing the new times (plus lat and long) back to a csv ###############

Garmin_all_data = np.array(list(zip(lat, lon, times)))
Garmin_all_data_df = pd.DataFrame(Garmin_all_data)
Garmin_all_data_df.columns = ['latitude', 'longitude', 'time']
Garmin_all_data_df.to_csv('new_Garmin.csv')

############### Convert to datetime so that it can merge with dashboard data ###############

new_Garmin = pd.read_csv('new_Garmin.csv')
new_Garmin['time'] = pd.to_datetime(new_Garmin['time'], errors = 'coerce')

############### Merge dashboard and Garmin GPS data ###############

garmin_data = pd.merge_asof(new_Garmin, data_table, on = 'time', direction = 'nearest')

############### Export as a csv ###############

garmin_data.to_csv('output\Garmin_final.csv')

"""