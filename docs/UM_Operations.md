
Turn on and off components using, for example:

./port_power.py -usb -on

usage: port_power.py [-h] [-port PORT] [-off] [-on] [-usb] [-camera] [-laser]
                     [-sled] [-allcomps]

Turn power port on/off

optional arguments:
  -h, --help  show this help message and exit
  -port PORT  port to turn on (-1 for no port!)
  -off        turns off port
  -on         turns on port
  -usb        turns on/off USB ports
  -camera     turns on/off CAMERA ports
  -laser      turns on/off LASER ports
  -sled       turns on/off SLED ports
  -allcomps   turns on/off ALL ports

