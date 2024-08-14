#!/usr/bin/python3

from config import config
from components.powercontrol import PowerControl
from time import sleep

from components.shutterhid import HIDLaserShutter

lasershutter = HIDLaserShutter(config['vendorId'],
                               config['productId'])

sleep(2)
print('Closing shutter ...')
lasershutter.close_shutter()

powerControl = PowerControl(config['powerSwitchAddress'],
                            config['powerSwitchUser'],
                            config['powerSwitchPassword'])

ports = ['AndorPowerPort',
         'SledPowerPort',
         'UsbPowerPort',
         'LaserPowerPort',
         'LaserShutterPowerPort']

for port in ports:
    print('Power Port : ', port)
    print('  --> number : ', config[port])
    print('  --> Turning off!')
    powerControl.turnOff(config[port])
    sleep(2)

exit()
