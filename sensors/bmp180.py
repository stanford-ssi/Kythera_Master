#!/usr/bin/env python

import struct
import time

_REG_AC1                 = 0xAA
_REG_AC2                 = 0xAC
_REG_AC3                 = 0xAE
_REG_AC4                 = 0xB0
_REG_AC5                 = 0xB2
_REG_AC6                 = 0xB4
_REG_B1                  = 0xB6
_REG_B2                  = 0xB8
_REG_MB                  = 0xBA
_REG_MC                  = 0xBC
_REG_MD                  = 0xBE
_REG_CALIB_OFFSET        = _REG_AC1
_REG_CONTROL_MEASUREMENT = 0xF4
_REG_DATA                = 0xF6

_CMD_START_CONVERSION    = 0b00100000
_CMD_TEMPERATURE         = 0b00001110
_CMD_PRESSURE            = 0b00010100

OS_MODE_SINGLE = 0b00
OS_MODE_2      = 0b01
OS_MODE_4      = 0b10
OS_MODE_8      = 0b11

_WAIT_TEMPERATURE = 0.0045
_WAIT_PRESSURE    = [0.0045, 0.0075, 0.0135, 0.0255]

class BMP180:

    def __init__(self, bus, channel, os_mode=OS_MODE_SINGLE):
        bus.write_byte(0x70, 1 << channel)
        self.channel = channel
        self._bus = bus
        self._addr = 0x77
        self._os_mode = os_mode
        calib = self._bus.read_i2c_block_data(self._addr,
                                              _REG_CALIB_OFFSET, 22)
        (self._ac1, self._ac2, self._ac3, self._ac4,
         self._ac5, self._ac6, self._b1, self._b2,
         self._mb, self._mc, self._md) = struct.unpack(
             '>hhhHHHhhhhh', ''.join([chr(x) for x in calib]))

    def read(self):
        self._bus.write_byte(0x70, 1 << self.channel)
        cmd = _CMD_START_CONVERSION | _CMD_TEMPERATURE
        self._bus.write_byte_data(self._addr,
                                  _REG_CONTROL_MEASUREMENT, cmd)
        time.sleep(_WAIT_TEMPERATURE)
        vals = self._bus.read_i2c_block_data(self._addr,
                                             _REG_DATA, 2)
        ut = vals[0] << 8 | vals[1]

        cmd = _CMD_START_CONVERSION | self._os_mode << 6 | _CMD_PRESSURE
        self._bus.write_byte_data(self._addr,
                                  _REG_CONTROL_MEASUREMENT, cmd)
        time.sleep(_WAIT_PRESSURE[self._os_mode])
        vals = self._bus.read_i2c_block_data(self._addr,
                                             _REG_DATA, 3)
        up = (vals[0] << 16 | vals[1] << 8 | vals[0]) >> (8 - self._os_mode)

        x1 = ((ut - self._ac6) * self._ac5) >> 15
        x2 = (self._mc << 11) / (x1 + self._md)
        b5 = x1 + x2
        self._temperature = ((b5 + 8) / 2**4) / 10.0

        b6 = b5 - 4000
        x1 = self._b2 * ((b6 * b6) >> 12)
        x2 = self._ac2 * b6
        x3 = (x1 + x2) >> 11
        b3 = (((self._ac1 *4 + x3) << self._os_mode) + 2) >> 2
        x1 = (self._ac3 * b6) >> 13
        x2 = (self._b1 * (b6 * b6) >> 12) >> 16
        x3 = ((x1 + x2) + 2) >> 2
        b4 = (self._ac4 * (x3 + 32768)) >> 15
        b7 = (up - b3) * (50000 >> self._os_mode)
        if (b7 < 0x80000000):
            p = (b7 * 2) / b4
        else:
            p = (b7 / b4) * 2
        x1 = p**2 >> 16
        x1 = (x1 * 3038) >> 16
        x2 = (-7357 * p) >> 16
        self._pressure = (p + ((x1 + x2 + 3791) >> 4)) / 100.0

        return (self._pressure, self._temperature)

