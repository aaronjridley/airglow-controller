#!/usr/bin/python3

from components.powercontrol import PowerControl
from config import config
from time import sleep

# Code to shutdown the peripherals that need to be off during the day
# (CCD, Laser, SkyScanner) This is a hedge against the code crashing
# and not going through the power down sequence

powerControl = PowerControl(config['powerSwitchAddress'], \
                            config['powerSwitchUser'], \
                            config['powerSwitchPassword'])

print(" -> Turning off ports")
ports = []
ports.append(config['UsbPowerPort'])
ports.append(config['AndorPowerPort'])
ports.append(config['LaserPowerPort'])
ports.append(config['LaserShutterPowerPort'])
ports.append(config['SledPowerPort'])
for port in ports:
    print('  --> Turning OFF port: ', port)
    powerControl.turnOff(port)
    sleep(2)

