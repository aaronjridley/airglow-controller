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

    if (args.port > 0):
        print('Working with port: ', args.port)
        if (args.off):
            print('  --> turning port off!')
            powerControl.turnOff(args.port)
        else:
            print('  --> turning port on!')
            powerControl.turnOn(args.port)
    else:
        print('Invalid port!')
        
    sleep(2)

    exit()
