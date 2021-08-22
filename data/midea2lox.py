#!/usr/bin/python3
# -*- coding: utf-8 -*-
import logging
import sys

Midea2Lox_Version = '3.0.1'
    
try:
    from msmart.device import air_conditioning_device as ac
    from msmart.device import VERSION
    import requests
    import configparser
    import time
    from netaddr import IPNetwork
    import paho.mqtt.client as mqtt
    import json

    # Miniserver Daten Laden
    cfg = configparser.RawConfigParser()
    cfg.read('REPLACELBPCONFIGDIR/midea2lox.cfg')
    UDP_Port = int(cfg.get('default','UDP_PORT'))
    LoxberryIP = cfg.get('default','LoxberryIP')
    DEBUG = cfg.get('default','DEBUG')
    Miniserver = cfg.get('default','MINISERVER')
    
    #MQTT
    with open('REPLACELBHOMEDIR/config/system/general.json') as jsonFile:
        jsonObject = json.load(jsonFile)
        jsonFile.close()
    try: # check if MQTTgateway is installed or not
        MQTTuser = jsonObject["Mqtt"]["Brokeruser"]
        MQTTpass = jsonObject["Mqtt"]["Brokerpass"]
        MQTTport = jsonObject["Mqtt"]["Brokerport"]
        MQTThost = jsonObject["Mqtt"]["Brokerhost"]
        client =mqtt.Client(client_id='Midea2Lox')
        client.username_pw_set(MQTTuser, MQTTpass)
        MQTT = 1
    except:
        MQTT = 0
    
    # Credentials to set Loxone Inputs over HTTP
    cfg.read('/opt/loxberry/config/system/general.cfg')
    LoxIP = cfg.get(Miniserver,'IPADDRESS')
    LoxPort = cfg.get(Miniserver,'PORT')
    LoxPassword = cfg.get(Miniserver,'PASS')
    LoxUser = cfg.get(Miniserver,'ADMIN')
    
    _LOGGER = logging.getLogger("Midea2Lox.py")
    if DEBUG == "1":
       logging.basicConfig(level=logging.DEBUG, filename='REPLACELBPLOGDIR/midea2lox.log', format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s', datefmt='%d.%m %H:%M')
       print("Debug is True")
       _LOGGER.debug("Debug is True")
    else:
       logging.basicConfig(level=logging.INFO, filename='REPLACELBPLOGDIR/midea2lox.log', format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s', datefmt='%d.%m %H:%M')

except:
    _LOGGER = logging.getLogger("Midea2Lox.py")
    logging.basicConfig(level=logging.INFO, filename='REPLACELBPLOGDIR/midea2lox.log', format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s', datefmt='%d.%m %H:%M')
    print('Error : ' + str(sys.exc_info()))
    _LOGGER.error(str(sys.exc_info()))
    sys.exit()

                swing = ["ac.swing_mode_enum.Off", "ac.swing_mode_enum.Vertical", "ac.swing_mode_enum.Horizontal", "ac.swing_mode_enum.Both"]
                eco = ["eco.True", "eco.False"]
                turbo = ["turbo.True", "turbo.False"]
                
                for eachArg in data: #find keys from Loxone to msmart
                    if eachArg in power:
                        device.power_state = eval(eachArg.split(".")[1])
                        _LOGGER.debug("Device Power state '{}'".format(device.power_state))
                    elif eachArg in tone:
                        device.prompt_tone = eval(eachArg.split(".")[1])                
                        _LOGGER.debug("Device promt Tone '{}'".format(device.prompt_tone))
                    elif eachArg in eco:
                        device.eco_mode = eval(eachArg.split(".")[1])                
                        _LOGGER.debug("Device Eco Mode '{}'".format(device.eco_mode))
                    elif eachArg in turbo:
                        device.turbo_mode = eval(eachArg.split(".")[1])                
                        _LOGGER.debug("Device Turbo Mode '{}'".format(device.turbo_mode))
                    elif eachArg in operation:
                        device.operational_mode = eval(eachArg)
                        _LOGGER.debug(device.operational_mode)
                    elif eachArg in fan:
                        device.fan_speed = eval(eachArg)
                        _LOGGER.debug(device.fan_speed)
                    elif eachArg in swing:
                        device.swing_mode = eval(eachArg)
                        _LOGGER.debug(device.swing_mode)
                    elif len(eachArg) == 2 and eachArg.isdigit():
                        device.target_temperature = int(eachArg)
                        _LOGGER.debug(device.target_temperature)
                    else: #unknown key´s
                        if protocol == 3:
                            if eachArg != device_k1 and eachArg != device_token and eachArg != device_id and eachArg != device_ip:
                                _LOGGER.error("Given command '{}' is unknown".format(eachArg))
                        else:
                            if eachArg != device_id and eachArg != device_ip:
                                _LOGGER.error("Given command '{}' is unknown".format(eachArg))
                                
            # Errorhandling
            # Midea AC only supports auto Fanspeed in auto-Operationalmode.
            if device.operational_mode == ac.operational_mode_enum.auto:                    
                device.fan_speed = ac.fan_speed_enum.Auto
                _LOGGER.warning("set auto-Fanspeed because of Auto-Operational Mode")

            #Midea AC only supports Temperature from 17 to 30 °C
            if int(device.target_temperature) < 17:
                _LOGGER.warning("Get Temperature '{}'. Allowed Temperature: 17-30, set target Temperature to 17°C".format(device.target_temperature))
                device.target_temperature = 17
            elif int(device.target_temperature) > 30:
                _LOGGER.warning("Get Temperature '{}'. Allowed Temperature: 17-30, set target Temperature to 30°C".format(device.target_temperature))
                device.target_temperature = 30

            # commit the changes with apply()
            device.apply()
            while device.online == False and retries < 5: # retry 5 times on connection error
                retries += 1
                _LOGGER.warning("apply retry %s/5" %(retries))
                time.sleep(5)
                device.apply()

        if device.online == True:
            if statusupdate == 1:
                _LOGGER.info("Statusupdate for Midea.{} @ {} successful".format(device.id, device.ip))
            else:
                _LOGGER.info("Set new state for Midea.{} @ {} successful".format(device.id, device.ip))
        else:
            _LOGGER.error("Device is offline")
            
        send_to_loxone(device, support_mode)
    
    finally:
        _LOGGER.info(time.time()-runtime)


def send_to_loxone(device, support_mode):
    r_error = 0

    address_loxone = ("http://%s:%s@%s:%s/dev/sps/io/" % (LoxUser, LoxPassword, LoxIP, LoxPort))    
    addresses = [
        ("%sMidea.%s.power_state,%s" % (address_loxone, device.id, int(device.power_state))),                #power_state
        ("%sMidea.%s.audible_feedback,%s" % (address_loxone, device.id, int(device.prompt_tone))),           #prompt_tone
        ("%sMidea.%s.target_temperature,%s" % (address_loxone, device.id, device.target_temperature)),  #target_temperature
        ("%sMidea.%s.operational_mode,%s" % (address_loxone, device.id, device.operational_mode)),      #operational_mode
        ("%sMidea.%s.fan_speed,%s" % (address_loxone, device.id, device.fan_speed)),                    #fan_speed
        ("%sMidea.%s.swing_mode,%s" % (address_loxone, device.id, device.swing_mode)),                  #swing_mode
        ("%sMidea.%s.eco_mode,%s" % (address_loxone, device.id, int(device.eco_mode))),                      #eco_mode
        ("%sMidea.%s.turbo_mode,%s" % (address_loxone, device.id, int(device.turbo_mode))),                  #turbo_mode
        ("%sMidea.%s.indoor_temperature,%s" % (address_loxone, device.id, device.indoor_temperature)),  #indoor_temperature
        ("%sMidea.%s.outdoor_temperature,%s" % (address_loxone, device.id, device.outdoor_temperature)), #outdoor_temperature
        ("%sMidea.%s.online,%s" % (address_loxone, device.id, int(device.online)))                      #device.online
        ]
    
    if device.online == True: # send all states to Loxone / MQTT
        for eachArg in addresses:
            if MQTT == 1 and support_mode == 0: # Publish over MQTTGateway
                MQTTpublish = eachArg.replace(address_loxone,'Midea2Lox/')
                MQTTpublish = MQTTpublish.split(',')
                client.connect(host=MQTThost, port=int(MQTTport), keepalive=60)
                client.publish(MQTTpublish[0],MQTTpublish[1])#publish
            else: #Publish over HTTP Loxoneinputs
                HTTPrequest = eachArg.replace(',' , '/')
                if support_mode == 0: # support Loxoneconfigs created with Midea2Lox V2.x
                    HTTPrequest = HTTPrequest.replace('Midea',  'Midea2Lox_Midea')
                r = requests.get(HTTPrequest)                
                if r.status_code != 200:
                    r_error = 1
                    Loxinput = HTTPrequest.replace(address_loxone,'')
                    _LOGGER.error("Error {} on set Loxone Input '{}', please Check User PW and IP from Miniserver in Loxberry config and the Names of Loxone Inputs.".format(r.status_code, Loxinput.split("/")[0]))
    else: # Send Device Offline state to Loxone or MQTT
        if MQTT == 1 and support_mode == 0:
            MQTTpublish = addresses[10].replace(address_loxone,'Midea2Lox/')
            MQTTpublish = MQTTpublish.split(',')
            client.connect(host=MQTThost, port=int(MQTTport), keepalive=60)
            client.publish(MQTTpublish[0],MQTTpublish[1])#publish
        else:
            HTTPrequest = addresses[10].replace(',' , '/')
            if support_mode == 0:
                HTTPrequest = HTTPrequest.replace('Midea',  'Midea2Lox_Midea')
            r = requests.get(HTTPrequest)
            if r.status_code != 200:
                r_error = 1
                _LOGGER.error("Error {} on set Loxone Input Midea.{}.online, please Check User PW and IP from Miniserver in Loxberry config and the Names of Loxone Inputs.".format(r.status_code, device.id))

    if r_error == 0:
        if MQTT == 1 and support_mode == 0:
            _LOGGER.info("send status to MQTTGateway for Midea.{} @ {}".format(device.id, device.ip))
        else:
            _LOGGER.info("Set Loxone Inputs for Midea.{} @ {} successful".format(device.id, device.ip))


# Start script
start_server()  
