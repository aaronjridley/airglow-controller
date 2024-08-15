from datetime import timedelta

config = {
    'site': 'ANN',
    'latitude': '42.4038',
    'longitude': '-83.9244',
    'elevation': 300,
    'horizon': '-8.0',
    'instr_name': 'minime20',
    'startHousekeeping': 20,
    'sky_offset_el': 0,
    'sky_offset_az': 0,
    'auto_schedule': 1,
    'temp_setpoint': -70,
    'bias_expose': 0.1,
    'dark_expose': 300,
    'laser_expose': 60,
    'azi_laser': 90,
    'zen_laser': 180,
    'data_dir': '/home/ridley/Data/ann01/',
    'log_dir': '/home/ridley/Data/ann01/logfiles/',
    'laser_timedelta': timedelta(minutes=15),
    'laser_lasttime': None,
    'maxExposureTime': 600,
    'moonThresholdAngle': 37,

    # Camera setting
    'hbin': 2,
    'vbin': 2,

    'powerSwitchAddress': '10.0.0.99',
    'powerSwitchUser': 'admin',
    'powerSwitchPassword': 'NeutralW1nds',

    # scipy.signal.convolve2d
    'i1': 150,
    'j1': 150,
    'i2': 200,
    'j2': 200,
    'N': 5,


    # Power Ports
    'AndorPowerPort': 3,
    'SledPowerPort' : 6,
    'UsbPowerPort': 7,
    'LaserPowerPort': 4,
    'LaserShutterPowerPort': 8,

    # Arduino specifications for moving the sled:
    'arduino_port' : '/dev/ttyACM0',
    'arduino_baud' : 9600,

    # Laser shutter
    'vendorId': 0x0461,
    'productId': 0x0030

}


dummy = {
    'nothing': 0}

