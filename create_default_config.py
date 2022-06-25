from configparser import ConfigParser

config = ConfigParser(allow_no_value=True)















###################################################################################################################










#live plot y-range settings
config['y-ranges'] = {
    'NO2': '0,150',
    'WCPC': '0,20000',
    'O3': '0,100',
    'CO': '0,20',
    'CO2': '0,1000',
    'NO': '0,150',
    'WS': '0,20',
    'WD': '0,360',
    'enable_autoscale_NO2':'true',
    'enable_autoscale_WCPC':'false',
    'enable_autoscale_O3':'false',
    'enable_autoscale_CO':'false',
    'enable_autoscale_CO2':'false',
    'enable_autoscale_NO':'false',
    'enable_autoscale_WS':'false',
    'enable_autoscale_WD':'false',
    'autoscale_padding_percentage_NO2':'5',
    'autoscale_padding_percentage_WCPC':'5',
    'autoscale_padding_percentage_O3':'5',
    'autoscale_padding_percentage_CO':'5',
    'autoscale_padding_percentage_CO2':'5',
    'autoscale_padding_percentage_NO':'5',
    'autoscale_padding_percentage_WS':'5',
    'autoscale_padding_percentage_WD':'5'
}

#command char
'''config['command_char'] = {
    'choose ONE character to use as the command character. this will indicate to the main script when a command is being ran\n'
    'command_character':'*'
}'''

#log files directory
config['log_directory'] = {
    'specify the directory for the dashboard to create the event markers and sensor transcript csv files in\n'
    'log_files_path':'C:/Users/Chris/Desktop/Dashboard/LOG_FILES'
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
    'WS': 'simulated',
    'WD': 'simulated',
    'sim_data_path': 'C:/Users/Chris/Desktop/Dashboard/SIMULATED_DATA',
    'sim_NO2_filename': 'NO2_sim.csv',
    'sim_WCPC_filename': 'WCPC_fake.xlsx',
    'sim_O3_filename': 'O3_fake.xlsx',
    'sim_CO_filename': 'CO_fake.xlsx',
    'sim_CO2_filename': 'CO2_fake.xlsx',
    'sim_NO_filename': 'NO_fake.xlsx',
    'sim_WS_filename': 'WS_sim.csv',
    'sim_WD_filename': 'WD_sim.csv'

}

#A1 settings
config['A1_coeff'] = {
    'which A1_coeff to use for each pollutant can be specified here. these settings will be used by the real time a1 and post processing a1\n'
    'NO2': '15',
    'WCPC': '15',
    'O3': '15',
    'CO': '15',
    'CO2': '15',
    'NO': '15',
    'WS': '15',
    'WD': '15'
}
config['A1_percentile'] = {
    'which a1 \'n\' percentile to be used for each pollutant can be specified here. these settings will be used by the real time a1 and post processing a1\n'
    'NO2': '50',
    'WCPC': '50',
    'O3': '50',
    'CO': '50',
    'CO2': '50',
    'NO': '50',
    'WS': '50',
    'WD': '50'
}
config['A1_thresh_bump_percentile'] = {
    'which a1 \'m\' percentile to be used for each pollutant can be specifed here. enter a \'0\' to disable this and thus remove the bm term from the threshold calculation. these settings will be used by the real time a1 and post processing a1\n'
    'NO2': '1',
    'WCPC': '1',
    'O3': '1',
    'CO': '1',
    'CO2': '1',
    'NO': '1',
    'WS': '1',
    'WD': '1'} #set to 0 to disable

config['A1_misc'] = {
    'miscellaneous settings of a1 can be specified here. startup_bypass is the mininum length that the pollutant dequeus must reach until a1 becomes enabled\n'
    'startup_bypass': '30',
    'folder_directory': 'C:/Users/Chris/Desktop/Dashboard/PEAK',
    'input_filename': 'IN.csv',
    'output_filename': 'OUT.csv',
    'chunk_size': '3000'

}
config['A1_post_processing_thresh_dump'] = {
    'specify whether or not the threshold should be included in the post processing a1 output csv for each pollutant. enter \'true\' to enable or \'false\' to disable\n'
    'NO2': 'true',
    'WCPC': 'true',
    'O3': 'true',
    'CO': 'true',
    'CO2': 'true',
    'NO': 'true',
    'WS': 'true',
    'WD': 'true'
}

#AQ setting
config['AQ_thresh'] = {
    'the flat AQ warning threshold can be set for each pollutant here\n'
    'NO2': '60',
    'WCPC': '5000',
    'O3': '62',
    'CO': '9',
    'CO2': '800',
    'NO': '100',
    'WS': '1',
    'WD': '180'}

#baseline settings
config['baseline'] ={
    'settings of the baseline calculation algorithm can be specified here\n'
    'window_size': '6',
    'smoothing_index': '25',
    'chunk_size': '3000',
    'interlace_chunks':'true',
    'folder_directory': 'C:/Users/Chris/Desktop/Dashboard/BASELINE',
    'input_filename': 'IN.csv',
    'output_filename': 'OUT.csv',
    'settings_in_name': 'true'

}

#modbus settings
#the "o3_modbus_hr" will always be 0 (as long as ModbusRegisters(1) = B2_O3 in the MAIN_PROG.CR1X). After that, the next one will be 3 and then 5,7,9,11 (+2...). They follow the ModbusRegisters(#)
config['modbus-tcp_settings'] ={
    'parameters of the modbus tcp/ip connection can be set here. these settings will only be read by the modbus-tcp_daq script so they can be left blank if a different daq script is being used. which modbus holding registers to read as well as how many should be read can be set for each pollutant here. typically, for float values, register_length for each pollutant should be set to \'2\'. individual pollutants can be enabled or disabled by entering \'true\' or \'false\'. if a pollutant is disabled, redis will send either a constant value or generate random values for the disabled pollutant(s). set the random_or_flat_if_disabled setting to \'random\' to use random values or \'flat\' to use flat values\n'
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









####################################################################################################################







################
# 'is_formatted': 'false',
# 'columns_with_data': '3,7'
################


with open('./user_defined_settings.ini', 'w') as f:
    config.write(f)