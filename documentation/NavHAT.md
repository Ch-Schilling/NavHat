# Navigation HAT
The Navigation HAT is a board that connects on top of the Raspberry Pi computer. HAT stands for Hardware-Attached-on-Top, the specification can be found [here](https://datasheets.raspberrypi.com/hat/hat-plus-specification.pdf).

![Rendered NavHAT board](./images/NavHAT-angle.png)

## Purpose
Navigation HAT is made to help embed the Raspberry Pi in a sailing boat. Of course, it can be used in many other use cases where the hardware features make sense.
On a sailing boat, one is consious about power consumption. Navigation HAT uses a wide input range, high efficiency and low noise step-down switcher. In operation, powered from the battery of the boat, its efficiency is approx. 95%.
In standby, it uses only a few µA. It can be woken up by a key or by the on-board real time clock (RTC).
Most boats use NMEA 2000 for information exchange between instruments, plotter, autopilot etc. The bus is based on CAN, therefore an important interface is to the CAN bus. Older boats might use NMEA0183, which is based on RS-422. Two UARTs in RS-422 configuration are populated as well.
To control other loads on the boat, there are four power outputs with current limitation and monitoring as well as other protective features. Barometric readings are essential for wheather observation. A barometer sensor is included on the board. Several connectors are ready for attaching other sensors using a two-wire bus.

## Installation

## Design
The design is made using KiCad. It is impressive how well that open source system is capable of drawing schematics and designing PCBs! Cudos to the KiCad team. Get the design files from the KiCad folder.
The board is designed for four coopper layers to achieve the densitiy needed for the small footprint of the HAT as well as thermal and EMI reasons.

### Power Supply
To operate a Raspberry Pi with Navigation HAT independent of other installation, two fuses are on board. F1 (approx. 3A) is installed in the path of the power supply for the Raspberry Pi, F2 (apporx. 20A) is in place for the four power outlets.
To achieve high efficiency, low noise, low stand-by current and a wide voltage input the TI LM62460 was chosen. The part also offers a wide range of the switching frequency and a spread spectrum option. To optimize efficiency, the switching frequency is set to 488kHz. Higher frequencies would allow to use smaller inductors. An EMI filter is used at the battery side. Electrolythic capacitors are waived, purely ceramic capacitors are used. See schematics page 2 and the [datasheet](https://www.ti.com/product/de-de/LM62460) of the manufacturer.

### Power Outlets
To control lights, relays or board instruments 4 power outlets are available. The high side switches family [TPS2HB](https://www.ti.com/product/TPS2HB16-Q1) of TI is used. The parts provide low R_on resistance, current limiter and -monitoring as well as temperature monitoring. Made for the automotive market, the seem to be a good fit for boating applications, too. The parts are controlled via a I2C port extension MCP23017. To save the part from reverse polarity 15kOhm resistors are used in all digital paths as described in the application notes.
A fraction of the output current can be fed throug a sense resistor to measure the output current. The voltage across the shunt resistor can be measured by the on-board ADC. Optionally, the first two switches can be controlled by the PWM engine of the Raspberry Pi. Please be aware that not all features of that mini computer can be used at the same time.

### NMEA Interfaces

### Sensors and Sensor Interfaces


