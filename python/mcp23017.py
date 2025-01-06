"""
This module provides a basic interface to the MCP23017 I/O port extender.
It inherits the I2C read and write access from the i2c_device module.

Christian Schilling     November 2024
"""

import time
import i2c_device

#Registers of MCP23017 datasheet section register map
MCP23017_IODIRA         = 0x00
MCP23017_IODIRB         = 0x01
MCP23017_PULL_UP_A      = 0x06
MCP23017_PULL_UP_B      = 0x07
MCP23017_GPIOA          = 0x12
MCP23017_GPIOB          = 0x13

#make register access more user friendly
PORT_A                  = 0x00
PORT_B                  = 0x01


class MCP23017(i2c_device.i2c_device):
    """
    provided a python friendly interface to the registers of the MCP23017 I/O extender.
    The communication to the I2C bus is not visible to the user.

    :param bus: the I2C bus of the connected device. For example 1 or i2c-1
    :type bus: int or str
    :param addr: address of the device. Like 0x20 for a port extender
    :type addr: int in the range of 0x08 ... 0x7f
    :param self.verbose: setting for printing verbosity information to the console, defaults to False.
    :type verbose: boolean
    """
    def __init__(self, bus, addr, verbose = False):
        super().__init__(bus, addr, verbose)
        self.verbose = verbose

    def set_io_direction(self, port, direction):
        """
        sets the direction of the I/O port, input or output.
    
        :param port: the selected port, A or B. Use PORT_A or PORT_B.
        :type port: int
        :param direction: direction of the I/O pin. 0 means output.
        :type direction: int, bit pattern of all 8 I/O pins.
        """
        assert port == PORT_A or port == PORT_B, "port needs to be PORT_A or PORT_B"
        self.write(port + MCP23017_IODIRA, [direction])
        return self
    
    def get_io_direction(self, port):
        """
        gets the direction of the I/O port, input or output.
    
        :param port: the selected port, A or B. Use PORT_A or PORT_B.
        :type port: int
        :return: bit pattern of the port direction. 0 means output.
        :rtype: integer, only the lowest 8 bits are used 
        """
        
        assert port == PORT_A or port == PORT_B, "port needs to be PORT_A or PORT_B"
        direction = self.read(port + MCP23017_IODIRA, 1)
        return direction[0]
    
    def set_io_output(self, port, pattern):
        """
        sets the output of the I/O port, high or low.
    
        :param port: the selected port, A or B. Use PORT_A or PORT_B.
        :type port: int
        :param pattern: pattern of the I/O pins. 1 means high, 0 means low, respectivly.
        :type pattern: int, bit pattern of all 8 I/O Pins.
        """
        assert port == PORT_A or port == PORT_B, "port needs to be PORT_A or PORT_B"
        self.write(port + MCP23017_GPIOA, [pattern])
        return self

    def get_io_pin(self, port):
        """
        gets the output state of the I/O port, high or low.
    
        :param port: the selected port, A or B. Use PORT_A or PORT_B.
        :type port: int
        :param pattern: pattern of the I/O pins. 
        :type pattern: int, bit pattern of all 8 I/O Pins.
        :return: bit pattern of the port status. 1 means high, 0 means low, respectivly.
        :rtype: integer
        """
        assert port == PORT_A or port == PORT_B, "port needs to be PORT_A or PORT_B"
        val = self.read(port + MCP23017_GPIOA, 1)
        return val[0]

    def set_pull_up(self, port, pattern):
        """
        Configures the weak pull-up resistors on each pin of the I/O port. Setting is only valid if configured as an input.
        
        :param port: the selected port, A or B. Use PORT_A or PORT_B.
        :type port: int
        :param pattern: pattern of the I/O pins. 1 means pull-up resistor enabled.
        :type pattern: int, bit pattern of all 8 I/O Pins.
        """
        assert port == PORT_A or port == PORT_B, "port needs to be PORT_A or PORT_B"
        self.write(port + MCP23017_PULL_UP_A, [pattern])
        return self


if __name__ == '__main__':
    
    # small demo to test functionality
    SMBUS_NUMBER = 1
    addr = 0x22
    iod=MCP23017(SMBUS_NUMBER, addr)

    time.sleep(0.5)
    iod.set_io_direction(PORT_A, 0x00)
    iod.set_io_direction(PORT_B, 0x00)

    print(iod.get_io_pin(PORT_B))

    time.sleep(0.5)
    iod.set_io_output(PORT_B, 0x01)
    print(iod.get_io_pin(PORT_B))
    time.sleep(0.5)
    iod.set_io_output(PORT_B, 0x00)
    print(iod.get_io_pin(PORT_B))
    
