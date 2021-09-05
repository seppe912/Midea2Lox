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

cfg_devices = configparser.RawConfigParser()
cfg_devices.read(cfg_path + '/devices.cfg')

try:
    from msmart.cli import discover

    if DEBUG == "1":
        _LOGGER = logging.getLogger("discover.py")
        logging.basicConfig(level=logging.DEBUG, filename= log_path + '/midea2lox.log', format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s', datefmt='%d.%m %H:%M')
        device_list = discover(1,int(BroadcastPakets), MideaUser, MideaPW)
    else:
        _LOGGER = logging.getLogger("discover.py")
        logging.basicConfig(level=logging.INFO, filename= log_path + '/midea2lox.log', format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s', datefmt='%d.%m %H:%M')    
        device_list = discover(0,int(BroadcastPakets), MideaUser, MideaPW)

    for eachArg in device_list:
        device = eval(eachArg)        
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
    _LOGGER = logging.getLogger("discover.py")
    logging.basicConfig(level=logging.INFO, filename= log_path + '/midea2lox.log', format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s', datefmt='%d.%m %H:%M')
    print('Error : ' + str(sys.exc_info()))
    _LOGGER.error(str(sys.exc_info()))
    sys.exit()
