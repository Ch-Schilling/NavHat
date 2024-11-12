# Navigation HAT
The Navigation HAT is a board that connects on top of the Raspberry Pi computer by its 40 pin header. HAT stands for Hardware-Attached-on-Top, the specification can be found [here](https://datasheets.raspberrypi.com/hat/hat-plus-specification.pdf).

![Rendered NavHAT board](./images/NavHAT-angle.png)

## Purpose
Navigation HAT is made to help embed the Raspberry Pi in a sailing boat. Of course, it can be used in many other use cases where the hardware features make sense.
On a sailing boat, one is consious about power consumption. Navigation HAT uses a wide input range, high efficiency and low noise step-down switcher. In operation, powered from the battery of the boat, its efficiency is approx. 95%.
In standby, it uses only a few µA. It can be woken up by a key or by the on-board real time clock (RTC).
Most boats use NMEA 2000 for information exchange between instruments, plotter, autopilot etc. The bus is based on CAN, therefore an important interface is the CAN bus. Older boats might use NMEA 0183, which is based on RS-422. Two UARTs in RS-422 configuration are populated as well.
To control other loads on the boat, there are four power outputs with current limitation and monitoring as well as other protective features. Barometric readings are essential for wheather observation. A high sensitivity barometric sensor is included. Several connectors are ready for attaching other sensors using a two-wire bus.

## Installation
The HAT is connected to the Raspberry Pi computer with the 40 pin header. Start connecting battery power to J1. 16mm M2.5 spacer can be used to mechanically fix the boards.

### Powering the system
J1 is the large screw terminal providing power to the system and connecting loads conrolled by the high-side switches. Positive voltage from the battery is connected closest to the fuses.

|Pin|Connection|
|:--|:---------|
|1|P1 Output|
|2|P2 Output|
|3|P3 Output|
|4|P4 Output|
|5|GND, Battery -|
|6|Supply, Battery +|

The screw terminals take wire sizes up to 2.5mm<sup>2</sup>.

### NMEA 2000 interface
J8 is the small screw terminal for the NMEA 2000 or CAN bus interface. Pin 1 is closest to the fuses.

|Pin|Connection|Color|
|:--|:----|:-------|
|1  |GND  |metallic|
|2  |CAN -|blue    |
|3  |CAN +|white   |

The colors refer to the NMEA cable specification. Use the metallic shield for ground connection.

### Power-on and RTC backup
J6 is reserved for RTC battery or super capacitor as well as the power-on button to switch the flip-flop and therefore start the DC/DC switcher.

|Pin|Connection|
|:--|:-------|
|1|GND       |
|2|VBATT_RTC |
|3|POWER_ON  |
|4|GND       |

Connect POWER_ON to GND for an instant to turn on the system. This is a good application for a power button. 
> Note: It is planned to use the button during operation as a signal and long-press to initiate shut-down. This is not implemented, yet.

### One-Wire
J2 offers a One-Wire interface. The Bit-banging driver of the Raspberry Pi is used. There is a 5kOhm pull-up resistor on board for a seamless start.

|Pin|Connection|
|:--|:------|
|1|GND      |
|2|One-Wire |
|3|+3.3V    |
|4|+5V      |

The +5V is directly connected to the output of the DC/DC converter. +3.3V is made by the Raspberry Pi and is taken from the 40Pin header. Pin 1 is at the Label J2 or closest to J1.

### Auxilary header J7
J7 offers differential signals to the ADC inclusive external differential reference voltage. Four GPIOs from the Port extender, I2C and a linear 3.3V supply are fed to that header as well.

|Signal    |Pin|Pin|Signal       |
|:---------|:-:|:-:|:------------|
| GND      | 1 | 2 | LIN3V3      |
| SCL      | 3 | 4 | SDA         |
| GPIO_A4  | 5 | 6 | AIN3        |
| GPIO_A3  | 7 | 8 | AIN2        |
| GPIO_A2  | 9 | 10| REF_N       |
| GPIO_A1  | 11| 12| REF_P       |
| GND      | 13| 14| CurSenseRef |
| POWER_ON | 15| 16| CurSense    |

The current sense signals are hooked up to that header, too. Removing R47 and R50 looses current sense of the power outputs in favour of additional external analogue voltages.

### STEMMA connectors J3 and J4
Two STEMMA connectors for external I2C devices are available. For reference, these signal are hooked up:

|Pin|Signal|
|:--|:-----|
|1 |SCL    |
|2 |SDA    |
|3 |LIN3V3 |
|4 |GND    |

### STEMMA QT / Qwiic connector J5
The miniature version of STEMMA can be used on J5. For reference, these signal are hooked up:

|Pin|Signal|
|:--|:-----|
|1 |GND    |
|2 |+3.3VA |
|3 |SDA    |
|4 |SCL    |

> Note: +3.3VA is powered from a linear regulator and is active, even when the DC/DC converter is disabled.

### NMEA 0183 / serial connectors
J9 and J10 are connectors for RS-232 and RS-422. Details will be updated later.


## Design
The design is made using KiCad. It is impressive how well that open source system is capable of drawing schematics and designing PCBs! Cudos to the KiCad team. Get the design files from the KiCad folder.
The board is designed for four copper layers to achieve the densitiy needed for the small footprint of the HAT as well as thermal and EMI reasons. For easyer manufacturing, components are populated on the top side only. KiCad and open hardware logos are printed on the bottom side of the board.

### Power Supply
To operate a Raspberry Pi with Navigation HAT independent of other installation, two fuses are on board. F1 (approx. 3A) is installed in the path of the power supply for the Raspberry Pi, F2 (apporx. 20A) is in place for the four power outlets.
To achieve high efficiency, low noise, low stand-by current and a wide voltage input the TI LM62460 was chosen. The part also offers a wide range switching frequency and a spread spectrum option. To optimize efficiency, the switching frequency is set to 488kHz. Higher frequencies would allow to use smaller inductors. An EMI filter is used at the battery side. Electrolythic capacitors are waived, purely ceramic capacitors are used. See schematics page 2 and the [datasheet](https://www.ti.com/product/de-de/LM62460) of the manufacturer.
The Enable signal EN_POWER of the device is controlled by a flip-flop U4. EN_POWER is high and remains high if POWER_ON gets low by an external signal like a button, power-on cycle or an interrupt of the RTC. The flip-flop consumes very little power, it has to remain on by a low Iq linear regulator U2. In case of shutting down the Raspberry Pi, the gpio-poweroff driver is used to rise the clock signal of the flip-flop, disabling the DC/DC converter and put it into µA current consumption sleep mode. To do so, this needs to be added in the /boot/firmware/config.txt file:
```
dtoverlay=gpio-poweroff,gpiopin=5,active-delay-ms=1000
```
The active-delay is not mandatory, but seems to be a good idea.
> Note: Make sure that there are no pending interrups of the RTC, otherwise the flip-flop cannot change state and turn off the DC/DC converter.

### Power Outlets
To control lights, relays or board instruments 4 power outlets are available. The high side switches family [TPS2HB](https://www.ti.com/product/TPS2HB16-Q1) of TI is used. The parts provide low R_on resistance, current limiter and -monitoring as well as temperature monitoring. Made for the automotive market, they seem to be a good fit for boating applications, too. The parts are controlled via a I2C port extension device MCP23017. To save the part from reverse polarity 15kOhm resistors are used in all digital paths as described in the application notes.
A fraction of the output current can be fed throug a sense resistor to measure the output current. The voltage across the shunt resistor can be measured by the on-board ADC. Optionally, the first two switches can be controlled by the PWM engine of the Raspberry Pi. Please be aware that not all features of that mini computer can be used at the same time.

### NMEA Interfaces
The NMEA 2000, CAN interface is implemented using a Microchip MCP25625. The MCP25625 is a more modern and compact device containing a MCP2515 and corresponding driver. It creates a one chip solution from SPI to CAN bridge. From the Raspberry Pi's perspecive the MCP2515 driver is used. Make sure the /boot/firmware/config.txt contains the following:
```
dtparam=spi=on
dtoverlay=mcp2515-can0,oscillator=20000000,interrupt=25,spimaxfrequency=2000000
```
In a console, configure the CAN bus for NMEA 2000:
```
sudo ip link set can0 up type can bitrate 250000
sudo ip link set can0 txqueuelen 65536
```
Check for can0 interface using
```
ip link
```
For more details pyssel describes to setup NMEA 2000 with a CAN HAT on their [webpage](https://pysselilivet.blogspot.com/2022/05/waveshare-can-hat-with-signal-k.html)

For NMEA 0183 devices and/or other serial devices, a MAX14830 bridges SPI to quad UART. The first two UARTs are converted into RS-422 signals and fed to connector J9. The last two UARTs can be converted to RS-232 signals and fed to connector J10. One can use the TTL signals but one has to disable the converter chip U13 and put it into shutdown mode. The quad UART U12 could have its own quatz, since it has a wide possibility of options to create its clocks, the clockout of the CAN chip U9 shall be used instead.
The CAN and RS-422 interfaces have an option of a termination resistor of typically 120Ohm, but these resistors are not populated by default. ESD protection diodes are used except for the RS-422 devices, they have large enough built-in protection.

> Note: The quad UART is not commissioned yet!

### Sensors and Sensor Interfaces
There are a wide variety of sensors with I2C interface. On board, the following parts share the user accessible I2C bus of the Raspberry Pi:
* MCP23017 I/O Port extension for controlling the power outlets
* ADS1119 analog to digital converter for measuring current and temperature of the power outlets
* MAX31343 RTC for wake up calls
* BMP390 barometric pressure sensor

The BMP390 is susceptible to stress. It is placed at the edge of the board in between two cutouts. Stress to the board is not passed to the part where the sensor is soldered to.
  
There are two [STEMMA](https://learn.adafruit.com/introducing-adafruit-stemma-qt/what-is-stemma) connectors J3 and J4 as well as a STEMMA QT / Qwiic connector J5. The power pin of J5 is hooked up from linear regulator U2. It provides 3.3V even if the main DC/DC converter is switched off. This allows low power sensors to continue to operate without operation of the computer. The header J7 also carries the two I2C signals. There should be plenty of options to add I2C sensors to the system.
Connector J2 is prepared for 1-wire devices inclusive 5kOhm pull-up and 3.3V and 5V to chose from.

A nice option for environmental monitoring of temperature and humidity, the part HDC3020 can be used. It is not on board because the environment of the computer system is typically not representative for the environment to be monitored. The part continues to measure these parameters, even if there is no I2C communication. It stores the minimum and maximum measurements of temperature and rel. humidity. This is an excellent choise to connect to J5 to be powered, even whten the Raspberry Pi is off. The computer can read the min. and max. readings when it is awake again.

### Configuration
Page 6 of the schematics shows hardware configurations of the board. The HAT specification requires a EEPROM describing the HAT and holds information about power delivery and required drivers. Unlike the proposal of the HAT specification, a software configurable EEPROM is used. This allows to set the I2C address as well as the write protection of the device. Gaining write access to the device from user space is relatively complicated, therefore an accidential write access is highly unlikely.
Chip select and interrup pin for the CAN- and UART controller are prepared for two options. The options can be chosen by using the corresponding resistor.
The signal I2C_ADDR0 can be set to logic 0 or logic 1. It is connected to the lowest address bit of the pressure sensor U5, the ADC U8 and the port extender U15. The I2C address of these devices can be rised by 1 commonly in case of conflict with other devices.

The following table shows the I2C addresses of the different devices. A0 corresponds to the configuration of the I2C_ADDR0 which can be set by the resistors R56 and R57. A0 = 0 if R57 is populated and A0 = 1 if R56 is populated, respectively.
|Device|Address|
|:-----|:------|
|MCP23017|0x22 + A0|
|BMP390|0x76 + A0|
|ADS1119|0x48 + A0|
|MAX31343|0x68|
|HDC3020|0x44|
