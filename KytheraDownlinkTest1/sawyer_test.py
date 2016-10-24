"""
Simple test provides options for bidirectional testing with
kythera

"""

import serial

ser = serial.Serial('/dev/ttyUSB0', 19200)
test_message = 'Hey! This is a string that contains more than 1 bytes! Even more than 90! This message is 100 bytes!'
string = 'Hello from Raspberry Pi'
ser.write('%s\n' % string)

sawyer_file = open('tomsawyerChapter1.txt', 'r')
ser.write('successfully opened tom sawyer text\n')
 
ser.write('\n\nsend me an \'t\' to get 100 bytes, \'s\' to get first chapter of tomsawyer, \'q\' to quit \n')

while True:
    incoming = ser.read()
    print 'Received %s' % incoming
    ser.write('\n\nRPi Received: %s\n\n' % incoming)
    if(incoming == 's'):
      for line in sawyer_file:
        ser.write('%s' % line)
      ser.write('\n\nwow can\'t believe that took so long\n\n')
    elif(incoming == 't'):
      ser.write('%s\n' % test_message)
    elif(incoming == 'q'):
      ser.write('\n\ngoodbye')
      break
