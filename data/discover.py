#!REPLACELBPBINDIR/venv/bin/python3
# -*- coding: utf-8 -*-
import logging
import sys
import configparser
import asyncio
from msmart.discover import Discover

#set path
cfg_path = 'REPLACELBPCONFIGDIR' #### REPLACE LBPCONFIGDIR ####
log_path = 'REPLACELBPLOGDIR' #### REPLACE LBPLOGDIR ####
home_path = 'REPLACELBHOMEDIR' #### REPLACE LBHOMEDIR ####

cfg = configparser.RawConfigParser()
cfg.read(cfg_path + '/midea2lox.cfg')
DEBUG = cfg.get('default','DEBUG')
MideaUser = cfg.get('default','MideaUser')
MideaPW = cfg.get('default','MideaPassword')
BroadcastPakets = cfg.get('default','BroadcastPakets')

## Logging
_LOGGER = logging.getLogger("discover.py")
try:
    if DEBUG == "1":
        logging.basicConfig(level=logging.DEBUG, filename= log_path + '/midea2lox.log', format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s', datefmt='%d.%m %H:%M')
    else:
        logging.basicConfig(level=logging.INFO, filename= log_path + '/midea2lox.log', format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s', datefmt='%d.%m %H:%M')    
except:
    logging.basicConfig(level=logging.INFO, filename= log_path + '/midea2lox.log', format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s', datefmt='%d.%m %H:%M')
    print('Error : ' + str(sys.exc_info()))
    _LOGGER.error(str(sys.exc_info()))
    sys.exit()

if sys.version_info < (3, 8):
    print(
        "To use this script you need python 3.8 or newer, got %s" % (
            sys.version_info,)
    )
    _LOGGER.error(
        "To use this script you need python 3.8 or newer, got %s" % (
            sys.version_info,)
    )
    sys.exit(1)


async def discovery():
    
    _LOGGER.info(
        "Sending Device Scan Broadcast...")
    
    try:
        device_list =[]
        discovered_devices = await Discover.discover()
        for device in discovered_devices:
            _LOGGER.info("*** Found a device: \033[94m\033[1m{} \033[0m".format(device))
            print("*** Found a device: {} ".format(device))
            cfg_devices = configparser.RawConfigParser()
            cfg_devices.read(cfg_path + '/devices.cfg')
            if cfg_devices.has_section('Midea_' + str(device.id)) == False:
                cfg_devices.add_section('Midea_' + str(device.id)) 
            cfg_devices.set('Midea_' + str(device.id),"type", device.type)
            #cfg_devices.set('Midea_' + device.id,"version", str(device['version']))
            cfg_devices.set('Midea_' + str(device.id),"supported", device.supported)
            cfg_devices.set('Midea_' + str(device.id),"id", device.id)
            cfg_devices.set('Midea_' + str(device.id),"ip", device.ip)
            cfg_devices.set('Midea_' + str(device.id),"port", device.port)
            if device.token is None and cfg_devices.get('Midea_' + str(device.id),"token"): ###keep last known Key/Token pair if cloud connection gets an error and sends None.
                pass
            else:
                cfg_devices.set('Midea_' + str(device.id),"token", device.token)
                cfg_devices.set('Midea_' + str(device.id),"key", device.key)
            cfg_devices.write(open(log_path + '/devices.log','w'))
            cfg_devices.write(open(cfg_path + '/devices.cfg','w'))
    except:
        _LOGGER.error(str(sys.exc_info()))
        sys.exit()

######## get devices and save to devices.cfg
try:
    device_list = asyncio.run(discovery())
        
except:
    print('Error : ' + str(sys.exc_info()))
    _LOGGER.error(str(sys.exc_info()))
    sys.exit()
