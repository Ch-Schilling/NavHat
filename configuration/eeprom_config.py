###########################################################################################
###
### eeprom_config.py
### ----------------
###
### The tool allows access to software configurable eeproms of the 24cw family.
### One example is Microchip 24cw640T, used as a configuraion memory of Raspberry Pi HAT.
### The bits 0x40 and odd address bit A0CK need to be set correctly for a successful write.
### Permanently locking the configuraiton of the device is not implemented.
### 
### For Raspberry Pi configuraiton, you may need to load a I2C driver like that:
###     sudo dtoverlay i2c-gpio i2c_gpio_sda=0 i2c_gpio_scl=1 bus=9
###
### (c) Ch. Schilling   1. Dec. 2024        Initial release
###
###########################################################################################

import sys, argparse, subprocess

# read the current configuraion from the device
def read_config(v, bus, addr):
    # read 2 bytes from 0x8000 of the memory chip
    sp = subprocess.run(["i2ctransfer", "-y","%s"%args.bus, "w2@0x%02x"%args.address, "0x80", "0x00", "r2"], capture_output=True)
    if v:
        print(sp)
    wp_reg  = int(sp.stdout.decode().split()[0], 16)
    adr_reg = int(sp.stdout.decode().split()[1], 16)
    return(wp_reg, adr_reg)

# show configuraion in clear sentences
def show(v, wp_reg, adr_reg):
    if wp_reg & 0x0e == 0x0e:
        wp_str = "write protection is ON."
    else:
        wp_str = "write protection is OFF."
    if wp_reg & 0x01:
        lock_str = "configuration is locked permanently."
    else:
        lock_str = "configuration is not locked."
    if args.verbose:
        print("Configuration: write protection register 0x%02x, adress register 0x%02x" % (wp_reg, adr_reg))
    print(wp_str)
    print("I2C bus address: 0x%02x" % ((adr_reg & 0x07) + 0x50))
    print(lock_str)
    
    
if __name__ == '__main__':

    # set up the command line parser with corresponding help.
    parser = argparse.ArgumentParser(
        description='configures a software programmable eeprom of the type 24CWxxxT',
        epilog='''
            Examples:\n
            eeprom_config.py -b 9 -a 0x50 --show                shows current configuration\n
            eeprom_config.py -b 9 -a 0x50 --write-protect       activates write protection\n
            eeprom_config.py -b 9 -a 0x50 -wp -t 0x52           activates write protection and sets address to 0x52\n\n
            Use with care at your own risk!''')
    parser.register('type', 'hexadecimal integer', lambda s: int(s, 16))
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    parser.add_argument("-b", "--bus", help="bus the i2c bus to use", default="9")
    parser.add_argument("-a", "--address", help="address is the i2c address of the chip", type='hexadecimal integer', default=0x50)
    parser.add_argument("-s", "--show", help="shows the configuration of the chip", action="store_true")
    parser.add_argument("-t", "--target-address", help="writes the new bus address for future use", type='hexadecimal integer')
    parser.add_argument("-wp", "--write-protect", help="write protects the chip", action="store_true")
    parser.add_argument("-we", "--write-enable", help="removes write protection the chip", action="store_true")
    args = parser.parse_args()
    # print the parsed arguments for debugging reasons
    if args.verbose:
        print(args)

    # read existing configuration
    (wp, ar) = read_config(args.verbose, args.bus, args.address)

    # show configuraion and quit
    if args.show:
        show(args.verbose, wp, ar)
        sys.exit(0)

    # work out new configuration
    if args.write_protect and args.write_enable:
        print("Cannot write anable and write disable at the same time!")
        
    if args.write_protect or args.write_enable or args.target_address:
        # if anything needs to change, these bits have to be set
        wp = wp | 0x40   # enables wirte access to configuration registers.
        ar = ar | 0x40 
    else:
        print("To make a change address or write protection scheme must be set!")
        sys.exit(0)
        
        
    if args.write_protect:
        wp = wp | 0x0e      # enable write protection for full address range

    if args.write_enable:
        wp = wp & ~0x0e     # disable write protection for full address range

    if args.target_address:
        if args.target_address >= 0x50 and args.target_address < 0x58:
            ar = 0x40 | (args.target_address & 0x07) | ((args.target_address & 0x01) << 5)
        else:
            print("Target address is out of range! Use 0x50 to 0x57")
            sys.exit(1)
    else:
        ar = ar + ((ar & 0x01) << 5) # add odd address bit of current address
            
    # write new configuraion
    sp = subprocess.run(["i2ctransfer", "-y","%s"%args.bus, "w4@0x%02x"%args.address, "0x80", "0x00", "0x%02x"%(wp), "0x%02x"%(ar)], capture_output=True)
    if args.verbose:
        print(sp)
