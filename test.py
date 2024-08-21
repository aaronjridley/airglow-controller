#!/usr/bin/python3

import os

from datetime import datetime, timedelta
import logging
from time import sleep

import utilities.time_helper
from config import config
from utilities.image_taker import Image_Helper
# Arduino controlling sled needs this:
import serial

from components.camera import getCamera
from components.shutterhid import HIDLaserShutter
from components.powercontrol import PowerControl
import argparse

iDebug = False
log_name = config['log_dir'] + config['site'] + datetime.now().strftime('_%Y%m%d_%H%M%S.log')
logging.basicConfig(filename = log_name, \
                    format = '%(asctime)s %(message)s',  \
                    level = logging.DEBUG)

# ----------------------------------------------------------------------  
# Function to parse input arguments                                     
# ----------------------------------------------------------------------  

def parse_args():

    parser = argparse.ArgumentParser(description = \
                                     'Run the FPI through the night')
    parser.add_argument('-port', default = -1, type = int, \
			help='port to turn on (-1 for no port!)')
    parser.add_argument('-log', \
                        help='Turn on logging and turn off debugging', \
                        action="store_true")
    args = parser.parse_args()

    return args

# ----------------------------------------------------------------------
# Print to the screen or to the log file
# ----------------------------------------------------------------------     

def myprint(value):
    if (iDebug):
        print(value)
    else:
        logging.info(value)
    return

# ----------------------------------------------------------------------
# These are for moving the sled
# ----------------------------------------------------------------------

def move_sled_to_sky(arduino):
    sledPositionSky = b"extend\n"
    dummyRead = arduino.read()
    myprint('Moving sled to sky')
    arduino.write(sledPositionSky)
    # It takes about 10s to move into place:
    sleep(10)
    return

def move_sled_to_cal(arduino):
    sledPositionCalibrate = b"retract\n"
    dummyRead = arduino.read()
    myprint('Moving sled to calibrate')
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

exposureSky = 120.0
exposureLaser = 60.0
doContinue = True
stopFile = 'stop'
nTimes = 8

args = parse_args()
iDebug = not args.log

command = '/bin/rm -f ' + stopFile
os.system(command)

timeHelper = utilities.time_helper.TimeHelper()
sunrise = timeHelper.getSunriseUtcCorrect()
myprint('Sunrise time set to ' + str(sunrise))
sunset = timeHelper.getSunsetUtcCorrect()
myprint('Sunset time set to ' + str(sunset))

ut = datetime.utcnow()

if (sunrise > sunset):
    if (ut < sunset):
        myprint('Need to wait until sunset')
        timeHelper.waitUntilHousekeeping(deltaMinutes=-30)
else:
    myprint('It looks like this script was started after sunset!')
    myprint('Proceeding!')

    
# Turn on power
powerControl = PowerControl(config['powerSwitchAddress'], \
                            config['powerSwitchUser'], \
                            config['powerSwitchPassword'])
sleep(2)
def turn_on(power, port):
    myprint('Turning on power port : %i' % port)
    power.turnOn(port)
    sleep(2)
    return
def turn_off(power, port):
    myprint('Turning off power port : %i' % port)
    power.turnOff(port)
    sleep(2)
    return

turn_on(powerControl, config['AndorPowerPort'])
turn_on(powerControl, config['UsbPowerPort'])
turn_on(powerControl, config['SledPowerPort'])
turn_on(powerControl, config['LaserPowerPort'])
turn_on(powerControl, config['LaserShutterPowerPort'])

timeHelper.waitUntilHousekeeping()

# Get all of the components:
lasershutter = HIDLaserShutter(config['vendorId'], config['productId'])
camera = getCamera("Andor")
arduino = serial.Serial(config['arduino_port'], config['arduino_baud'])

move_sled_to_sky(arduino)
lasershutter.close_shutter()

myprint("  --> Setting read mode to 4 (image)")
camera.setReadMode(4)
camera.setImage(hbin=config['hbin'], vbin=config['vbin'])
camera.setShiftSpeed()

myprint('Setting camera temperature to %.2f C' % config["temp_setpoint"])
camera.setTemperature(config["temp_setpoint"])
camera.turnOnCooler()

# Create data directroy based on the current sunset time
data_folder_name = config['data_dir'] + sunset.strftime('%Y%m%d')
myprint('Creating data directory: ' + data_folder_name)
isExist = os.path.exists(data_folder_name)
if not isExist:
    os.makedirs(data_folder_name)


myprint('Waiting for camera to cool down:')
while (camera.getTemperature() > config["temp_setpoint"]+5):
    myprint('  --> CCD Temperature: ' + str(camera.getTemperature()))
    sleep(5)

myprint("Waiting for sunset: " + str(sunset))
timeHelper.waitUntilStartTimeUtc()
myprint('Sunset time start')
    
myprint('Inititing image taker...')
imageTaker = Image_Helper(data_folder_name, \
                          camera, \
                          config['site'], \
                          config['latitude'], \
                          config['longitude'], \
                          config['instr_name'], \
                          config['hbin'], \
                          config['vbin'], \
                          None)

while (doContinue):
    myprint('Taking bias image - exposure = %5.1f' % config["bias_expose"])
    bias_image = imageTaker.take_bias_image(config["bias_expose"], 0, 0)

    if (timeHelper.beforeSunrise(exposureLaser)):
        move_sled_to_cal(arduino)
        lasershutter.open_shutter()
        myprint('Taking laser image - exposure = %5.1f' % exposureLaser)
        laser_image = \
            imageTaker.take_normal_image('L',
                                         exposureLaser,
                                         0.0, \
                                         0.0, \
                                         None)
        if (os.path.isfile(stopFile)):
            myprint('Stop file exists!')
            doContinue = False
    else:
        doContinue = False
        
    move_sled_to_sky(arduino)
    lasershutter.close_shutter()
    if (doContinue):
        iTime = 0
    else:
        iTIme = nTimes
    while (iTime < nTimes):
        if (timeHelper.beforeSunrise(exposureSky)):
            myprint('Taking sky image - exposure = %5.1f' % exposureSky)
            new_image = \
                imageTaker.take_normal_image('XR',
                                             exposureSky,
                                             0.0, \
                                             0.0, \
                                             None)
            iTime = iTime + 1
            if (os.path.isfile(stopFile)):
                myprint('Stop file exists!')
                doContinue = False
                iTime = nTimes
        else:
            iTime = nTimes
            doContinue = False

    
myprint('Warming up CCD')
camera.turnOffCooler()
while (camera.getTemperature() < -20):
    myprint('CCD Temperature: ' + str(camera.getTemperature()))
    sleep(10)

turn_off(powerControl, config['AndorPowerPort'])
turn_off(powerControl, config['UsbPowerPort'])
turn_off(powerControl, config['SledPowerPort'])
turn_off(powerControl, config['LaserPowerPort'])
turn_off(powerControl, config['LaserShutterPowerPort'])
    
