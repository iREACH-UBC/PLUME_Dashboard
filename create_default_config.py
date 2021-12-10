from configparser import ConfigParser

config = ConfigParser()



#live plot y-range settings
config['y-ranges'] = {
    'NO2': '0,80',
    'WCPC': '7000,10000',
    'O3': '0,100',
    'CO': '0,100',
    'CO2': '0,100',
    'NO': '0,100'
}

#command char
config['command_char'] = {
    'command_character':'*'
}

#log files directory
config['log_directory'] = {
    'log_files_directory':'C:\Users\Chris\Sync\iREACH\Students\Chris\Test1'
}

#misc, including algorithm circuit breaker
config['algorithm_circuit_breaker'] = {
    'A1_on': 'true',
    'A2_on': 'false',
    'AQ_on': 'true',
}

#data setting
config['real_or_simulated'] = {
    'NO2': 'simulated',
    'WCPC': 'real',
    'O3': 'real',
    'CO': 'real',
    'CO2': 'real',
    'NO': 'real',
    'simulated_data_path': 'C:/Users/Chris/Sync/iREACH/Students/Chris/SIMULATED_DATA/',
    'simulated_NO2_filename': 'NO2_12s.xlsx',
    'simulated_WCPC_filename': 'WCPC.csv',
    'simulated_O3_filename': 'O3.csv',
    'simulated_CO_filename': 'CO.csv',
    'simulated_CO2_filename': 'CO2.csv',
    'simulated_NO_filename': 'NO.csv'

}

#A1 settings
config['A1_coeff'] = {
    'NO2': '15',
    'WCPC': '3',
    'O3': '3',
    'CO': '3',
    'CO2': '3',
    'NO': '3'
}
config['A1_percentile'] = {
    'NO2': '50',
    'WCPC': '50',
    'O3': '50',
    'CO': '50',
    'CO2': '50',
    'NO': '50'
}
config['A1_thresh_bump_percentile'] = {
    'NO2': '1',
    'WCPC': '1',
    'O3': '1',
    'CO': '1',
    'CO2': '1',
    'NO': '1'} #set to 0 to disable
config['A1_misc'] = {
    'startup_bypass': '30',
    'post_processing_folder_directory': 'C:/Users/Chris/Sync/iREACH/Students/Chris/PEAK/',
    'post_processing_input_filename': 'IN.csv',
    'post_processing_output_filename': 'OUT.csv',
    'post_processing_chunk_size': '3000'

}
config['A1_post_processing_thresh_dump'] = {
    'NO2': 'true',
    'WCPC': 'false',
    'O3': 'false',
    'CO': 'false',
    'CO2': 'false',
    'NO': 'false',
    'only_show_base_thresh': 'true',
    'limit_thresh_to_just_above_max': 'true'
}

#AQ setting
config['AQ_thresh'] = {
    'NO2': '40',
    'WCPC': '100',
    'O3': '100',
    'CO': '100',
    'CO2': '100',
    'NO': '100'}

#baseline settings
config['baseline'] ={
    'window_size': '5',
    'smoothing_index': '5',
    'chunk_size': '3000',
    'folder_directory': 'C:/Users/Chris/Sync/iREACH/Students/Chris/BASELINE/',
    'input_filename': 'IN.csv',
    'output_filename': 'OUT.csv'

}

################
# 'is_formatted': 'false',
# 'columns_with_data': '3,7'
################


with open('./user_defined_settings.ini', 'w') as f:
    config.write(f)