#!/usr/bin/python3

from config import config
from components.powercontrol import PowerControl
from time import sleep

powerControl = PowerControl(config['powerSwitchAddress'], \
                            config['powerSwitchUser'], \
                            config['powerSwitchPassword'])

ports = ['UsbPowerPort', 'AndorPowerPort']

for port in ports:
    print('Power Port : ', port)
    print('  --> number : ', config[port])
    print('  --> Turning on!')
    powerControl.turnOn(config[port])
    sleep(2)

exit()
