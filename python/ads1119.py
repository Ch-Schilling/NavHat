"""
This module provides a basic interface to the Texas Instruments ADS1119 analogue to digital converter.
It inherits the I2C read and write access from the i2c_device module.

Christian Schilling     September 2024
"""

import time
import i2c_device

# register description
ADS119_RESET        = 0x06 
ADS119_START_SYNC   = 0x08
ADS119_POWERDOWN    = 0x02
ADS119_READ_DATA    = 0x10
ADS119_READ_REG     = 0x20
ADS119_READ_BUSY    = 0x24
ADS119_WRITEREG     = 0x40

class ADS1119(i2c_device.i2c_device):
    """
    Provides an interface to the ADC based on the information of the I2C bus and the device address.

    :param bus: the I2C bus of the connected device. For example 1 or i2c-1
    :type bus: int or str
    :param addr: address of the device. Like 0x20 for a port extender
    :type addr: int in the range of 0x08 ... 0x77
    :param verbose: setting for printing verbosity information to the console, defaults to False.
    :type verbose: boolean
    """
    def __init__(self, bus_number, i2c_addr, verbose = False):
        super().__init__(bus_number, i2c_addr, verbose)
        self.verbose = verbose
        
        # configuration options
        self.gain = 1
        self.datarate = 0
        self.mux = 0
        self.ext_vref = 0
        self.continous = 1
        
        # parameters
        self.vref = 2.048
    
    def reset(self):
        """
        Resets the ADC via its reset command over the I2C bus.
        """
        if self.verbose:
            print("Resetting ADS1119")
        self.write(ADS119_RESET, [])

        # configuration reset values
        self.gain = 1
        self.datarate = 0
        self.mux = 0
        self.ext_vref = 0
        self.continous = 0
        return self
        
    def power_down(self):
        """
        shuts down the ADC in sleep mode.
        """
        if self.verbose:
            print("Power down ADS1119")
        self.write(ADS119_POWERDOWN, [])
        return self
    
    def start(self, continous = True):
        """
        Starts the ADC. This can be done for a single measurement of for continous sampling.
        
        :param continous: Flag for continous sampling, defaults to True.
        :type continous: boolean
        """
        self.continous = continous
        if self.verbose:
            print("Starting ADS1119, continous=", self.continous)
        self.write(ADS119_START_SYNC, [])
        return self
        
    def read_data(self):
        """
        Reads the last result from the ADC.
        
        :return: last measured value.
        :rtype: integer, 16Bit two's complement value.
        """
        for k in range(5):
            if self.data_ready():
                blk = self.read(ADS119_READ_DATA, 2)
                value = (blk[0] << 8) + blk[1]
                return value
            else:
                time.sleep(0.01)
        return 0x0000
        
    def write_reg(self, val):
        """
        Writes to the configuration register.
        
        :param val: bit pattern for the configuration register.
        :type val: integer, 8 bits only
        """
        if self.verbose:
            print("Writing configuration ADS1119: %02x" % (val))
        self.write(ADS119_WRITEREG, [val & 0xff])
        return self

    def configure(self):
        """
        Configures the configuration register based on gain, datarate, input multiplexer and voltge reference.
        These parameters are hold in the object.
        """
        # check configuration parameters in correct range
        assert(self.gain == 1 or self.gain == 4)
        assert(self.datarate >= 0 and self.datarate <4)
        assert(self.mux >= 0 and self.mux <8)
        assert(self.ext_vref == 0 or self.ext_vref == 1)
        assert(self.continous == 0 or self.continous == 1)
        
        if self.gain == 1:
            gainval = 0x00
        else:
            gainval = 0x10
        config = self.ext_vref | (self.continous << 1) | (self.datarate << 2) | (gainval) | (self.mux << 5)
        self.write_reg(config)
        
    def read_register(self):
        """
        Reads the configuration register of the ADC.
        
        :return: configuration value.
        :rtype: integer, 8bit only
        """
        blk = self.read(ADS119_READ_REG, 1)
        if self.verbose:
            print("Read configuration of ADS1119 %02x" % (blk[0]))
        return blk[0]

    def data_ready(self):
        """
        Reads the conversion status of the ADC. Information is read from the busy register.
        
        :return: conversion status, reads True if a new reading is available, reads False if conversion data are read.
        :rtype: boolean
        """
        blk = self.read(ADS119_READ_BUSY, 1)
        if self.verbose:
            print("Ready register: %02x" % (blk[0]))
        ready = (blk[0] & 0x80) != 0
        return ready
        
    def read_voltage(self):
        """
        Reads the measured voltage from the ADC in Volts. The result is depending on the measured value, the gain and the voltage reference.
        
        :return: last measured voltage in [v].
        :rtype: float
        """
        bval = self.read_data()
        v = self.gain * (self.vref * bval / 0x7fff)
        return v

if __name__ == '__main__':
    

    SMBUS_NUMBER = 1
    addr = 0x48
    ads=ADS1119(SMBUS_NUMBER, addr)
    ads.reset()
    ads.continous = 1
    ads.configure()
    ads.start()
    time.sleep(0.2)
    
    print("read: ", ads.data_ready(), ads.read_register(), ads.read_data())
    time.sleep(0.1)
    print("read: ", ads.data_ready(), ads.read_register(), ads.read_data())
    time.sleep(0.1)
    print("read: ", ads.data_ready(), ads.read_register(), ads.read_data())
    time.sleep(0.1)

    v = ads.read_voltage()
    
