#!/usr/bin/python3

import os
import sys
import serial
from time import sleep

arduino_port = '/dev/ttyACM0'
baud = 9600
arduino = serial.Serial(arduino_port, baud)

sledPositionCalibrate = b"retract\n"
sledPositionSky = b"extend\n"

t = arduino.read()
print(t)

print('Moving sled to Calibration')
print('  --> It takes about 10 seconds')
arduino.write(sledPositionCalibrate)
sleep(10)

exit()

