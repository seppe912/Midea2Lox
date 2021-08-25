#!/usr/bin/python3
# -*- coding: utf-8 -*-
import logging
import sys
import configparser

cfg = configparser.RawConfigParser()
cfg.read('REPLACELBPCONFIGDIR/midea2lox.cfg')
DEBUG = cfg.get('default','DEBUG')
MideaUser = cfg.get('default','MideaUser')
MideaPW = cfg.get('default','MideaPassword')
BroadcastPakets = cfg.get('default','BroadcastPakets')

cfg2 = configparser.RawConfigParser()
cfg2.read('REPLACELBPLOGDIR/devices.log')

try:
    from msmart.cli import discover

    if DEBUG == "1":
        _LOGGER = logging.getLogger("discover.py")
        logging.basicConfig(level=logging.DEBUG, filename='/opt/loxberry/log/plugins/Midea2Lox/midea2lox.log', format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s', datefmt='%d.%m %H:%M')
        device_list = discover(1,int(BroadcastPakets), MideaUser, MideaPW)
    else:
        _LOGGER = logging.getLogger("discover.py")
        logging.basicConfig(level=logging.INFO, filename='/opt/loxberry/log/plugins/Midea2Lox/midea2lox.log', format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s', datefmt='%d.%m %H:%M')    
        device_list = discover(0,int(BroadcastPakets), MideaUser, MideaPW)

    for eachArg in device_list:
        device = eval(eachArg)
        
        if cfg2.has_section('Midea_' + str(device['id'])) == False:
            _LOGGER.info(cfg2.has_section(str(device['id'])))
            cfg2.add_section('Midea_' + str(device['id']))
            
        cfg2.set('Midea_' + str(device['id']),"type", str(device['type']))
        cfg2.set('Midea_' + str(device['id']),"version", str(device['version']))
        cfg2.set('Midea_' + str(device['id']),"id", str(device['id']))
        cfg2.set('Midea_' + str(device['id']),"ip", str(device['ip']))
        cfg2.set('Midea_' + str(device['id']),"port", str(device['port']))
        if device['version'] == 3:
            cfg2.set('Midea_' + str(device['id']),"token", str(device['token']))
            cfg2.set('Midea_' + str(device['id']),"key", str(device['key']))
            
        cfg2.write(open("REPLACELBPLOGDIR/devices.log","w"))
        
except:
    _LOGGER = logging.getLogger("discover.py")
    logging.basicConfig(level=logging.INFO, filename='REPLACELBPLOGDIR/midea2lox.log', format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s', datefmt='%d.%m %H:%M')
    print('Error : ' + str(sys.exc_info()))
    _LOGGER.error(str(sys.exc_info()))
    sys.exit()
 
