"""
Sensor interfacing functions utilized by Kythera to gather sensor values
and flight status.

Status enumeration:
  /*
   * 0:   startup
   * 5:   idle-prelaunch (all nodes reporting prelaunch status bit)
   * 10:  motor-ignition (vehicle z-acceleration exceedes 2g's)
   * 15:  burnout (vehicle velocity begins to decrease)
   * 20:  coast   (reported until vehicle dips below 10 meters per second)
   * 25:  slow-coast (<10 meters per second)
   * 30:  near-apogee (<5 meters per second)
   * 35:  apogee (<1 meter per second)
   * 40:  early-descent (<5 meters per second)
   * 45:  programmable-recovery-event-1 (user specified)
   * 50:  programmable-recovery-event-2 (user specified)
   * 55:  slow-descent  (<6 meters per second)
   * 60:  landing (<0.5 meters per second)
   */

"""
# ADD the required sensor libraries to the current path
import sys
sys.path.insert(0, './Pi_10DOF')

from L3GD20 import L3GD20
from Adafruit_BMP085 import Adafruit_BMP085
from Adafruit_LSM303 import Adafruit_LSM303
import smbus
import time

"""
	Class to handle all interactions with the 10DOF.
"""
class Unified_Sensor:
	"""
		Initialize all sensors via i2c.
	"""
	def __init__(self):
		self.L3GD20_s = L3GD20(busId = 1, slaveAddr = 0x6b, ifLog = False, ifWriteBlock=False)
		self.L3GD20_s.Set_PowerMode("Normal")
		self.L3GD20_s.Set_FullScale_Value("250dps")
		self.L3GD20_s.Set_AxisX_Enabled(True)
		self.L3GD20_s.Set_AxisY_Enabled(True)
		self.L3GD20_s.Set_AxisZ_Enabled(True)
		self.L3GD20_s.Init()
		self.L3GD20_s.Calibrate()

		self.bmp = Adafruit_BMP085.BMP085()
		self.lsm = Adafruit_LSM303.Adafruit_LSM303()

		# for sensing roll rate
		self.start_time = time.time()
		self.dt = 0.02
		self.x = 0
		self.y = 0
		self.z = 0

	"""
		BMP pressure.
	"""
	def get_pressure(self):
		return self.bmp.readPressure()

	"""
		BMP temperature.
	"""
	def get_temperature(self):
		return self.bmp.readTemperature()

	"""
		BMP altitude.
	"""
	def get_altitude(self):
		return self.bmp.readAltitude()

	"""
		L3GD20 xyz change.
	"""
	def get_xyz(self):
		xyz_1 = self.L3GD20_s.Get_CalOut_Value()
		time.sleep(self.dt) # sleep a bit so we can get the difference in xyz
		xyz_2 = self.L3GD20_s.Get_CalOut_Value()

		self.x += (xyz_2[0] - xyz_1[0])*self.dt;
		self.y += (xyz_2[1] - xyz_1[1])*self.dt;
		self.z += (xyz_2[2] - xyz_1[2])*self.dt;
		return (self.x, self.y, self.z)

	def get_acc(self):
		lsm = self.get_lsm()
		return lsm[0]

	def get_mag(self):
		lsm = self.get_lsm()
		return lsm[1]

	"""
		TODO: the LSM data needs to be parsed.
	"""
	def get_lsm(self):
		return self.lsm.read()

	def __repr__(self):
		return "I am a unified sensor. "
