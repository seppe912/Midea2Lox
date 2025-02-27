#!REPLACELBPBINDIR/venv/bin/python3
# -*- coding: utf-8 -*-
import logging
import sys
import configparser
import asyncio
from msmart.discover import Discover

###WORKAROUND OF CLOUD REGION BLOCK FOR EU
Discover._account = "midea_eu@mailinator.com"
Discover._password = "das_ist_passwort1"
###WORKAROUND OF CLOUD REGION BLOCK FOR EU

#set path
cfg_path = 'REPLACELBPCONFIGDIR' #### REPLACE LBPCONFIGDIR ####
log_path = 'REPLACELBPLOGDIR' #### REPLACE LBPLOGDIR ####
home_path = 'REPLACELBHOMEDIR' #### REPLACE LBHOMEDIR ####

cfg = configparser.RawConfigParser()
cfg.read(cfg_path + '/midea2lox.cfg')
DEBUG = cfg.get('default','DEBUG')
region = cfg.get('default','region')

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

if sys.version_info <= (3, 8):
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
        print(region)
        _LOGGER.info(f"Cloudregion = {region}")
        discovered_devices = await Discover.discover(region=region)
        for device in discovered_devices:
            _LOGGER.info("*** Found a device: \033[94m\033[1m{} \033[0m".format(device))
            print("*** Found a device: {} ".format(device))
            cfg_devices = configparser.RawConfigParser()
            cfg_devices.read(cfg_path + '/devices.cfg')
            if cfg_devices.has_section('Midea_' + str(device.id)) == False:
                cfg_devices.add_section('Midea_' + str(device.id)) 
            cfg_devices.set('Midea_' + str(device.id),"type", device.type.name)
            #cfg_devices.set('Midea_' + device.id,"version", str(device['version']))
            cfg_devices.set('Midea_' + str(device.id),"supported", device.supported)
            cfg_devices.set('Midea_' + str(device.id),"id", device.id)
            cfg_devices.set('Midea_' + str(device.id),"ip", device.ip)
            cfg_devices.set('Midea_' + str(device.id),"port", device.port)
            if device.supported:
                await device.get_capabilities()
                cfg_devices.set('Midea_' + str(device.id),"modes", [str(mode.name.lower()) for mode in device.supported_operation_modes])
                cfg_devices.set('Midea_' + str(device.id),"swingmodes", [str(swingmode.name.capitalize()) for swingmode in device.supported_swing_modes])
                cfg_devices.set('Midea_' + str(device.id),"fanspeeds", [str(fanspeed.name) for fanspeed in device.supported_fan_speeds])
                cfg_devices.set('Midea_' + str(device.id),"device min temperature", device.min_target_temperature)
                cfg_devices.set('Midea_' + str(device.id),"device max temperature", device.max_target_temperature)
                cfg_devices.set('Midea_' + str(device.id),"supports custom fanspeed", device.supports_custom_fan_speed)
                cfg_devices.set('Midea_' + str(device.id),"supports EcoMode", device.supports_eco)
                cfg_devices.set('Midea_' + str(device.id),"supports TurboMode", device.supports_turbo)
                cfg_devices.set('Midea_' + str(device.id),"supports Freeze Protection", device.supports_freeze_protection)
                cfg_devices.set('Midea_' + str(device.id),"supports Display control", device.supports_display_control)
                cfg_devices.set('Midea_' + str(device.id),"supports filter reminder", device.supports_filter_reminder)
                cfg_devices.set('Midea_' + str(device.id),"supports pruifier", device.supports_purifier)
                cfg_devices.set('Midea_' + str(device.id),"supports humidity", device._supports_humidity)
                cfg_devices.set('Midea_' + str(device.id),"supports horizontal swing angle", device.supports_horizontal_swing_angle)
                cfg_devices.set('Midea_' + str(device.id),"supports vertical swing angle", device.supports_vertical_swing_angle)
                cfg_devices.set('Midea_' + str(device.id),"supports Rate selects", [str(rate.name) for rate in device.supported_rate_selects])
                cfg_devices.set('Midea_' + str(device.id),"supports breeze_away", device.supports_breeze_away)
                cfg_devices.set('Midea_' + str(device.id),"supports breeze_mild", device.supports_breeze_mild)
                cfg_devices.set('Midea_' + str(device.id),"supports breezeless", device.supports_breezeless)
                cfg_devices.set('Midea_' + str(device.id),"supports ieco", device.supports_ieco)
            
            if device.token is None and cfg_devices.get('Midea_' + str(device.id),"token"): ### keep last known Key/Token pair if cloud connection gets an error.
                pass
            elif device.token and device.key:
                cfg_devices.set('Midea_' + str(device.id),"token", device.token)
                cfg_devices.set('Midea_' + str(device.id),"key", device.key)
            cfg_devices.write(open(log_path + '/devices.log','w'))
            cfg_devices.write(open(cfg_path + '/devices.cfg','w'))
    except:
        _LOGGER.error(str(sys.exc_info()))
        sys.exit()

######## get devices and save to devices.cfg
try:
    asyncio.run(discovery())
        
except:
    print('Error : ' + str(sys.exc_info()))
    _LOGGER.error(str(sys.exc_info()))
    sys.exit()
