"""
Main executable for the Kythera flight computer

Demo written for 5/28/16 Stanford Faculty and Community demo

"""

# IMPORTS
#import smbus
import time
import struct
import csv
import subprocess
import signal
import os
import sys
import time
import threading
import serial
import sys
from multiprocessing import Process


# INIT GLOBALS
kytheraLog = open('logs/KytheraLog.txt', 'a')
kytheraLog.write('\n\nSTARTING NEW SESSION\n')
ser = serial.Serial('/dev/ttyUSB0', 19200)


# INIT XBEE
import main
f = main.SensorFilter()
f.loop()
s = main.KytheraSensors()
last_y = f.state["euler"][0][1]
last_x = f.state["euler"][0][2]
last_z = f.state["euler"][0][0]
delay = 3.5

while True:
    #s.read()
    f.loop()
    #print f.state
    #print f.state["acc"][0]
    acc_y =  str(f.state["acc"][0])
    acc_x =  str(f.state["acc"][1])
    acc_z =  str(f.state["acc"][2])
    info_sum = 0;
    #print "Acc Y ", acc_y[0:5]
    #print "Acc X ",acc_x[0:5]
    #print "Acc Z ",acc_z[0:5]
    temp_f =  str((f.state["temperature"][0] * 1.8) + 32.0)
    #print "Temp ",temp_f[0:4]
    alt_m =  str(f.state["altitude"][0])
    #print "Alt ",alt_m[0:4]
    if(f.state["euler"][0][1] - last_y < 100):
        last_y = f.state["euler"][0][1]
    if(f.state["euler"][0][2] - last_x < 100):
        last_x = f.state["euler"][0][2]

    z_change = (f.state["euler"][0][0] - last_z)/delay
    if(z_change == 16.0 or z_change == -16.0):
        z_change = 0.0
    last_z = f.state["euler"][0][0]


    #print "Gyro Y", str(last_y)[0:5]
    #print "Gyro X", str(last_x)[0:5]
    #print "Roll Rate", str(z_change/360)[0:5]
    info_sum = 99+ float(acc_y[0:5]) +float(acc_x[0:5])+float(acc_z[0:5])+float(temp_f[0:5])+ \
    float(alt_m[0:4])+float(str(last_y)[0:5]) + float(str(last_x)[0:5]) +float(str(z_change/360)[0:5])
    line = "99K"+acc_y[0:5].zfill(5)+acc_x[0:5].zfill(5)+acc_z[0:5].zfill(5)+temp_f[0:4].zfill(4)+ \
    alt_m[0:4].zfill(4)+str(last_y)[0:5].zfill(5)+str(last_x)[0:5].zfill(5)+str(z_change/360)[0:5].zfill(5)+str(info_sum)+"\n"
    print line
    ser.write(line)

    time.sleep(delay)

# INIT SENSORS


# PING CAN BUSSES


# POWERUP


# testing
# datalink.runTest()
kytheraLog.write('\ntest complete success \n')

# Ithread.join()
print('\nInput thread finished\n')

# FLIGHT
