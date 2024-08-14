#!/usr/bin/python3

from time import sleep
from components.camera import getCamera
from datetime import datetime, timedelta
import h5py
import sys
import numpy as np
# Arduino controlling sled needs this:
import serial

from config import config
from components.shutterhid import HIDLaserShutter

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
# This is for removing hotspots from the image, not used by default
# ----------------------------------------------------------------------        

def remove_hotspots(image):

    newImage = image

    std = np.std(newImage)
    med = np.median(newImage)
    accMax = med + 10.0 * std
    actMax = np.max(newImage)
    print('Acceptable max : ',accMax)
    print('Actual max     : ',np.max(newImage))

    if (accMax < actMax):
        print('Replacing hot spot pixels...')
        newImage[newImage > accMax] = med
    
    print(np.min(newImage), \
          np.mean(newImage), \
          np.median(newImage), \
          np.max(newImage))
    
    return newImage
    
# ----------------------------------------------------------------------        
# Main code
# ----------------------------------------------------------------------        

args = parse_args()

IsSky = args.sky

if (args.cal):
    IsSky = False
    print('Setting up for LASER CALIBRATION measurements')
else:
    print('Setting up for SKY measurements')

    
arduino_port = '/dev/ttyACM0'
baud = 9600

cameraTemp = args.temp
print('Setting Camera Temperature to :', cameraTemp)

# This is just to verify that we can operate the shutter:
lasershutter = HIDLaserShutter(config['vendorId'], config['productId'])
print('Testing shutter by closing it...')
lasershutter.close_shutter()


# Initialize the Arduino for the calibration sled:
print('Initializing the Arduino to move the sled...')
arduino = serial.Serial(arduino_port, baud)

exposure = 2

print('Initializing Camera...')
camera = getCamera("Andor")

# Setup camera
camera.setReadMode()
camera.setImage(hbin=config['hbin'], vbin=config['vbin'])
camera.setShiftSpeed()
camera.setTemperature(cameraTemp)
camera.turnOnCooler()

# Wait until temperature stablize and print the temperature

print('Waiting for camera to cool down:')
while (camera.getTemperature() > desired_temp+2):
    print('  --> CCD Temperature: ' + str(camera.getTemperature()))
    sleep(5)

if (IsSky):
    print('Sending Laser Shutter Close Signal...')
    lasershutter.close_shutter()      
    print('Moving sled to sky')
    move_sled_to_sky(arduino)
else:
    print('Opening Laser Shutter...')
    lasershutter.open_shutter()
    print('Moving sled to calibrate')
    move_sled_to_calibrate(arduino)

    
while (exposure > 0):

    sExposure = 'Enter exposure (%d, 0 to exit) : ' % exposure
    value = input(sExposure)
    if (len(value) > 0):
      exposure = int(value)
    else:
      exit()

    print('Taking Image...')
      
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
    if (exposure > 10):
        sleep(exposure - 2)
    else:
        sleep(exposure/2)
    print('  --> Checking for acquiring signal... ')
    while (camera.getStatus() == "DRV_ACQUIRING"):
        print('   ... waiting ... ')
        sleep(2)
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

print('Done aquiring images!')
print("  --> Closing Laser Shutter...")
lasershutter.close_shutter()      

# Warm the camera back up slowly so that the CCD is not damaged
camera.turnOffCooler()
print('  --> Waiting for camera to warm up')
while (camera.getTemperature() < 10):
    print('  --> CCD Temperature: ' + str(camera.getTemperature()))
    sleep(5)
      
# Shutdown/disconnect camera afterward
print('  --> Shutting down camera') 
camera.shutDown()

print('')
print('Nothing is turned off, so you will need to do this manually!')
print('')

exit()
