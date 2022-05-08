r"""
Elation Sports Technologies LLC
2 Mar 2021

Serial Logger

This script is meant to log data that is sent by Arduino (or ESP32, Raspberry Pi,
or another microcontroller or a PC) over serial/USB.

To install the Serial module on Spyder/Anaconda, use:
pip install pyserial


"""

import csv,time
import matplotlib.pyplot as plt
import serial, io, datetime
from serial import Serial

def readData():
    buffer = ""
    while True:
        oneByte = ser.read(1)
        if oneByte == b"\n":    #method should returns bytes
            return buffer
        else:
            buffer += oneByte.decode("ascii")


timestr = time.strftime("%d%b%Y_%H%M%p")

folder_path = r'C:\Users\(username)\Desktop' #Replace "username" with your PC's local username.
file_prefix = r'Log' 
file_type = '.csv'
file_name = file_prefix + '_' + timestr + file_type
file_path = folder_path + '\\' + file_name

#Include the timestamps in the data
include_timestamp_boolean = True

#Show the serial data in the Python console
show_serial_data_boolean = True

addr = "COM6" ## serial port to read data from
baud = 9600 ## baud rate for instrument

ser = serial.Serial(
    port = addr,\
    baudrate = baud,\
    parity=serial.PARITY_NONE,\
    stopbits=serial.STOPBITS_ONE,\
    bytesize=serial.EIGHTBITS,\
    timeout=0)

print('Start time: ' + timestr)
print("Connected to: " + ser.portstr)
print('Now collecting data...')

start_time = time.time()

try:
    
    with open(file_path, 'w', newline='') as csvfile:
        
        spamwriter = csv.writer(csvfile, delimiter=',')

        while True:
            line = readData()
            
            if show_serial_data_boolean:
                print(line)
            
            
            if include_timestamp_boolean != True:
                to_write = [str(line)]
            else:
                to_write = [str(time.time()-start_time) + ',' + str(line)]
            
            spamwriter.writerow(to_write)
                

except KeyboardInterrupt:
    
    print('Cntl+C press detected - ending script.')
    
    print()
    print('Log data saved to:')
    print(file_name)

    #datafile.close()
    ser.close()
    
    






