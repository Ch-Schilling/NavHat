
dtc -@ -O dtb -I dts -o power-5A.dtbo power-5A.dts

eepmake  -v1 eeprom_navhat.txt eeprom_navhat.eep power-5A.dtbo

sudo eepflash.sh -w -f eeprom_navhat.eep -d=9 -t=24c64
