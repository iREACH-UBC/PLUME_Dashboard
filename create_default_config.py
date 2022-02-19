from configparser import ConfigParser

config = ConfigParser(allow_no_value=True)



#live plot y-range settings
config['y-ranges'] = {
    'y ranges of the live plots can be specified for each pollutant here. use a comma to seperate the lower and upper bounds\n'
    'NO2': '0,80',
    'WCPC': '7000,10000',
    'O3': '0,100',
    'CO': '0,100',
    'CO2': '0,100',
    'NO': '0,100'
}

#command char
'''config['command_char'] = {
    'choose ONE character to use as the command character. this will indicate to the main script when a command is being ran\n'
    'command_character':'*'
}'''

#log files directory
config['log_directory'] = {
    'specify the directory for the dashboard to create the event markers and sensor transcript csv files in\n'
    'log_files_path':'C:/Users/Chris/Sync/iREACH/Students/Chris/Test1'
}

#misc, including algorithm circuit breaker
config['algorithm_circuit_breaker'] = {
    'A1 and AQ can be enabled or disabled for all pollutants here. enter \'true\' to enable or \'false\' to disable\n'
    'A1_on': 'true',
    'AQ_on': 'true',
}

#data setting
config['real_or_simulated'] = {
    'specify whether to use real or simulated data for each pollutant below. enter \'real\' to use real data from Redis or \'simulated\' to use simulated data. if simulated data is being used, it will override incoming pollutant data from Redis, however it will still use time data from Redis, thus Redis must still be running. enter the directory and filename of the simulated data. the files must be .xlxs spreadsheets\n'
    'NO2': 'simulated',
    'WCPC': 'real',
    'O3': 'real',
    'CO': 'real',
    'CO2': 'real',
    'NO': 'real',
    'sim_data_path': 'C:/Users/Chris/Sync/iREACH/Students/Chris/SIMULATED_DATA/',
    'sim_NO2_filename': 'NO2_12s.xlsx',
    'sim_WCPC_filename': 'WCPC.csv',
    'sim_O3_filename': 'O3.csv',
    'sim_CO_filename': 'CO.csv',
    'sim_CO2_filename': 'CO2.csv',
    'sim_NO_filename': 'NO.csv'

}

#A1 settings
config['A1_coeff'] = {
    'which A1_coeff to use for each pollutant can be specified here. these settings will be used by the real time a1 and post processing a1\n'
    'NO2': '15',
    'WCPC': '3',
    'O3': '3',
    'CO': '3',
    'CO2': '3',
    'NO': '3'
}
config['A1_percentile'] = {
    'which a1 \'n\' percentile to be used for each pollutant can be specified here. these settings will be used by the real time a1 and post processing a1\n'
    'NO2': '50',
    'WCPC': '50',
    'O3': '50',
    'CO': '50',
    'CO2': '50',
    'NO': '50'
}
config['A1_thresh_bump_percentile'] = {
    'which a1 \'m\' percentile to be used for each pollutant can be specifed here. enter a \'0\' to disable this and thus remove the bm term from the threshold calculation. these settings will be used by the real time a1 and post processing a1\n'
    'NO2': '1',
    'WCPC': '1',
    'O3': '1',
    'CO': '1',
    'CO2': '1',
    'NO': '1'} #set to 0 to disable

config['A1_misc'] = {
    'miscellaneous settings of a1 can be specified here. startup_bypass is the mininum length that the pollutant dequeus must reach until a1 becomes enabled\n'
    'startup_bypass': '30',
    'folder_directory': 'C:/Users/Chris/Sync/iREACH/Students/Chris/PEAK/',
    'input_filename': 'IN.csv',
    'output_filename': 'OUT.csv',
    'chunk_size': '3000'

}
config['A1_post_processing_thresh_dump'] = {
    'specify whether or not the threshold should be included in the post processing a1 output csv for each pollutant. enter \'true\' to enable or \'false\' to disable\n'
    'NO2': 'true',
    'WCPC': 'false',
    'O3': 'false',
    'CO': 'false',
    'CO2': 'false',
    'NO': 'false'
}

#AQ setting
config['AQ_thresh'] = {
    'the flat AQ warning threshold can be set for each pollutant here\n'
    'NO2': '40',
    'WCPC': '100',
    'O3': '100',
    'CO': '100',
    'CO2': '100',
    'NO': '100'}

#baseline settings
config['baseline'] ={
    'settings of the baseline calculation algorithm can be specified here\n'
    'window_size': '6',
    'smoothing_index': '25',
    'chunk_size': '3000',
    'folder_directory': 'C:/Users/Chris/Sync/iREACH/Students/Chris/BASELINE/',
    'input_filename': 'IN.csv',
    'output_filename': 'OUT.csv',
    'settings_in_name': 'true'

}

#modbus settings
config['modbus-tcp_settings'] ={
    'parameters of the modbus tcp/ip connection can be set here. these settings will only be read by the modbus-tcp_daq script so they can be left blank if a different daq script is being used. which modbus holding registers to read as well as how many should be read can be set for each pollutant here. typically, for float values, register_length for each pollutant should be set to \'2\'. individual pollutants can be enabled or disabled by entering \'true\' or \'false\'. if a pollutant is disabled, redis will send either a constant value or generate random values for the disabled pollutant(s). set the random_or_flat_if_disabled setting to \'random\' to use random values or \'flat\' to use flat values\n'
    'ip_address': '169.254.67.85',
    'port': '502',
    'enable_no2': 'false',
    'no2_modbus_hr': '5',
    'no2_hr_length': '2',
    'enable_wcpc': 'false',
    'wcpc_modbus_hr': '',
    'wcpc_hr_length': '',
    'enable_o3': 'false',
    'o3_modbus_hr': '0',
    'o3_hr_length': '2',
    'enable_co': 'false',
    'co_modbus_hr': '7',
    'co_hr_length': '2',
    'enable_co2': 'false',
    'co2_modbus_hr': '',
    'co2_hr_length': '2',
    'enable_no': 'false',
    'no_modbus_hr': '3',
    'no_hr_length': '2',
}

################
# 'is_formatted': 'false',
# 'columns_with_data': '3,7'
################


with open('./user_defined_settings.ini', 'w') as f:
    config.write(f)