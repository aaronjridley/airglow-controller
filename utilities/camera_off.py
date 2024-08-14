#!/usr/bin/python3

from config import config
from components.powercontrol import PowerControl
from components.camera import getCamera
from time import sleep

powerControl = PowerControl(config['powerSwitchAddress'], \
                            config['powerSwitchUser'], \
                            config['powerSwitchPassword'])

camera = getCamera("Andor")
print('Turning off the cooler on the camera.')
camera.turnOffCooler()
print('  --> Waiting for the CCD temp to reach 10C.')
while (camera.getTemperature() < 10):
    print('  --> CCD Temperature: ' + str(camera.getTemperature()))
    sleep(5)
      
# Shutdown/disconnect camera afterward
print('Shutting down camera.')
camera.shutDown()
sleep(2)

print('Turning off the power port for the camera.')
ports = ['AndorPowerPort']

for port in ports:
    print('Power Port : ', port)
    print('  --> number : ', config[port])
    print('  --> Turning off!')
    powerControl.turnOff(config[port])
    sleep(2)

exit()
