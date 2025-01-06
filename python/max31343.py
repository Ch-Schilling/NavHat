"""
This module provides a basic interface to the Analog Devices MAX31343 real time clock.
It inherits the I2C read and write access from the i2c_device module.

Christian Schilling     September 2024
"""


import time
import i2c_device

#Registers of MAX31343 datasheet section register map
MAX31343_STATUS         = 0x00
MAX31343_INT_ENABLE     = 0x01
MAX31343_RESET          = 0x02
MAX31343_SECONDS        = 0x06

MAX31343_ALARM2         = 0x13
MAX31343_TRICKLE        = 0x19
MAX31343_TEMPERATURE    = 0x1a

#Flags
INTERRUPT_ALARM1        = 0x01
INTERRUPT_ALARM2        = 0x02
INTERRUPT_TIMER         = 0x04
INTERRUPT_TEMPERATURE   = 0x08
INTERRUPT_POWER_FAIL    = 0x20



def _bcd2bin(a):
    b = ((a & 0xf0) >> 4) *10
    return (b + (a & 0x0f))

def _bin2bcd(a):
    d = a // 10
    r = a % 10
    return ((d << 4) | r)


class MAX31343(i2c_device.i2c_device):
    """
    Provides a python friendly interface to the registers of the RTC MAX31343.

    :param bus: the I2C bus of the connected device. For example 1 or i2c-1
    :type bus: int or str
    :param addr: address of the device. Like 0x20 for a port extender.
    :type addr: int in the range of 0x08 ... 0x77
    :param verbose: setting for printing verbosity information to the console, defaults to False.
    :type verbose: boolean
    """
    def __init__(self, bus_number, i2c_addr, verbose = False):
        super().__init__(bus_number, i2c_addr, verbose)
        self.verbose = verbose
 
    def reset(self):
        """
        Resets the device by setting the corresponding bit in the register via the I2C bus.
        """
        if self.verbose:
            print("Resetting max31343")
        self.write(MAX31343_RESET, [0x01])
        return self
    
    def get_status(self):
        """
        Read status byte from device. Interrupt indicators are cleared afterwards.
        :return: Content of status register.
        :rtype: int, 8bit
        """
        status = self.read(MAX31343_STATUS, 1)[0]
        if self.verbose:
            print("Status max31343: %02x" % (status))
        return status
    
    def set_time(self):
        """
        Sets the time of the RTC. The time is taken from the host using localtime().
        """
        t=time.localtime()
        d=[0,0,0,0,0,0,0]
        d[0] = _bin2bcd(t.tm_sec)
        d[1] = _bin2bcd(t.tm_min)
        d[2] = _bin2bcd(t.tm_hour)
        d[3] = _bin2bcd(t.tm_wday)
        d[4] = _bin2bcd(t.tm_mday)
        d[5] = _bin2bcd(t.tm_mon)
        d[6] = _bin2bcd(t.tm_year % 100)
        if self.verbose:
            print('Time sending to max31343', d)
        self.write(MAX31343_SECONDS, d)
        return self
        
    def get_time(self):
        """
        Reads the time from the device and creats a time string in the ISO format.
        
        :return: Time information from the RTC.
        :rtype: str
        """
        d=self.read(MAX31343_SECONDS, 7)
        isostr = ("%4d-%02d-%02d %02d:%02d %02d" % (_bcd2bin(d[6])+2000, _bcd2bin(d[5]), _bcd2bin(d[4]), _bcd2bin(d[2]), _bcd2bin(d[1]), _bcd2bin(d[0])))
        return isostr
                                                                                                      

    def set_alarm2(self, hour=8, min=0):
        """
        Sets the alarm2 to the hour and minute every day. Each day, the alarm is triggered at the specified time.
        
        :param hour: the hour of the day in the range 0 - 23.
        :type hour: int
        :param min: the min after the set hour in the range 0 - 59.
        :type hour: int
        """
        #disable interrupt alarm2
        ie = self.read(MAX31343_INT_ENABLE, 1)[0] & ~INTERRUPT_ALARM2
        self.write(MAX31343_INT_ENABLE, [ie])
        d=[0,0,0]
        d[0] = _bin2bcd(min)
        d[1] = _bin2bcd(hour)
        d[2] = 0x80 # once every day
        self.write(MAX31343_ALARM2, d)
        #enable interrupt alarm2
        time.sleep(.05)
        ie = self.read(MAX31343_INT_ENABLE, 1)[0] | INTERRUPT_ALARM2
        self.write(MAX31343_INT_ENABLE, [ie])

        
    def set_trickle_charger(self, enable = True, setting = 0x05):
        """
        Sets and configures the trickle charcher of the device. It can be enabled or disabled. The voltage can be lowered by an additional diode (approx. 0.7V). The charging current can flow through a 3, 6 or 11 kOhm resistor.
        
        :param enable: enables or disables the trickle charger, defaults to True.
        :type enalbe: boolean
        :param setting: setting of extra diode and charging resistor, defaults to 0x05 which is extra diode and 3kOhm resistor.
        :type setting: int
        """
        #default setting: extra diode and 3kOhm
        en = 0x00
        if enable: en = 0x50
        self.write(MAX31343_TRICKLE, [(en | setting)])
        return self
        
    def temperature(self):
        """
        Returns the temperature in degrees Celsius as a floating point number.

        :return: Die temperature of the RTC in °C.
        :rtype: float
        """
        reg = self.read(MAX31343_TEMPERATURE, 2)
        self.temp = ((reg[0] <<8) + reg[1]) / 256.0
        #print("Temperature: %02x %02x -> %3.2f °C" % (reg[0], reg[1], self.temp))
        return self.temp
    

    def Diag(self):
        """
        Diag is a demo function to display time and temperature from the device in a terminal.
        """
        
        print("Status: %02x" % self.get_status())
        
        # print static title of the table
        print('MAX31343 real time clock')
        while 1:
            isotime = self.get_time()
            t = self.temperature()
            print("Temperature: %3.2f °C" % (self.temp))
            print("Time       : %s" % (isotime))
            time.sleep(1.0)
            print("\033[A"*3)


if __name__ == '__main__':
    

    SMBUS_NUMBER = 1
    addr = 0x68
    rtc=MAX31343(SMBUS_NUMBER, addr)
    rtc.set_time()
    time.sleep(0.5)
    rtc.set_trickle_charger()
    rtc.set_alarm2(7,56)
    rtc.Diag()
