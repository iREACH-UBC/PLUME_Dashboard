"""
Created by Julian Fawkes, 2020.

wcpc_daq.py - A standalone program that requests data from a TSI 375x/3789 WCPC then writes the data to a redis server
and a local csv file. Connect to the same redis server from Dash to visualize the data that is incoming.

Running the program: To run the program from the command line, you must include the pathname of the folder you wish
to log to *after* the function call. e.g. "python3 wcpc_daq.py /users/julianfawkes/mycoolfolder"

Using the Start Dash helper bash script helps walk you through this.
"""
import telnetlib
import csv
import os
import time
import sys
import json
import redis
import re


def get_wcpc_data():
    # When ran from the command line, this program must have the folder path you wish to log to after the program call.
    folderpath = str(sys.argv[1])
    # To make sure that the folder path is formatted correctly, remove a trailing '/' and add it back later
    if folderpath.endswith('/'):
        folderpath.removesuffix('/')
    # Open a connection to a redis server hosted on the local machine
    redisdata = redis.Redis('localhost')
    # TSI WCPC's transmit data over their serial port using json strings
    with telnetlib.Telnet() as tn:
        # Physical location of the USB serial adapter. Will vary between computers and the port you've plugged into.
        # Data transmission settings. These are set by the instrument you're connecting to and are found in the manual.
        # Open serial port with exception handling if port fails to open.
        while True:
            try:
                tn.open(host='169.254.4.17', port=3603, timeout=2)
            except IOError as error:
                print("The telnet connection at '" + str(tn.host) + ":" + str(
                    tn.port) + "' failed to open. Make sure the instrument is connected to the correct usb port.")
                print(error)
                time.sleep(5)
            else:
                print("Telnet connection at '" + str(tn.host) + ":" + str(tn.port) + "' has opened successfully.")
                tn.read_until(b"}").decode('ascii')
                # This command was taken from the WCPC programming guide on Sync. We are subscribing to the
                # concentration, meaning we get an updated value every second. There are other datastreams
                # we can subscribe to. Consult the programming guide for more options.
                tn.write(b'{"command":"SUBSCRIBE","transactionID":100,"subscriptionID":150,'
                         b'"element":"Concentration"}')
                tn.read_until(b"}").decode('ascii')
                break
        # Loop while process is running.
        while True:
            # Acquire data and write to a csv with exception handling if the connection is broken
            try:
                # Read a new line as it comes in.
                line = tn.read_until(b"}}").decode('ascii')
                # Strip the line of leading and trailing formatting characters.
                datadict = json.loads(line)['value']
                print(datadict)
                # Create a list to pass as column header in the CSV.
                columnlist = list(datadict.keys())
                # Place it in a redis dictionary.
                outdict = dict((k, datadict[k]) for k in ('time', 'concentration'))
                # The wcpc spits out YYYY-MM-DDT:HH:MM:SS-0800, so we split the string between the 'T' and '-'.
                outdict['time'] = (re.split("[T\-]", (outdict['time'])))[3]
                redisdata.set('wcpc', json.dumps(outdict))
                # Create a file name.
                filename = folderpath + "/wcpc data.csv"
                # Check if the log file already exists.
                file_exists = os.path.isfile(filename)
                # Exception handling causes the code not to crash if an exception in the CSV writing portion occurs.
                try:
                    with open(filename, 'a+', newline='\n') as wcpccsv:
                        # Create a dictwriter object using the previously created column header list.
                        writer = csv.DictWriter(wcpccsv, fieldnames=columnlist)
                        # If the log file did not already exist, write the column headers.
                        if not file_exists:
                            writer.writeheader()
                        # Write a row of new data.
                        writer.writerow(datadict)
                except IOError:
                    print("Failed to write to file. Check user and directory permissions.")
            # If the connection is severed for any reason, display the following:
            except IOError:
                print("The serial connection on port '" + str(tn.port) + "' has closed.")
                break


if __name__ == '__main__':
    try:
        get_wcpc_data()
    except KeyboardInterrupt:
        try:
            sys.exit(0)
        except SystemExit:
            print("Operator has terminated the process.")