import os
import sys
import logging
import signal
import scipy
import numpy
from time import sleep
from datetime import datetime, timedelta


from config import config, skyscan_config
from schedule import observations

import utilities.time_helper
from utilities.image_taker import Image_Helper

from components.camera import getCamera
from components.lasershutter.shutter import LaserShutter
from components.sky_scanner import SkyScanner
from components.skyalert import SkyAlert
from components.powercontrol import PowerControl


logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

powerControl = PowerControl(config['powerSwitchAddress'], config['powerSwitchUser'], config['powerSwitchPassword'])
powerControl.turnOn(config['AndorPowerPort'])
powerControl.turnOn(config['SkyScannerPowerPort'])
powerControl.turnOn(config['LaserPowerPort'])

logging.info('Initializing LaserShutter')
lasershutter = LaserShutter()

lasershutter.close_shutter()
lasershutter.open_shutter()
sleep(5)
lasershutter.close_shutter()
sleep(5)


logging.info('Initializing SkyScanner')
skyscanner = SkyScanner(skyscan_config['max_steps'], skyscan_config['azi_offset'], skyscan_config['zeni_offset'], skyscan_config['azi_world'], skyscan_config['zeni_world'], skyscan_config['number_of_steps'], skyscan_config['port_location'])
logging.info('Sending SkyScanner home')
skyscanner.go_home()

logging.info('Initializing CCD')
camera = getCamera("Andor")
camera.shutDown()

sa = SkyAlert(config['skyAlertAddress'])
logging.info(sa.getList())

powerControl.turnOff(config['AndorPowerPort'])
powerControl.turnOff(config['SkyScannerPowerPort'])
powerControl.turnOff(config['LaserPowerPort'])