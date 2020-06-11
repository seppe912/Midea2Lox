#!/usr/bin/python3
# -*- coding: utf-8 -*-
import logging
import sys

import configparser

cfg = configparser.RawConfigParser()
cfg.read('REPLACELBPCONFIGDIR/midea2lox.cfg')
DEBUG = cfg.get('default','DEBUG')

try:
    from msmart.cli import discover

    # logging
    _LOGGER = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO, filename='REPLACELBPLOGDIR/midea2lox.log', format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s', datefmt='%d.%m %H:%M')

except:
    _LOGGER = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO, filename='REPLACELBPLOGDIR/midea2lox.log', format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s', datefmt='%d.%m %H:%M')
    print('Error : ' + str(sys.exc_info()))
    _LOGGER.error(str(sys.exc_info()))
    sys.exit()

if DEBUG == 1:
    discover(1)
else:
    discover(0)
