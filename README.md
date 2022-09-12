# PLUME_Dashboard
Data visualization dashboard with post processing features designed specifically for mobile air quality monitoring 

## Installation

PLUME Dashboard requires three pieces of downloadable software to run: Python 3, the language PLUME Dashboard is coded in, PyCharm, a popular Python integrated development environment (IDE), and Redis, an open source (BSD licensed), in-memory data structure store, used as a database, cache, and message broker. The latest version of Python 3 can be downloaded and installed from [https://www.python.org/downloads/]. An installation guide for PyCharm is available at [https://www.jetbrains.com/help/pycharm/installation-guide.html]. Redis can be installed by downloading and running the installer “Redis-x64-3.0.504.msi”, which can be fount at [https://github.com/microsoftarchive/redis/releases].

PLUME Dashboard also requires the following Python packages to run:
* dash
* plotly
* dash-core-components
* dash-html-components
* dash-bootstrap-components
* dash-daq
* redis
* openpyxl
* pandas
* numpy
* db
* pyModbusTCP
* pyModbus

To install these packages, open PyCharm, navigate to File>Settings>Project>Python Interpreter and click on the “+” icon near the top left corner. From here, for each package, enter its name into the search bar, click on the first result, and then click on “Install Package” in the lower left corner. 

Alternatively, all of the packages can be installed by opening the “requirements.txt” file in PyCharm and clicking on “Install requirements” on the top yellow banner.

## Running PLUME Dashboard
Before running PLUME Dashboard, values for the following settings (which are blank by default) must be specified in the “user_defined_settings.ini” file:
* [log_directory], log_files_path
* (if one wishes to use the simulated data feature) [real_or_simulated], sim_data_path

If one wishes to use the provided modbus-tcp_daq.py script, values must be entered for the [modbus-tcp] settings as well. The pollutant specific settings can be left blank for pollutants that are disabled.

To run the dashboard, first run “redis-server.exe” (located in C:\Program Files\Redis) as administrator and then run redis-cli.exe (also located in C:\Program Files\Redis) as administrator. Next, open PyCharm and run modbus-tcp_daq.py (or a different DAQ script written using the DAQ script template provided in Section 5), and then run main.py.

Before running the baseline, post processing peak detection, and GPS data merging scripts, values must be entered for the [baseline], [A1_misc], and [GPS_merge_data] settings respectively. Some of the settings have default values whereas some of them are left blank by default. Additionally, for the post processing peak detection script, ensure that there is a value entered for all of the other A1 related settings.
