# edit /etc/rc.local to ~/Desktop/launch.sh

#!/bin/sh
# launcher.sh
#

/bin/sleep 100
echo sleep finished, system has booted
# path to the main executable
/usr/bin/python /home/pi/Desktop/PiSky_Master/Kythera_Main.py
