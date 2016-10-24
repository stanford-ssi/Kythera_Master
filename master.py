import smbus
import time
import struct
import csv
import subprocess 

"""
	SSI Rockets: Raspberry Pi based flight computer

	Finds all connected devices using i2c and logs data transmitted by sensors.

	Unimplemented features:
		* CAN bus (instead of i2c)

	Revision history:
		* 11/4/15: continuous logging, print statements in cronlog (not txt file)

	Known bugs:
		* Put bugs here
"""

logData = True
mybus = smbus.SMBus(1)

"""
1 byte read write from: http://blog.oscarliang.net/raspberry-pi-arduino-connected-i2c/
"""
def testAddress(address):
	try:
		writeNumber(1, address)
	except:
		return False
	time.sleep(1)
	number = readNumber(address)

	if number == 1:
		return True
	return False

"""
	Write a specific number to an address
"""
def writeNumber(value, address):
	mybus.write_byte(address, value)
	return

"""
	Read a byte (number) from an address
"""
def readNumber(address):
	number = mybus.read_byte(address)
	return number

"""
	Finds all connected i2c addresses
"""
def scan_i2c():
	connected_i2c = []
	cur_address = 0
	for jj in xrange(0, 120):
		if(testAddress(jj)):
			connected_i2c.append(jj)

	print "Connected i2c Ports:"
	print connected_i2c

	return connected_i2c

"""
	Read an array of bytes and convert into a floating point number.
"""
def readPacket(address):
    data = []
    length = int(mybus.read_byte(address));
    print 'length of data: ' + str(length)
    for ii in xrange(length):
    	try:
        	k = mybus.read_byte(address)
		data.append(k)
       	except:
       		break

    data_arr = []
    # join incoming data from separate bytes
    for jj in xrange(5):
    	ByteArray = data[jj*4:(jj+1)*4]
    	b = ''.join(chr(i) for i in ByteArray)
    	f = struct.unpack('f',b)
    	s = float(str(f)[1:-2])
    	data_arr.append(s)

    return data_arr


# data ping rate
rescan_rate = 1000
data_count = 0

"""
	Write to CSV file.
"""
def writeCSV(data,CSVfile):
    writer = csv.writer(CSVfile)
    writer.writerows(data)

if __name__ == "__main__":
	print 'I2C logger startup'

	start_time  = time.time()
	devices = scan_i2c() # gather the inital connected devices

	# loop infinitely to get data
	CSVfile = open('DataFiles/log.csv', 'w+')
	CSVfile.truncate() # wipes file every time script is run
	CSVfile.close()

	with open("log.csv", "a+") as CSVlog, open("logfile.txt", "a+") as log:

		while(True):
			data_count += 1
			# loop through each client
			if(data_count % rescan_rate == 0):
				try:
					CSVlog.close() # close for plotting
					subprocess.call(['gnuplot', 'graphpng.sh']) # replot png file
					devices = scan_i2c() # rescan at end of 10 cycles
									 	# put them into test mode
				except:
					print 'Device scanning failure' # goes to cronlog
					log.write("Device scanning failure.")

				CSVlog = open('DataFiles/log.csv', 'a+')	# reopen for appending data
				devices = scan_i2c() # rescan at end of 10 cycles
								 	# put them into test mode

				for item in devices:
		    	# which arduino are we looking for
				try:
					# print 'reading to [%s]' % (item)
					# this was for txt
					print "Reading from Arduino on port: %i \n" % (item)
					log.write("Reading from Arduino on port: %i \n" % (item))
					data_back = readPacket(item)
					data_line = "%i," % (item)
					print str(time.time() - start_time)
					data_line += str(time.time() - start_time) + ","

					for ii in xrange(len(data_back)):
						data_line += str(data_back[ii]) + ","

					data_line += "\n"
					CSVlog.write(data_line)
				except:
					devices = scan_i2c()  # lost an arduino = rescan
					log.write("Rescanning for i2c devices.")
			# sleep a bit
			time.sleep(0.05)
