#!/usr/bin/python3

from time import sleep
from components.camera import getCamera
from components.powercontrol import PowerControl
from components.shutterhid import HIDLaserShutter
from datetime import datetime, timedelta
import h5py
import sys
import numpy as np
# Arduino controlling sled needs this:
import serial

from config import config

import argparse

# ----------------------------------------------------------------------  
# Function to parse input arguments                                       
# ----------------------------------------------------------------------

def parse_args():

    parser = argparse.ArgumentParser(description = 'Take images code')
    parser.add_argument('-temp', default = -68, type = int, \
			help='temperature for camera (-68 default)')
    parser.add_argument('-sky', \
                        help='move the sled to sky and close shutter', \
                        action="store_true")
    parser.add_argument('-cal', \
                        help='move the sled to calibration and open shutter', \
                        action="store_true")
    args = parser.parse_args()

    return args

# ----------------------------------------------------------------------
# These are for moving the sled
# ----------------------------------------------------------------------

def move_sled_to_sky(arduino):
    sledPositionSky = b"extend\n"
    dummyRead = arduino.read()
    print('Moving sled to sky')
    arduino.write(sledPositionSky)
    # It takes about 10s to move into place:
    sleep(10)
    return

def move_sled_to_calibrate(arduino):
    sledPositionCalibrate = b"retract\n"
    dummyRead = arduino.read()
    print('Moving sled to calibrate')
    arduino.write(sledPositionCalibrate)
    # It takes about 10s to move into place:
    sleep(10)
    return

# ----------------------------------------------------------------------
# Main code
# ----------------------------------------------------------------------

args = parse_args()


print("Setting a bunch of system things...")

print(" -> Turning on ports")
powerControl = PowerControl(config['powerSwitchAddress'],
                            config['powerSwitchUser'],
                            config['powerSwitchPassword'])
ports = []
ports.append(config['UsbPowerPort'])
ports.append(config['AndorPowerPort'])
ports.append(config['LaserPowerPort'])
ports.append(config['LaserShutterPowerPort'])
ports.append(config['SledPowerPort'])
for port in ports:
    print('  --> Turning ON port: ', port)
    powerControl.turnOn(port)
    sleep(2)

print(" -> Testing Arduino...")
arduino_port = '/dev/ttyACM0'
baud = 9600
# Initialize the Arduino for the calibration sled:
print('  --> Initializing the Arduino to move the sled...')
arduino = serial.Serial(arduino_port, baud)
print('  --> Moving sled to sky')
move_sled_to_sky(arduino)
print('  --> Moving sled to calibrate')
move_sled_to_calibrate(arduino)


# This is just to verify that we can operate the shutter:
lasershutter = HIDLaserShutter(config['vendorId'], config['productId'])
print(' -> Testing shutter by opening it...')
lasershutter.open_shutter()
print(' -> Testing shutter by closing it...')
lasershutter.close_shutter()

exposure = 0.01

print(' -> Initializing Camera...')
camera = getCamera("Andor")

cameraTemp = 10.0
print('  --> Setting Camera Temperature to :', cameraTemp)

# Setup camera
camera.setReadMode()
camera.setImage(hbin=config['hbin'], vbin=config['vbin'])
camera.setShiftSpeed()
camera.setTemperature(cameraTemp)
camera.turnOnCooler()

# Wait until temperature stablize and print the temperature

print('  --> Waiting for camera to cool down:')
while (camera.getTemperature() > cameraTemp):
    print('  --> CCD Temperature: ' + str(camera.getTemperature()))
    sleep(5)

print('  --> Taking Image with exposure : ', exposure)
      
print("  --> Setting read mode to 4 (image)")
camera.setReadMode(4)
print("  --> setting shutter to fully auto mode")
camera.setShutter(1)
print("  --> setting acquision mode to 1")
camera.setAcquisitionMode(1)
print("  --> setting exposure time: ", exposure)
camera.setExposureTime(exposure)

startTime = str(datetime.utcnow())
print('  --> Starting acquisition... ', startTime)
camera.startAcquisition()
sleep(exposure * 0.95)
print('  --> Checking for acquiring signal... ')
while (camera.getStatus() == "DRV_ACQUIRING"):
    print('   ... waiting ... ')
    sleep(exposure * 0.1)
print('  --> Getting image...')
nparr = camera.getImage()

sTimeNow = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
filename = 'image_' + sTimeNow + '.hdf5'
print('  --> Saving image to : ', filename)
data_files = h5py.File(filename, 'w')
f = data_files.create_dataset("image", data=nparr)
f.attrs['ExposureTime'] = exposure
f.attrs['LocalTime'] = startTime 
f.attrs['CCDTemperature'] = camera.getTemperature()
data_files.close()

# Warm the camera back up slowly so that the CCD is not damaged
camera.turnOffCooler()
print('  --> Waiting for camera to warm up')
while (camera.getTemperature() < 15):
    print('  --> CCD Temperature: ' + str(camera.getTemperature()))
    sleep(5)
      
# Shutdown/disconnect camera afterward
print('  --> Shutting down camera') 
camera.shutDown()

for port in ports:
    print('  --> Turning off port: ', port)
    powerControl.turnOff(port)
    sleep(2)

exit()
