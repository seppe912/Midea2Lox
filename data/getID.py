#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Update Midea status
#Start


# Update Midea status

from midea.client import client as midea_client
from midea.device import air_conditioning_device as ac

import sys
import requests
import configparser
import logging

# Miniserver Daten Laden
cfg = configparser.ConfigParser()
cfg.read('/opt/loxberry/config/plugins/Midea2Lox/midea2lox.cfg')
MideaUser = cfg.get('default','MideaUser')
MideaPassword = cfg.get('default','MideaPassword')

_LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, filename='/opt/loxberry/log/plugins/Midea2Lox/midea2lox.log', format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s', datefmt='%d.%m %H:%M')

#Start
_LOGGER.info("connecting to Midea Cloud") 
# The client takes an App_Key, an account email address and a password
client = midea_client('3742e9e5842d4ad59c2db887e12449f9', MideaUser, MideaPassword)

# Log in right now, to check credentials (this step is optional, and will be called when listing devices)
client.setup()

# List devices. These are complex state holding objects, no other trickery needed from here. 
devices = client.devices()
  
count = 0

for device in devices:

    count +=1
    # Refresh the object with the actual state by querying it
    device.refresh()    
    print("Appliance %s, Name: %s, ID: %s" % (count, device.name, device.id))
    _LOGGER.info("Appliance {}: Name: {}, ID: {}".format(count, device.name, device.id))
