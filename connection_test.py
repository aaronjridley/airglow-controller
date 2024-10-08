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
from config import config, skyscan_config, filterwheel_config
from schedule import observations

import utilities.time_helper
from utilities.image_taker import Image_Helper
#from utilities.send_mail import SendMail

from components.camera import getCamera
from components.shutterhid import HIDLaserShutter
#from components.sky_scanner import SkyScanner
#from components.skyalert import SkyAlert
from components.powercontrol import PowerControl
#from components.filterwheel import FilterWheel

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

# powerControl = PowerControl(config['powerSwitchAddress'], config['powerSwitchUser'], config['powerSwitchPassword'])
# powerControl.turnOn(config['AndorPowerPort'])
# powerControl.turnOn(config['SkyScannerPowerPort'])
# powerControl.turnOn(config['LaserPowerPort'])

#logging.info('Initializing LaserShutter')
#lasershutter = HIDLaserShutter(config['vendorId'], config['productId'])
#
#lasershutter.close_shutter()
#lasershutter.open_shutter()
#sleep(5)
#lasershutter.close_shutter()
#sleep(5)

fw = FilterWheel(ip_address='http://192.168.1.143:8080/')
fw.home()
fw.go(1)

#logging.info('Initializing SkyScanner')
#skyscanner = SkyScanner(skyscan_config['max_steps'], skyscan_config['azi_offset'], skyscan_config['zeni_offset'], skyscan_config['azi_world'], skyscan_config['zeni_world'], skyscan_config['number_of_steps'], skyscan_config['port_location'])
#logging.info('Sending SkyScanner home')
#skyscanner.go_home()
#skyscanner.set_pos_real(45,45)

#logging.info('Initializing CCD')
#camera = getCamera("Andor")
#camera.setTemperature(-40)
#camera.turnOnCooler()
#print(camera.getTemperature())
#sleep(10)
#print(camera.getTemperature())
#sleep(10)
#print(camera.getTemperature())
#camera.shutDown()

# sa = SkyAlert(config['skyAlertAddress'])
# logging.info(sa.getList())

# powerControl.turnOff(config['AndorPowerPort'])
# powerControl.turnOff(config['SkyScannerPowerPort'])
# powerControl.turnOff(config['LaserPowerPort'])

# sm = SendMail(config['email'], config['pickleCred'], config['gmailCred'], config['site'])

# print("sending mail")
# sm.send_error(["khanhn2@illinois.edu"], "Test connection")
