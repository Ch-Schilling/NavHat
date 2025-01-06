"""
This module creates a base class for I2C devices with easy access methods.
Derived classes for specific I2C devices inherit the base methods and can focus on the specific features.
The module makes use of smbus.py, however this would be the right spot to use a different access library if needed.
"""

import smbus


class i2c_device:
    """
    This is the base class of I2C devices. It holds its information about I2C bus and device address and provdes simple read an write access for child classes.

    :param bus: the I2C bus of the connected device. For example 1 or i2c-1
    :type bus: int or str
    :param addr: address of the device. Like 0x20 for a port extender
    :type addr: int in the range of 0x08 ... 0x77
    :param verbose: setting for printing verbosity information to the console, defaults to False.
    :type verbose: boolean
    """
    def __init__(self, bus, addr, verbose = False):
        self.bus  = smbus.SMBus(bus)
        self.addr = addr
        self.verbose = verbose
        
        # set up different I2C implementations here
        
    def write(self, register, data):
        """
        writes a one byte register followed by zero or more bytes of data to the device.
        
        :param register: device register to write the data
        :type register: one byte integer
        :param data: data to be written after specific register
        :type data: array of single byte integers
        :return: returns a success value.
        :rtype: int
        """
        if self.verbose:
            print("i2c_device write: register, data: ", register, data)

        assert register >= 0x00 and register <= 0xff, "register is only 8 bits wide."
        ret = self.bus.write_i2c_block_data(self.addr, register, data)
        return ret
    
    def read(self, register, lenght):
        """
        reads one or more bytes from a certain register.
        
        :param register: device register to read from
        :type register: one byte integer
        :param lenght: number of bytes to be read
        :type lenght: one byte integer
        :return: returns a block of data
        :rtype: array of int
        """
        assert register >= 0x00 and register <= 0xff, "register is only 8 bits wide."
        blk = self.bus.read_i2c_block_data(self.addr, register, lenght)
        if self.verbose:
            print("i2c_device read: register, data: ", register, blk)
        return blk
        
