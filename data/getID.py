#!/usr/bin/python3
# -*- coding: utf-8 -*-

try:
    from midea.client import client as midea_client

    import configparser
    import logging
except:
    _LOGGER = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO, filename='REPLACELBPLOGDIR/midea2lox.log', format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s', datefmt='%d.%m %H:%M')
    print('Error : ' + str(sys.exc_info()))
    _LOGGER.error(str(sys.exc_info()))
    sys.exit()

# Midea Cloud Zugangsdaten laden
cfg = configparser.ConfigParser()
cfg.read('REPLACELBPCONFIGDIR/midea2lox.cfg')
MideaUser = cfg.get('default','MideaUser')
MideaPassword = cfg.get('default','MideaPassword')

# logging
_LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, filename='REPLACELBPLOGDIR/midea2lox.log', format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s', datefmt='%d.%m %H:%M')

# Start getID
_LOGGER.info("connecting to Midea Cloud") 
# The client takes an App_Key, an account email address and a password
client = midea_client('3742e9e5842d4ad59c2db887e12449f9', MideaUser, MideaPassword)

# Log in right now, to check credentials (this step is optional, and will be called when listing devices)
try: 
    client.setup()
except:
    import sys
    print('Error : ' + str(sys.exc_info()))
    _LOGGER.error(str(sys.exc_info()))

# List devices. These are complex state holding objects, no other trickery needed from here. 
devices = client.devices()
count = 0

for device in devices:

    count +=1
    print("Appliance %s, Name: %s, ID: %s" % (count, device.name, device.id))
    _LOGGER.info("Appliance {}: Name: {}, ID: {}".format(count, device.name, device.id))
