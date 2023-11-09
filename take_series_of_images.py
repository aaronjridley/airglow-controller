#!/usr/bin/python3

from matplotlib import pyplot as plt
from time import sleep
from components.camera import getCamera
import logging
from datetime import datetime, timedelta
import h5py
from PIL import Image as im
import sys
from scipy import signal
import numpy as np

from config import config, skyscan_config
from components.shutterhid import HIDLaserShutter

def remove_hotspots(image):

    newImage = image

    std = np.std(newImage)
    med = np.median(newImage)
    accMax = med + 5.0 * std
    actMax = np.max(newImage)
    print('Acceptable max : ',accMax)
    print('Actual max     : ',np.max(newImage))

    if (accMax < actMax):
        print('Replacing hot spot pixels...')
        newImage[newImage > accMax] = med
    
    print(np.min(newImage), np.mean(newImage), np.median(newImage), np.max(newImage))
    
    return newImage
    
config['temp_setpoint'] = -80

#config = {
#    'log_dir': './',
#    'site': 'UM01',    
#    'hbin': 2,
#    'vbin': 2,
#    'temp_setpoint': 10,
#    'bias_expose': 0.1,
#    'dark_expose': 300,
#    'laser_expose': 30,
#    'i1': 150,
#    'j1': 150,
#    'i2': 200,
#    'j2': 200,
#    'N': 5}

# logging.info('Initializing LaserShutter')
#lasershutter = HIDLaserShutter(config['vendorId'], config['productId'])

#print("Closing Shutter...")
#lasershutter.close_shutter()


exposure = 2

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logging.info('Initializing Camera')


log_name = config['log_dir'] + config['site'] + datetime.now().strftime('_%Y%m%d_%H%M%S.log')
#logging.basicConfig(filename=log_name, encoding='utf-8',
#                   format='%(asctime)s %(message)s',
#                    level=logging.DEBUG)


camera = getCamera("Andor")

desired_temp = config["temp_setpoint"]
# Setup camera
camera.setReadMode()
camera.setImage(hbin=config['hbin'], vbin=config['vbin'])
camera.setShiftSpeed()
camera.setTemperature(config["temp_setpoint"])
camera.turnOnCooler()
print('Set camera temperature to %.2f C' % config["temp_setpoint"])
# Wait until temperature stablize and print the temperature

while (camera.getTemperature() > desired_temp+2):
    print('CCD Temperature: ' + str(camera.getTemperature()))
    sleep(5)

#print("Opening Laser Shutter...")
#lasershutter.open_shutter()

    
while (exposure > 0):

    sExposure = 'Enter exposure (%d, 0 to exit) : ' % exposure
    value = input(sExposure)
    if (len(value) > 0):
      exposure = int(value)
    else:
      exit()
      
    print("Setting read mode to 4 (image)")
    camera.setReadMode(4)

    print("setting shutter to fully auto mode")
    camera.setShutter(1)
    print("Setting acquision mode to 1")
    camera.setAcquisitionMode(1)
    print("Setting exposure time: ", exposure)
    camera.setExposureTime(exposure)

    startTime = str(datetime.now())
    print('Starting acquisition... ', startTime)
    camera.startAcquisition()
    sleep(exposure/2)
    print('Checking for acquiring signal... ')
    while (camera.getStatus() == "DRV_ACQUIRING"):
        print('  ... waiting ... ')
        sleep(2)
    print('Getting image...')
    nparr = camera.getImage()

    new_image_pre = np.array(nparr)

    print('Removing hot spots...')
    new_image = remove_hotspots(new_image_pre)
    
    image_sub = signal.convolve2d(
        new_image[config['i1']:config['i2'], config['j1']:config['j2']], np.ones((config['N'], config['N']))/config['N']**2, mode='valid')
    image_intensity = (np.percentile(image_sub, 75) - np.percentile(image_sub, 25))
    print('Image intensity : ', image_intensity)
    
    sTimeNow = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Set the figure size
    plt.rcParams["figure.figsize"] = [7.00, 7.00]
    plt.rcParams["figure.autolayout"] = True
    # Plot the data using imshow with gray colormap
    plt.imshow(new_image, cmap='plasma')

    plt.savefig('test_' + sTimeNow + '.png')

    data_files = h5py.File('test_' + sTimeNow + '.hdf5', 'w')
    f = data_files.create_dataset("image", data=nparr)
    f.attrs['ExposureTime'] = exposure
    f.attrs['LocalTime'] = startTime 
    f.attrs['CCDTemperature'] = camera.getTemperature()
    print('Camera temp set to :', camera.getTemperature())
    data_files.close()

print("Closing Laser Shutter...")
#lasershutter.close_shutter()      

# Warm the camera back up slowly so that the CCD is not damaged
camera.turnOffCooler()
while (camera.getTemperature() < 10):
    print('CCD Temperature: ' + str(camera.getTemperature()))
    sleep(5)
      
# Shutdown/disconnect camera afterward
camera.shutDown()


#logging.info('Set camera temperature to %.2f C' % config["temp_setpoint"])

#logging.info('Executed flawlessly, exitting')
