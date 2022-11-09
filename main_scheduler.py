from time import sleep
import ephem
from datetime import datetime, timedelta, timezone, date
import utilities.time_helper
from config import config
from schedule import observations
import sys 
import os
from components.camera import getCamera
from components.lasershutter_i2c.shutter import LaserShutter
fromt components.sky_scanner import SkyScanner
from utilities.image_taker import take_initial_image, take_normal_image

import h5py
import logging


# logger file 

logging.basicConfig(filename='example.log',
                    encoding='utf-8', format='%(asctime)s %(message)s',  level=logging.DEBUG)
 

# from filterwheel import FilterWheel

data_file_name = date.today()
data_files = h5py.File(date_file_name + '.hdf5', 'w')

timeHelper = utilities.time_helper.TimeHelper()
sunrise = timeHelper.getSunrise()
sunset = timeHelper.getSunset()
logging.info('Got sunrise and sunset times')

# TODO: close laser_shutter

timeHelper.waitUntilHousekeeping()
logging.info('Housekeeping time start')

# housekeeping operations


# initialise skyscanned, camera, filterwheel


# Housekeeping
lasershutter = LaserShutter()
skyscanner = SkyScanner()
camera = getCamera("Andor")
skyscanner.go_home()
camera.setReadMode()



# TODO: filterwheel

# sets temperature
camera.setTemperature(temp_setpoint)
camera.turnOnCooler()
logging.info('Set camera temperature')


# Wait until sunset
timeHelper.waitUntilStartTime()
logging.info('Sunset time start')


# take dark, bias, laser image
bias_image = take_initial_image(camera, config[bias_expose]) 
dark_image = take_initial_image(camera, config[dark_expose])
laser_image = take_laser_image(camera, laser_expose, skyscanner, lasershutter, config[azi_laser] , config[zen_laser])
data_files.create_dataset("bias_image", data = bias_image)
data_files.create_dataset("dark_image", data = dark_image)
logging.info('dark, bias and laser image taken')



# Start main loop
image_count = 1
while (datetime.now() <= sunrise):
    # take images
    # TODO
    for observation in observations:
        # perform tasks as specified
        # TODO
        skyscanner.set_pos(observation["skyScannerLocation"][0], observation["skyScannerLocation"][1]
        new_image = take_normal_image(camera, observation["exposureTime"])
        data_files.create_dataset("image"+ str(image_count), data = new_image)
        image_count = image_count + 1
        logging.info('image' + str(image_count) + 'taken')
        pass

data_files.close()

# Prepare to sleep

