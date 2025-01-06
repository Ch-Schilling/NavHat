"""
Contol TPS2HBxx high side swithes via a MCP23017 port extender.
The switches have a diagnostic mode, the current throuhg the load and the die temperature
can be monitored. A diagnostic current is created which flows throuhg a sense resistor. The resulting voltage is fed to an ADC.
"""

import time
import ads1119, mcp23017

# The board has 4 IOs, mapped to the lowest 4 Bits
OUTPUT_MASK = 0x0f
MAX_CHANNEL = 3

DIAG_SELECT_1 = 0x01
DIAG_SELECT_2 = 0x02

# current factor for TPS2HB16
SNS_CURRENT   = 3000
# current factor for TPS2HB32
#SNS_CURRENT   = 2000

# Sense resistor in Ohm
SNS_RESISTOR  = 750.0

class TPS2H:
    """
    This class holds the high side switches.

    :param io: a link to the port extender which controls the switches.
    :type io: MCP23017 object
    :param adc: a link to the ADC which is used to measure the diagnostic features.
    :type adc: ADS1119 object
    :param verbose: setting for printing verbosity information to the console, defaults to False.
    :type verbose: boolean
    """
    def __init__(self, io, adc, verbose = False):
        self.io = io
        self.adc = adc
        self.channel = 0x00
        
    def set_output(self, channel):
        """
        Activates one of the power outputs.
    
        :param channel: the channel that needs to be activated. Must be between 0 and 3.
        :type channel: int
        """
        assert(channel >= 0 and channel <= MAX_CHANNEL)
        self.channel = self.channel | (1 << channel)
        self.io.set_io_output(mcp23017.PORT_B, self.channel)
        return self

    def clear_output(self, channel):
        """
        Deactivates one of the power outputs.
    
        :param channel: the channel that needs to be deactivated. Must be between 0 and 3.
        :type channel: int
        """
        assert(channel >= 0 and channel <= MAX_CHANNEL)
        self.channel = self.channel & ~(1 << (channel))
        self.io.set_io_output(mcp23017.PORT_B, self.channel)

        return self
    
    def diag(self, channel, current=0, temperature=0):
        """
        Activates diagnostic mode for a certain channel. It can be chosen between current measurement or die temperature.
        If none of them are selected, diagnostic mode is turned off.
        
        :param channel: The channel for which diagnostic mode shall be selected.
        :type channel: int
        :param current: Set to True for current measurement.
        :type current: boolean
        :param temperature: Set to True for temperature measurement.
        :type temperature: boolean
        """
        assert(channel >= 0 and channel <= MAX_CHANNEL)
        self.diag_channel = channel
        self.diag_current = current
        self.diag_temperature = temperature
        
        #turn off diagnostic mode
        if current == 0 and temperature == 0:
            diag_pattern = 0x00
        else:
            ch = 1 << (int(channel /2) +2)
            diag_pattern = ch
            if current and channel & 0x01:
                    diag_pattern = diag_pattern | DIAG_SELECT_2
            if temperature:
                diag_pattern = diag_pattern | DIAG_SELECT_1
        #print("Diag: %02x" % diag_pattern)
        self.io.set_io_output(mcp23017.PORT_A, diag_pattern)
        return self
    
    def measure(self):
        """
        Reads from the ADC and calculates temperature or current, based on what was selected.
        
        :return: The reading of the selection. Units are [A] for current measurement, [°C] for temperature.
        :rtype: float
        """
        v = self.adc.read_voltage()
        print("v: %3.4f" % v)
        
        if self.diag_current:
            value = self.current(v)
        if self.diag_temperature:
            value = self.temperature(v)
        return value
    
    # for TPS2H junction temperature. See section 9.3.3.2 of the datasheet for details.
    def temperature(self, voltage):
        """
        Calculates the die temperature of the switch based on the measured voltage.
        
        :param voltage: Measured voltage [V]
        :type voltage: float
        :return: calculated temperature in [°C]
        :rtype: float
        """
        i_snst = voltage / SNS_RESISTOR *1000.0 #mA
        tj = (i_snst - 0.85) * 90.90909 + 25.0  #°C
        #print (voltage, i_snst, tj)
        return tj

    def current(self, voltage):
        """
        Calculates the current in the load based on the measured voltage.
        
        :param voltage: Measured voltage [V]
        :type voltage: float
        :return: calculated load current in [A]
        :rtype: float
        """
        i_sns = voltage / SNS_RESISTOR * SNS_CURRENT
        return i_sns
    
    
if __name__ == '__main__':

    SMBUS_NUMBER = 1
    ads=ads1119.ADS1119(SMBUS_NUMBER, 0x48, verbose = False)
    gpio = mcp23017.MCP23017(SMBUS_NUMBER, 0x22)
    
    ads.reset()
    ads.continous = 1
    ads.configure()
    ads.start()
    time.sleep(0.2)
    
    sw = TPS2H(gpio, ads)
    sw.set_output(0)

    for k in range(3):
        sw.diag(0, current=1)
        time.sleep(0.1)
        val = sw.measure()
        print("Current: %3.2f" % val)
    
        sw.diag(0, temperature=1)
        time.sleep(0.1)
        val = sw.measure()
        print("Temperature: %3.2f" % val)
    
    sw.clear_output(0)
