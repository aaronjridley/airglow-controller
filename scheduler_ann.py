#!/usr/bin/python3

import os
import sys
import logging
import signal
import scipy
import numpy
import pickle
from time import sleep
from datetime import datetime, timedelta
import smtplib, ssl
from config import config
from schedule import observations
# Arduino controlling sled needs this:
import serial

import utilities.time_helper
from utilities.image_taker import Image_Helper
#from utilities.send_mail import SendMail

from components.camera import getCamera
from components.shutterhid import HIDLaserShutter
from components.powercontrol import PowerControl



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


try:
    # logger file
    log_name = config['log_dir'] + config['site'] + datetime.now().strftime('_%Y%m%d_%H%M%S.log')
    logging.basicConfig(filename=log_name, encoding='utf-8',
                        format='%(asctime)s %(message)s',  level=logging.DEBUG)


    timeHelper = utilities.time_helper.TimeHelper()
    sunrise = timeHelper.getSunrise()
    logging.info('Sunrise time set to ' + str(sunrise))
    sunset = timeHelper.getSunset()
    logging.info('Sunset time set to ' + str(sunset))

    # 30 min before house keeping time
    timeHelper.waitUntilHousekeeping(deltaMinutes=-30)

    # Turn on power
    powerControl = PowerControl(config['powerSwitchAddress'], config['powerSwitchUser'], config['powerSwitchPassword'])
    powerControl.turnOn(config['AndorPowerPort'])
    powerControl.turnOn(config['UsbPowerPort'])
    powerControl.turnOn(config['SledPowerPort'])
    powerControl.turnOn(config['LaserPowerPort'])
    powerControl.turnOn(config['LaserShutterPowerPort'])

    logging.info('Waiting until Housekeeping time: ' +
                str(timeHelper.getHousekeeping()))
    timeHelper.waitUntilHousekeeping()

    # Housekeeping
    lasershutter = HIDLaserShutter(config['vendorId'], config['productId'])
    camera = getCamera("Andor")

    # Initialize the Arduino for the calibration sled:
    logging.info('Initializing the Arduino to move the sled...')
    arduino = serial.Serial(config['arduino_port'], config['arduino_baud'])

    # Signal to response to interupt/kill signal
    def signal_handler(sig, frame):
        move_sled_to_sky(arduino)
        lasershutter.close_shutter()
        camera.turnOffCooler()
        camera.shutDown()
        powerControl = PowerControl(config['powerSwitchAddress'], config['powerSwitchUser'], config['powerSwitchPassword'])
        powerControl.turnOff(config['AndorPowerPort'])
        powerControl.turnOff(config['LaserPowerPort'])
        logging.info('Exiting')
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)

    move_sled_to_sky(arduino)
    lasershutter.close_shutter()

    #print("  --> setting shutter to fully auto mode")
    #camera.setShutter(1)
    #print("  --> setting acquision mode to 1")
    #camera.setAcquisitionMode(1)
    #print("  --> setting exposure time: ", exposure)
    #camera.setExposureTime(exposure)
    # Setup camera
    logging.info("  --> Setting read mode to 4 (image)")
    camera.setReadMode(4)
    camera.setImage(hbin=config['hbin'], vbin=config['vbin'])
    camera.setShiftSpeed()
    camera.setTemperature(config["temp_setpoint"])
    camera.turnOnCooler()
    logging.info('Set camera temperature to %.2f C' % config["temp_setpoint"])


    logging.info("Waiting for sunset: " + str(sunset))
    timeHelper.waitUntilStartTime()
    logging.info('Sunset time start')

    # Create data directroy based on the current sunset time
    data_folder_name = config['data_dir'] + sunset.strftime('%Y%m%d')
    logging.info('Creating data directory: ' + data_folder_name)
    isExist = os.path.exists(data_folder_name)
    if not isExist:
        os.makedirs(data_folder_name)

    imageTaker = Image_Helper(data_folder_name, camera,
                            config['site'], config['latitude'], config['longitude'], config['instr_name'], config['hbin'], config['vbin'], SkyAlert(config['skyAlertAddress']))

    # Take initial images
    if datetime.now() < (sunset + timedelta(minutes=10)):
        bias_image = imageTaker.take_bias_image(config["bias_expose"], 0, 0)
        dark_image = imageTaker.take_dark_image(config["dark_expose"], 0, 0)
        laser_image = imageTaker.take_laser_image(
            config["laser_expose"], skyscanner, lasershutter, config["azi_laser"], config["zen_laser"], fw, filterwheel_config["laser_position"])
        if config['laser_timedelta'] is not None:
            config['laser_lasttime'] = datetime.now()
    else:
        logging.info('Skipped initial images because we are more than 10 minutes after sunset')
        if config['laser_timedelta'] is not None:
            config['laser_lasttime'] = datetime.now()


    # Main loop
    while (datetime.now() <= sunrise):
        for observation in observations:
            if (datetime.now() >= sunrise):
                logging.info('Inside observation loop, but after sunrise! Exiting')
                break
            
            currThresholdMoonAngle = skyscanner.get_moon_angle(config['latitude'], config['longitude'], observation['skyScannerLocation'][0], observation['skyScannerLocation'][1])
            logging.info('The current Moon angle Threshold is: %.2f' % currThresholdMoonAngle)
            if (currThresholdMoonAngle <= config['moonThresholdAngle']):
                logging.info('The moonThreshold angle was too small. The current threshold moon angle is:  %.2f' % currThresholdMoonAngle + 
                ' the current direction of telescope is az: %.2f ze: %.2f' % (
                    observation['skyScannerLocation'][0], observation['skyScannerLocation'][1]))   
                continue

            logging.info('Moving SkyScanner to: %.2f, %.2f' % (
                observation['skyScannerLocation'][0], observation['skyScannerLocation'][1]))
            skyscanner.set_pos_real(
                observation["skyScannerLocation"][0], observation['skyScannerLocation'][1])
            world_az, world_zeni = skyscanner.get_world_coords()
            logging.info("The Sky Scanner has moved to azi: %.2f, and zeni: %2f" %(world_az, world_zeni))

            # Move the filterwheel
            logging.info('Moving FilterWheel to: %d' % (observation['filterPosition']))
            fw.go(observation['filterPosition'])
            logging.info("Moved FilterWheel")

            logging.info('Taking sky exposure')

            if (observation['lastIntensity'] == 0 or observation['lastExpTime'] == 0):
                observation['exposureTime'] = observation['defaultExposureTime']
            else:
                observation['exposureTime'] = min(0.5*observation['lastExpTime']*(1 + observation['desiredIntensity']/observation['lastIntensity']),
                                                config['maxExposureTime'])

            logging.info('Calculated exposure time: ' +
                        str(observation['exposureTime']))

            # Take image
            new_image = imageTaker.take_normal_image(observation['imageTag'],
                                                    observation['exposureTime'],
                                                    observation['skyScannerLocation'][0],
                                                    observation['skyScannerLocation'][1], skyscanner)

            image_sub = scipy.signal.convolve2d(
                new_image[config['i1']:config['i2'], config['j1']:config['j2']], numpy.ones((config['N'], config['N']))/config['N']**2, mode='valid')
            image_intensity = (numpy.percentile(image_sub, 75) - numpy.percentile(
                image_sub, 25))*numpy.cos(numpy.deg2rad(observation['skyScannerLocation'][1]))

            observation['lastIntensity'] = image_intensity
            observation['lastExpTime'] = observation['exposureTime']

            logging.info('Image intensity: ' + str(image_intensity))

            # Check if we should take a laser image
            logging.info('Time since last laser ' +  str(datetime.now() - config['laser_lasttime']))
            take_laser = (datetime.now() - config['laser_lasttime']) > config['laser_timedelta']
            logging.info('Take_laser is ' + str(take_laser))
            if take_laser:
                world_az, world_zeni = skyscanner.get_world_coords()
                logging.info("The Sky Scanner is pointed at laser position of azi: %.2f and zeni %.2f" %(world_az, world_zeni))
                logging.info('Taking laser image')
                laser_image = imageTaker.take_laser_image(
                    config["laser_expose"], skyscanner, lasershutter, config["azi_laser"], config["zen_laser"], fw, filterwheel_config["laser_position"])
                config['laser_lasttime'] = datetime.now()

    skyscanner.go_home()
    fw.go(filterwheel_config['park_position'])

    logging.info('Warming up CCD')
    camera.turnOffCooler()
    while (camera.getTemperature() < -20):
        logging.info('CCD Temperature: ' + str(camera.getTemperature()))
        sleep(10)

    logging.info('Shutting down CCD')
    camera.shutDown()

    powerControl = PowerControl(config['powerSwitchAddress'], config['powerSwitchUser'], config['powerSwitchPassword'])
    powerControl.turnOff(config['AndorPowerPort'])
    powerControl.turnOff(config['LaserPowerPort'])

    logging.info('Executed flawlessly, exitting')

except Exception as e:
    logging.error(e)

    logging.error('Turning off components')
    powerControl = PowerControl(config['powerSwitchAddress'], config['powerSwitchUser'], config['powerSwitchPassword'])
    powerControl.turnOff(config['AndorPowerPort'])
    powerControl.turnOff(config['LaserPowerPort'])

    #sm = SendMail(config['email'], config['pickleCred'], config['gmailCred'], config['site'])
    
    #print("sending mail")
    #sm.send_error(config['receiverEmails'], e)

    
