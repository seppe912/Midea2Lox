#!REPLACELBPDATADIR/venv/bin/python3
# -*- coding: utf-8 -*-
import logging
import sys
import configparser

cfg = configparser.RawConfigParser()
cfg.read('REPLACELBPCONFIGDIR/midea2lox.cfg')
DEBUG = cfg.get('default','DEBUG')

try:
    from msmart.cli import discover

    if DEBUG == "1":
        _LOGGER = logging.getLogger("discover.py")
        logging.basicConfig(level=logging.DEBUG, filename='REPLACELBPLOGDIR/midea2lox.log', format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s', datefmt='%d.%m %H:%M')
        discover(1)
    else:
        _LOGGER = logging.getLogger("discover.py")
        logging.basicConfig(level=logging.INFO, filename='REPLACELBPLOGDIR/midea2lox.log', format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s', datefmt='%d.%m %H:%M')    
        discover(0)
except:
    _LOGGER = logging.getLogger("discover.py")
    logging.basicConfig(level=logging.INFO, filename='REPLACELBPLOGDIR/midea2lox.log', format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s', datefmt='%d.%m %H:%M')
    print('Error : ' + str(sys.exc_info()))
    _LOGGER.error(str(sys.exc_info()))
    sys.exit()
 
