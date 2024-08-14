#!/usr/bin/python3

from config import config
from components.powercontrol import PowerControl
from time import sleep

powerControl = PowerControl(config['powerSwitchAddress'],
                            config['powerSwitchUser'],
                            config['powerSwitchPassword'])

print('Turning off the power ports for the laser.')
ports = ['LaserPowerPort', 'LaserShutterPowerPort']

for port in ports:
    print('Power Port : ', port)
    print('  --> number : ', config[port])
    print('  --> Turning off!')
    powerControl.turnOff(config[port])
    sleep(2)

exit()
