## Drivers

To make full advantage of the board, two drivers need attention: the CAN device MCP25625 and the quad UART MAX14830. These communication devices share one oscillator. The CAN chip needs to be configured to provide a clock output which is used as a clock input for the quad UART device. The quad UART driver is not included in the kernel by default, it must be added as max310x module. 
The clock output did not find attention by the kernel maintainers, so far. A patch is added that allows a user friendly configuration of the clock output signal.

To compile the kernel follow these well [documented steps of the raspberry pi documentation.](https://www.raspberrypi.com/documentation/computers/linux_kernel.html#configure-the-kernel)

To enable the quad UART max14830, make sure the .config shows this driver as a module:
```
CONFIG_SERIAL_MAX310X=m
```
Add the patch for the mcp250x driver and corresponding device tree files or swap the entire kernel source files.
Compile the kernel afterwards.


### CAN driver
To configure the output clock CLKOUT, a field was introduced in the mcp2515-can0-overlay.dts device tree overlay file.
```
          clkout-prescale = <0>;
```

The driver looks for that entry during probing and sets the CANCTRL register accordlingly. A value of 0 does not enable clock output and remains the output low. In this case, the driver behaves no different than the original version does.
Valid parameters for clkout-prescale are 1,2,4 and 8 which divides the input clock by 1 (same frequency), 2 ,4 or 8 respectively.

This information can be found by the driver using device_property interface during probing:
```
	/* check clkout property and convert it to register value */
	if(device_property_present(&spi->dev, "clkout-prescale")) {
		dev_info(&spi->dev, "clkout-prescale: found\n");
		device_property_read_u32(&spi->dev, "clkout-prescale", &clkout_prescale);
		dev_info(&spi->dev, "clkout-prescale found: %d\n", clkout_prescale);
		if(clkout_prescale) {
			if (clkout_prescale > 8)
				return -ERANGE;

			clkout_prescale = (clkout_prescale >> 1);
			clkout_prescale = (clkout_prescale == 4 ? 3 : clkout_prescale) | CANCTRL_CLKEN;
			dev_info(&spi->dev, "(CS) clkout-prescale register value: 0x%02x.", clkout_prescale);
		}
	}
	...
```
This is for illustration only, no actions needed for commissioning.

### UART driver
The driver for the MAX14830 works without modification but a device tree overlay is needed to hook it correctly in the SPI 1 bus. The following line creates a device-tree blop which needs to be copied to /boot/firmware/overlays using root priviledges.
```
dtc -@  -O dtb -I dts -o max14830-spi1.dtbo max14830-spi1-overlay.dts 
```

Describing the clock input is 2.5MHz, 1/8 of the 20MHz oscillator for the CAN device. The UART uses a PLL and internal prescaler to adjust the baudrate as close as pssible to the desired one. Below are exceprts from max14830-spi1-overlay.dts.
```
	fragment@3 {
		target-path = "/clocks";

		__overlay__ {
			max14830_xtal: max14830_xtal {
				compatible = "fixed-clock";
				#clock-cells = <0>;
				clock-frequency = <2500000>;
			};
		};

	};
```
Also, clock-names has to be "osc" for an external input. "xtal" is used for a quarz.
```
	fragment@1 {
		target = <&spi1>;

		__overlay__ {
			#address-cells = <1>;
			#size-cells = <0>;

			pinctrl-names = "default";
			pinctrl-0 = <&spi1_pins &spi1_cs_pins>;

			cs-gpios = <&gpio 17 1>;  //GPIO_ACTIVE_LOW>;
			status = "okay";

			max14830: max14830@0 {
				compatible = "maxim,max14830";
				reg = <0>;

				#address-cells = <1>;
				#size-cells = <0>;
				gpio-controller;
				#gpio-cells = <2>;

				spi-max-frequency = <5000000>;
				interrupts = <12 8>; // 2:IRQ_TYPE_EDGE_FALLING>;  8:low
				interrupt-parent = <&gpio>;

				pinctrl-0 = <&int_pins>;
				pinctrl-names = "default";

				clocks = <&max14830_xtal>;
				clock-names = "osc";
			};
		};
	};

```
It seemed that some interupts got lost when the interrupt signal was configured as falling edge. Setting it to low (8) seems to solve that problem.

To load these drivers at boot time, make sure they are mentioned in the /boot/firmware/config.txt file:
```
...
dtparam=spi=on
dtoverlay=mcp2515-can0,oscillator=20000000,interrupt=25,spimaxfrequency=2000000,clkoutprescale=8
dtoverlay=max14830-spi1
...
```

If configured correctly the two drivers appear in dmsg after reboot.
```
...
[   11.391625] mcp251x spi0.0: clkout-prescale: 4
[   11.417303] mcp251x spi0.0 can0: MCP2515 successfully initialized.
...
[   11.471622] spi1.0: ttyMAX0 at I/O 0x0 (irq = 172, base_baud = 3750000) is a MAX14830
[   11.479118] spi1.0: ttyMAX1 at I/O 0x1 (irq = 172, base_baud = 3750000) is a MAX14830
[   11.483086] spi1.0: ttyMAX2 at I/O 0x2 (irq = 172, base_baud = 3750000) is a MAX14830
[   11.483433] spi1.0: ttyMAX3 at I/O 0x3 (irq = 172, base_baud = 3750000) is a MAX14830
...
```

The CAN driver mcp251x displays the clkout-prescale if found and its successful initialization. The single nodes of the UART can be accessed using /dev/ttyMAX0 ... /dev/ttyMAX3. Make sure to turn off hardware handshaking, because these lines are not wired. The upper two (ttyMAX2 and ttyMAX3) can be configured to use the RS-232 level shifter or to keep the TTL signals. Enable and shutdown of the the level shifter are controlled by GPIO0 and GPIO1 of the UART. Since the UART device acts as a standard gpio controller these lines can be set as follows:
```
gpioset --drive=push-pull gpiochip14 0=1 1=0
```
Sets GPIO0 to high and GPIO1 to low, which disables the level shifter.

```
gpioset --drive=push-pull gpiochip14 0=0 1=1
```
Sets GPIO0 to high and GPIO1 to low, which enables the level shifter.

Depending on the configuration, gpiochip14 might not be the correct device. Try to use gpiodetect to find the correct one.
```
user@raspberrypi:~ $ gpiodetect
gpiochip0 [pinctrl-rp1] (54 lines)
gpiochip10 [gpio-brcmstb@107d508500] (32 lines)
gpiochip11 [gpio-brcmstb@107d508520] (4 lines)
gpiochip12 [gpio-brcmstb@107d517c00] (17 lines)
gpiochip13 [gpio-brcmstb@107d517c20] (6 lines)
gpiochip14 [MAX14830] (16 lines)
gpiochip0 [pinctrl-rp1] (54 lines)
```
gpioinfo shows the status of all GPIO signals of the system:
```
...
gpiochip14 - 16 lines:
        line   0:      unnamed       unused  output  active-high 
        line   1:      unnamed       unused  output  active-high 
        line   2:      unnamed       unused   input  active-high 
        line   3:      unnamed       unused   input  active-high 
...
```

To see how much data was transferred by the four UARTs as well as the line stati, check the driver information:
```
user@raspberrypi:~ $ sudo cat /proc/tty/driver/max310x
serinfo:1.0 driver revision:
0: uart:MAX14830 port:00000000 irq:172 tx:0 rx:0 DSR|CD
1: uart:MAX14830 port:00000001 irq:172 tx:0 rx:0 DSR|CD
2: uart:MAX14830 port:00000002 irq:172 tx:0 rx:0 DSR|CD
3: uart:MAX14830 port:00000003 irq:172 tx:0 rx:0 DSR|CD
```
