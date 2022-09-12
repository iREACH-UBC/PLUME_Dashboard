"""
Run this script to create a new 'user_defined_settings.ini' file with the default settings.

WARNING: Running this script will overwrite the current 'user_defined_settings.ini' file if one exists.
"""


from configparser import ConfigParser

config = ConfigParser(allow_no_value=True)



###################################################################################################################



#live plot y-range settings
config['y-ranges'] = {
    'NO2': '0,100',
    'WCPC': '0,15000',
    'O3': '0,100',
    'CO': '0,700',
    'CO2': '0,700',
    'NO': '0,80',
    'WS': '0,20',
    'WD': '0,360',
    'as_NO2':'false',
    'as_WCPC':'false',
    'as_O3':'false',
    'as_CO':'false',
    'as_CO2':'false',
    'as_NO':'false',
    'as_WS':'false',
    'as_WD':'false',
}

#log files directory
config['log_directory'] = {
    'log_files_path':''
}

#GPS merge data settings
config['GPS_merge_data'] = {
    'folder_path': '',
    'gpx_filename': 'gps_data.gpx',
    'csv_filename': 'pollutant_data.csv',
    'output_filename': 'MERGED.csv',
    'no2_lag': '40',
    'wcpc_lag': '5',
    'o3_lag': '40',
    'co_lag': '40',
    'co2_lag': '40',
    'no_lag': '40',
    'start_time': '',
    'end_time': ''
}

#A1 and AQ toggle
config['algorithm_circuit_breaker'] = {
    'A1_on': 'true',
    'AQ_on': 'true',
}

#wdrw settings
config['wind_direction_range_warning'] = {
    'enable_wdrw': 'true',
    'range': '170,200'
}

#data settings
config['real_or_simulated'] = {
    'NO2': 'real',
    'WCPC': 'real',
    'O3': 'real',
    'CO': 'real',
    'CO2': 'real',
    'NO': 'real',
    'WS': 'real',
    'WD': 'real',
    'sim_data_path': '',
    'sim_NO2_filename': 'NO2_sim.csv',
    'sim_WCPC_filename': 'WCPC_sim.csv',
    'sim_O3_filename': 'O3_sim.csv',
    'sim_CO_filename': 'CO_sim.csv',
    'sim_CO2_filename': 'CO2_sim.csv',
    'sim_NO_filename': 'NO_sim.csv',
    'sim_WS_filename': 'WS_sim.csv',
    'sim_WD_filename': 'WD_sim.csv'

}

#A1 coeff settings
config['A1_coeff'] = {
    'NO2': '15',
    'WCPC': '15',
    'O3': '15',
    'CO': '15',
    'CO2': '15',
    'NO': '15',
    'WS': '15',
    'WD': '15'
}

#A1 percentile settings
config['A1_percentile'] = {
    'NO2': '50',
    'WCPC': '50',
    'O3': '50',
    'CO': '50',
    'CO2': '50',
    'NO': '50',
    'WS': '50',
    'WD': '50'
}

#A1 thresh bump percentile settings
config['A1_thresh_bump_percentile'] = {
    'NO2': '1',
    'WCPC': '1',
    'O3': '1',
    'CO': '1',
    'CO2': '1',
    'NO': '1',
    'WS': '1',
    'WD': '1'} #set to 0 to disable

#misc settings for A1
config['A1_misc'] = {
    'startup_bypass': '30',
    'folder_directory': '',
    'input_filename': 'IN.csv',
    'output_filename': 'OUT.csv',
    'chunk_size': '3000',
}

#PP_A1 thresh dump settings
config['A1_post_processing_thresh_dump'] = {
    'NO2': 'true',
    'WCPC': 'true',
    'O3': 'true',
    'CO': 'true',
    'CO2': 'true',
    'NO': 'true',
    'WS': 'true',
    'WD': 'true'
}

