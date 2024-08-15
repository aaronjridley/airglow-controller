#!/usr/bin/python3

from config import config
from components.powercontrol import PowerControl
from time import sleep
import argparse

# ----------------------------------------------------------------------        
# Function to parse input arguments                                             
# ----------------------------------------------------------------------        

def parse_args():

    parser = argparse.ArgumentParser(description = 'Turn power port on/off')
    parser.add_argument('-port', default = -1, type = int, \
			help='port to turn on (-1 for no port!)')
    parser.add_argument('-off', \
                        help='turns off port', \
                        action="store_true")
    parser.add_argument('-on', \
                        help='turns on port', \
                        action="store_true")
    parser.add_argument('-usb', \
                        help='turns on/off USB ports', \
                        action="store_true")
    parser.add_argument('-camera', \
                        help='turns on/off CAMERA ports', \
                        action="store_true")
    parser.add_argument('-laser', \
                        help='turns on/off LASER ports', \
                        action="store_true")
    parser.add_argument('-sled', \
                        help='turns on/off SLED ports', \
                        action="store_true")
    parser.add_argument('-allcomps', \
                        help='turns on/off ALL ports', \
                        action="store_true")
    args = parser.parse_args()

    return args


#----------------------------------------------------------------------------   
# main code                                                                     
#----------------------------------------------------------------------------   

if __name__ == '__main__':  # main code block                                   

    args = parse_args()

    powerControl = PowerControl(config['powerSwitchAddress'],
                                config['powerSwitchUser'],
                                config['powerSwitchPassword'])

    ports = []
    if (args.port > 0):
        ports = [args.port]
    if (args.usb):
        ports.append(config['UsbPowerPort'])
    if (args.camera):
        ports.append(config['AndorPowerPort'])
    if (args.laser):
        ports.append(config['LaserPowerPort'])
        ports.append(config['LaserShutterPowerPort'])
    if (args.sled):
        ports.append(config['SledPowerPort'])
    if (args.allcomps):
        ports.append(config['UsbPowerPort'])
        ports.append(config['AndorPowerPort'])
        ports.append(config['LaserPowerPort'])
        ports.append(config['LaserShutterPowerPort'])
        ports.append(config['SledPowerPort'])
    if (len(ports) > 0):
        for port in ports:
            print('Working with port: ', port)
            if (args.off):
                print('  --> turning port %i off!' % port)
                powerControl.turnOff(port)
            else:
                print('  --> turning port %i on!' % port)
                powerControl.turnOn(port)
    else:
        print('Invalid port - need to specify some port!')
        
    sleep(2)

    exit()
