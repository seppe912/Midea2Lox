#!REPLACELBPBINDIR/venv/bin/python3
# -*- coding: utf-8 -*-
import logging
import sys
import configparser

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

if sys.version_info < (3, 5):
    print(
        "To use this script you need python 3.5 or newer, got %s" % (
            sys.version_info,)
    )
    _LOGGER.error(
        "To use this script you need python 3.5 or newer, got %s" % (
            sys.version_info,)
    )
    sys.exit(1)


def discover(amount: int, account:str, password:str):
    import asyncio
    from msmart.const import OPEN_MIDEA_APP_ACCOUNT, OPEN_MIDEA_APP_PASSWORD
    from msmart.scanner import MideaDiscovery
    from msmart import VERSION
    """Send Device Scan Broadcast"""

    if account == "":
        account = OPEN_MIDEA_APP_ACCOUNT
        password = OPEN_MIDEA_APP_PASSWORD

    _LOGGER.info(
        "Sending Device Scan Broadcast...")
    
    try:
        device_list =[]
        discovery = MideaDiscovery(account=account, password=password, amount=amount)
        loop = asyncio.new_event_loop()
        found_devices = loop.run_until_complete(discovery.get_all())
        loop.close()
        
        for device in found_devices:
            _LOGGER.info("*** Found a device: \033[94m\033[1m{} \033[0m".format(device))
            print("*** Found a device: {} ".format(device))
            device_list.append(str(device))
        return device_list
    except:
        _LOGGER.error(str(sys.exc_info()))
        sys.exit()

######## get devices and save to devices.cfg
try:
    device_list = discover(int(BroadcastPakets), MideaUser, MideaPW)
    for eachArg in device_list:
        device = eval(eachArg)
        cfg_devices = configparser.RawConfigParser()
        cfg_devices.read(cfg_path + '/devices.cfg')
        if cfg_devices.has_section('Midea_' + str(device['id'])) == False:
            cfg_devices.add_section('Midea_' + str(device['id']))            
        cfg_devices.set('Midea_' + str(device['id']),"type", str(device['type']))
        cfg_devices.set('Midea_' + str(device['id']),"version", str(device['version']))
        cfg_devices.set('Midea_' + str(device['id']),"support", str(device['support']))
        cfg_devices.set('Midea_' + str(device['id']),"id", str(device['id']))
        cfg_devices.set('Midea_' + str(device['id']),"ip", str(device['ip']))
        cfg_devices.set('Midea_' + str(device['id']),"port", str(device['port']))
        if device['token'] is not None:
            cfg_devices.set('Midea_' + str(device['id']),"token", str(device['token']))
            cfg_devices.set('Midea_' + str(device['id']),"key", str(device['key']))
            
        cfg_devices.write(open(log_path + '/devices.log','w'))
        cfg_devices.write(open(cfg_path + '/devices.cfg','w'))
        
except:
    print('Error : ' + str(sys.exc_info()))
    _LOGGER.error(str(sys.exc_info()))
    sys.exit()
