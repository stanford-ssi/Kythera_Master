from __future__ import division
import smbus
import bmp180
import math
import BNO055
import time
import pykalman
import numpy as np

class KytheraSensors:

    baros = []
    imus = []
    count = 0

    def __init__(self):
        self.bus = smbus.SMBus(1)
        for i in [3, 4, 5]:
            try:
                baro = bmp180.BMP180(channel=i, bus=self.bus, os_mode=bmp180.OS_MODE_8)
                self.baros.append(baro)
            except IOError:
                print 'Barometer in channel %d not found.' % i
        calibs = {0: [134, 0, 234, 255, 14, 0, 53, 0, 121, 255, 72, 1, 255, 255, 255, 255, 1, 0, 232, 3, 123, 2]}
        calibs = {0: [255, 255, 237, 255, 23, 0, 19, 0, 26, 255, 30, 1, 255, 255, 255, 255, 1, 0, 232, 3, 75, 2]}
        calibs = {0: [140, 0, 200, 255, 7, 0, 40, 255, 99, 0, 109, 0, 254, 255, 255, 255, 2, 0, 232, 3, 221, 2]}
        for i in [0, 1, 2]:
            try:
                self.switch(i)
                imu = BNO055.BNO055(channel=i) #channel=i, bus=self.bus)
                imu.begin()
                #if calibs.get(i): imu.set_calibration(calibs[i])
                self.imus.append(imu)
            except IOError:
                print 'IMU in channel %d not found.' % i
        time.sleep(0.1)

    def switch(self, channel):
        self.bus.write_byte(0x70, 1 << channel)

    def read(self):
        accs = []
        mags = []
        gyrs = []
	pressures = []
	temperatures = []
        euler = []
        for imu in self.imus:#[self.imus[1]]:
            self.switch(imu.channel)
            #status = imu.get_calibration_status()
            #print "yo",imu.channel, status, imu.get_calibration()
            #print "sup",imu.read_euler()
            accs.append(imu.read_accelerometer())
            mags.append(imu.read_magnetometer())
            gyrs.append(imu.read_gyroscope())
            euler.append(imu.read_euler())
            #print "calib",imu.channel,imu.get_calibration()
        if self.count % 10 == 0:
		for baro in self.baros:
		    try:
			(p, t) = baro.read()
			pressures.append(p)
			temperatures.append(t)
		    except IOError:
			continue
        self.count += 1

        return {'pressure': pressures, 'temperature': temperatures, 'acc':accs,'mag':mags,'gyro':gyrs,'euler':euler}

alt = lambda P: 44330*(1-(P/1016.25)**(1/5.255))
class SensorFilter:
    def __init__(self):
        self.sensors = KytheraSensors()
        self.kalman = pykalman.KalmanFilter(transition_matrices=[[1]],observation_matrices=[[1]],observation_covariance=[[1.5]])
        self.kalman.observation_covariance = [[0.5]]
        self.kalman.transition_covariance = [[0.001]]
        self.temp = pykalman.KalmanFilter(transition_matrices=[[1]],observation_matrices=[[1]],observation_covariance=[[1.5]])
        self.temp.observation_covariance = [[0.5]]
        self.temp.transition_covariance = [[0.001]]
        self.state = {'altitude': [0,5], 'euler': None, 'temperature': [25,5], 'acc':None, 'gyro': None,'mag':None}
    def loop(self):
        for _ in range(1000):
            data = self.sensors.read()
            if len(data['pressure']) != 0:
                alts = map(alt, data['pressure'])
                alts = sum(alts)/len(alts)
                st, cov = self.kalman.filter_update(self.state['altitude'][0], self.state['altitude'][1], alts)
                self.state['altitude']  = st[0][0], cov[0][0]
                temps = data['temperature']
                temp = sum(temps)/len(temps)
                st, cov = self.temp.filter_update(self.state['temperature'][0], self.state['temperature'][1], temp)
                self.state['temperature']  = st[0][0], cov[0][0]
            self.state['acc'] = self.dothething(data['acc'],self.state['acc'])
            self.state['gyro'] = self.dothething(data['gyro'],self.state['gyro'])
            self.state['mag'] = self.dothething(data['mag'],self.state['mag'])
            self.state['euler'] = data['euler']
    def dothething(self, data,prev):
        a = 0; b = 0; c = 0;
        for i in data:
            a += i[0]; b+=i[1]; c+=i[2]
        a = a/len(data); b=b/len(data); c=c/len(data) 
        if prev is not None:
           diff = math.sqrt((a-prev[0])**2+(b-prev[1])**2+(c-prev[2])**2)
           if diff/(prev[0]*prev[0]+prev[1]*prev[1]+prev[2]*prev[2]) > 10: return prev
        return [a,b,c]

import time
            
f = SensorFilter()
t0 = time.time()
f.loop()
print time.time()-t0

exit()

s = KytheraSensors()
import time
t0 = time.time()
for _ in range(100):
#while True:
    s.read()
print time.time()-t0
exit()
def read_imu(i):
    bus = smbus.SMBus(1)
    bus.write_byte(0x70,1<<i)
    print "hi"
    sensor = BNO055.BNO055()
    print "hello"
    print sensor.begin()
    print sensor.get_system_status()
    print sensor.read_euler()
    print sensor.read_gyroscope()
    print sensor.read_accelerometer()

for i in range(0,8):
  try:
    print i
    read_imu(i)
  except:
    print "ooops",i
    continue

"""
init_baros()
import time
t0 = time.time()
#for _ in range(100):
while True:
    read_baros()
print time.time()-t0

for i in range(0,8):
    #print i
    #plex.channel(0x70,i)
    I2C_setup(i)
    try:
    	sensor = bmp180.Bmp180(smbus.SMBus(1),addr=0x77)
    except IOError:
        print "foiled!"
        continue
    sensor.os_mode = bmp180.OS_MODE_SINGLE
    for _ in range(10):
        vals.append(sensor.pressure_and_temperature[0])
print sum(vals)/len(vals)
"""
