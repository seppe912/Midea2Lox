#!REPLACELBPDATADIR/venv/bin/python3
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

try:
    from msmart.cli import discover

    if DEBUG == "1":
        _LOGGER = logging.getLogger("discover.py")
        logging.basicConfig(level=logging.DEBUG, filename='REPLACELBPLOGDIR/midea2lox.log', format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s', datefmt='%d.%m %H:%M')
        discover(1,int(BroadcastPakets), MideaUser, MideaPW)
    else:
        _LOGGER = logging.getLogger("discover.py")
        logging.basicConfig(level=logging.INFO, filename='REPLACELBPLOGDIR/midea2lox.log', format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s', datefmt='%d.%m %H:%M')    
        discover(0,int(BroadcastPakets), MideaUser, MideaPW)
except:
    _LOGGER = logging.getLogger("discover.py")
    logging.basicConfig(level=logging.INFO, filename='REPLACELBPLOGDIR/midea2lox.log', format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s', datefmt='%d.%m %H:%M')
    print('Error : ' + str(sys.exc_info()))
    _LOGGER.error(str(sys.exc_info()))
    sys.exit()
 
