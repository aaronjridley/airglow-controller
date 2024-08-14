#!/usr/bin/python3

from config import config
from components.powercontrol import PowerControl
from time import sleep

powerControl = PowerControl(config['powerSwitchAddress'], \
                            config['powerSwitchUser'], \
                            config['powerSwitchPassword'])

print('Turning Sled on!')
print('  --> Power Port for Sled : ', config['SledPowerPort'])
powerControl.turnOn(config['SledPowerPort'])
sleep(2)

exit()