#AQ thresh settings
config['AQ_thresh'] = {
    'NO2': '25',
    'WCPC': '5000',
    'O3': '62',
    'CO': '9',
    'CO2': '800',
    'NO': '100',
    'WS': '1'}

#baseline settings
config['baseline'] ={
    'window_size': '3',
    'smoothing_index': '5',
    'chunk_size': '3000',
    'interlace_chunks':'true',
    'folder_directory': '',
    'input_filename': 'IN.csv',
    'output_filename': 'OUT.csv',
    'settings_in_name': 'true',
}

#baseline bulk processing
config['baseline_bulk_processing'] = {
    'enable_bulk_processing': 'false',
    'window_sizes': '3,3,4',
    'smoothing_indexes': '7,15,25,30'
}

#PPA1 bulk processing
config['A1_bulk_processing'] = {
    'enable_bulk_processing': 'false',
    'no2_coeffs': '10,25',
    'no2_percentiles':'50',
    'no2_thresh_bump_percentiles':'1',
    'wcpc_coeffs': '10,25',
    'wcpc_percentiles':'50',
    'wcpc_thresh_bump_percentiles':'1',
    'o3_coeffs': '10,25',
    'o3_percentiles':'50',
    'o3_thresh_bump_percentiles':'1',
    'co_coeffs': '10,25',
    'co_percentiles':'50',
    'co_thresh_bump_percentiles':'1',
    'co2_coeffs': '10,25',
    'co2_percentiles':'50',
    'co2_thresh_bump_percentiles':'1',
    'no_coeffs': '10,25',
    'no_percentiles':'50',
    'no_thresh_bump_percentiles':'1',
    'ws_coeffs': '10,25',
    'ws_percentiles':'50',
    'ws_thresh_bump_percentiles':'1',
    'wd_coeffs': '10,25',
    'wd_percentiles':'50',
    'wd_thresh_bump_percentiles':'1'
}

#modbus settings
config['modbus-tcp'] ={
    'ip_address': '',
    'port': '502',
    'enable_no2': 'true',
    'no2_modbus_hr': '',
    'no2_hr_length': '2',
    'enable_wcpc': 'true',
    'wcpc_modbus_hr': '',
    'wcpc_hr_length': '2',
    'enable_o3': 'true',
    'o3_modbus_hr': '',
    'o3_hr_length': '2',
    'enable_co': 'true',
    'co_modbus_hr': '',
    'co_hr_length': '2',
    'enable_co2': 'true',
    'co2_modbus_hr': '',
    'co2_hr_length': '2',
    'enable_no': 'true',
    'no_modbus_hr': '',
    'no_hr_length': '2',
    'enable_ws': 'true',
    'ws_modbus_hr': '',
    'ws_hr_length': '2',
    'enable_wd': 'true',
    'wd_modbus_hr': '',
    'wd_hr_length': '2',
}

'''
config['modbus-tcp'] ={
    'ip_address': '169.254.67.85',
    'port': '502',
    'enable_no2': 'false',
    'no2_modbus_hr': '5',
    'no2_hr_length': '2',
    'enable_wcpc': 'false',
    'wcpc_modbus_hr': '11',
    'wcpc_hr_length': '2',
    'enable_o3': 'false',
    'o3_modbus_hr': '0',
    'o3_hr_length': '2',
    'enable_co': 'false',
    'co_modbus_hr': '9',
    'co_hr_length': '2',
    'enable_co2': 'false',
    'co2_modbus_hr': '7',
    'co2_hr_length': '2',
    'enable_no': 'false',
    'no_modbus_hr': '3',
    'no_hr_length': '2',
    'enable_ws': 'false',
    'ws_modbus_hr': '15',
    'ws_hr_length': '2',
    'enable_wd': 'false',
    'wd_modbus_hr': '13',
    'wd_hr_length': '2',
}
'''









####################################################################################################################




with open('./user_defined_settings.ini', 'w') as f:
    config.write(f)