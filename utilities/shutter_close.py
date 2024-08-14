#!/usr/bin/python3

import os
import sys
from time import sleep
from config import config
import serial

from components.shutterhid import HIDLaserShutter

lasershutter = HIDLaserShutter(config['vendorId'], \
                               config['productId'])

sleep(2)
print('Closing shutter ...')
lasershutter.close_shutter()

exit()

