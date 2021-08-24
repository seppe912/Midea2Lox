#!/usr/bin/python3
# -*- coding: utf-8 -*-
import logging
import sys

Midea2Lox_Version = '3.0.1'
  

# Mainprogramm
def start_server():
    _LOGGER.info("Midea2Lox Version: {} msmart Version: {}".format(Midea2Lox_Version, VERSION))
    import socket
    soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        soc.bind((LoxberryIP, UDP_Port))
        print('Socket bind complete, listen at' , LoxberryIP, ":", UDP_Port)
        _LOGGER.info("Socket bind complete, listen at {}:{}".format(LoxberryIP, UDP_Port))

    except socket.error as msg:
        print('Bind failed. Error : ' + str(sys.exc_info()))
        _LOGGER.error('Bind failed. Error : ' + str(sys.exc_info()))
        sys.exit()
    
    while True:
        data, addr = soc.recvfrom(1024)
        data = data.decode('utf-8')
        data = data.split(' ')
        if data[0] != '0' and data[0] != '':
            print("Incomming Message from Loxone: ", data)
            _LOGGER.info("Incomming Message from Loxone: {}".format(data))
            try:
                print("send Message to Midea Appliance")
                _LOGGER.info("send Message to Midea Appliance")
                send_to_midea(data)
            except:
                print('Error : ' + str(sys.exc_info()))
                _LOGGER.error(str(sys.exc_info()))
    soc.close()

# send to Midea Appliance over LAN/WLAN
def send_to_midea(data):
    try: 
        #Start, set Loxone Script to active
        runtime = time.time()

        retries = 0
        protocol = 2
        statusupdate = 0
        support_mode = 0
        
        device_id = None
        device_ip = None
        device_k1 = None
        device_token = None

        for eachArg in data: # get device_id, device_ip and for V3 K1 and Token.
            if len(eachArg) == 64:
                device_k1 = eachArg
                _LOGGER.debug("Device K1: '{}'".format(device_k1))
                protocol = 3
            elif len(eachArg) == 128:
                device_token = eachArg
                _LOGGER.debug("Device Token: '{}'".format(device_token))
                protocol = 3
            elif len(eachArg) == 14 and eachArg.isdigit():
                device_id = eachArg
                _LOGGER.debug("Device ID: '{}'".format(device_id))
            elif eachArg == "status":
                statusupdate = 1
                _LOGGER.debug("statusupdate =: {}".format(statusupdate))
            try:
                if eachArg in IPNetwork('0/0') and not eachArg.isdigit():
                    device_ip = eachArg
                    _LOGGER.debug("Device ip: {}".format(device_ip))
            except:
                pass
                
        if device_id == None:                
            sys.exit("missing device_id")
        elif device_ip == None:
            sys.exit("missing device_ip")
        elif protocol == 3 and device_k1 == None:
            sys.exit("missing device_k1 only token is given")
        elif protocol == 3 and device_token == None:
            sys.exit("missing device_token only K1 is given")

        device = ac(device_ip, int(device_id), 6444)
        
        if protocol == 3: # support midea V3
            # If the device is using protocol 3 (aka 8370)
            # you must authenticate with device's k1 and token.
            # adb logcat | grep doKeyAgree
            # device.authenticate('YOUR_AC_K1', 'YOUR_AC_TOKEN')
            _LOGGER.info("use Midea V3 8370")
            _LOGGER.debug("AC token:{}; AC K1:{}".format(device_token, device_k1))
            try:
                device.authenticate(device_k1, device_token)
            except Exception as error:
                device._online = False
                send_to_loxone(device, support_mode)
                raise error
                
        else:
            _LOGGER.info("use Midea V2")
        if statusupdate == 1: # refresh() AC State
            try:
                device.refresh()
                while device.online == False and retries < 2: # retry 2 times on connection error
                    retries += 1
                    _LOGGER.warning("retry refresh %s/2" %(retries))
                    time.sleep(5)
                    device.refresh()
            except Exception as error:
                device._online = False
                _LOGGER.error(error)

        else: # apply() AC changes
            if len(data) == 10 and data[0] == 'True' or len(data) == 10 and data[0] == 'False': #support older Midea2Lox Versions <3.x
                support_mode = 1
                _LOGGER.info("use support Mode for Loxone Configs createt with Midea2Lox V2.x --> MQTT disabled. If you want to use MQTT you need to update your Loxoneconfig")
                key = ["True", "False", "ac.operational_mode_enum.auto", "ac.operational_mode_enum.cool", "ac.operational_mode_enum.heat", "ac.operational_mode_enum.dry", "ac.operational_mode_enum.fan_only", "ac.fan_speed_enum.High", "ac.fan_speed_enum.Medium", "ac.fan_speed_enum.Low", "ac.fan_speed_enum.Auto", "ac.fan_speed_enum.Silent", "ac.swing_mode_enum.Off", "ac.swing_mode_enum.Vertical", "ac.swing_mode_enum.Horizontal", "ac.swing_mode_enum.Both"] 
                if data[0] in key and data[1] in key and data[3] in key and data[4] in key and data[5] in key and data[6] in key and data[7] in key:
                    device.power_state = eval(data[0])
                    device.prompt_tone = eval(data[1])
                    device.target_temperature = int(data[2])
                    device.operational_mode = eval(data[3])
                    device.fan_speed = eval(data[3])
                    device.swing_mode = eval(data[5])
                    device.eco_mode = eval(data[6])
                    device.turbo_mode = eval(data[7])
                else:
                    for eachArg in data:
                        if eachArg not in key and eachArg != data[2] and eachArg != data[8] and eachArg != data[9]:
                            print("getting wrong Argument: ", eachArg)
                            _LOGGER.error("getting wrong Argument: '{}'. Please check your Loxone config.".format(eachArg))                        
                    _LOGGER.info("allowed Arguments: {}".format(key))
                    sys.exit()


            else: # new find command logic. Need new Loxone config (power.True, tone.True, eco.True, turbo.True -- and False of each)
                if protocol == 3 and len(data) != 12 or protocol == 2 and len(data) != 10: #if not all settings are sent from loxone, refresh() is neccessary.
                    try:
                        device.refresh()
                        while device.online == False and retries < 2: # retry 2 times on connection error
                            retries += 1
                            _LOGGER.warning("retry refresh %s/2" %(retries))
                            time.sleep(5)
                            device.refresh()
                    except Exception as error:
                        device._online = False
                        send_to_loxone(device, support_mode)
                        raise error
                    
                #set all allowed key´s for Loxone input
                power = ["power.True", "power.False"]
                tone = ["tone.True", "tone.False"]
                operation = ["ac.operational_mode_enum.auto", "ac.operational_mode_enum.cool", "ac.operational_mode_enum.heat", "ac.operational_mode_enum.dry", "ac.operational_mode_enum.fan_only"] 
                fan = ["ac.operational_mode_enum.fan_only", "ac.fan_speed_enum.High", "ac.fan_speed_enum.Medium", "ac.fan_speed_enum.Low", "ac.fan_speed_enum.Auto", "ac.fan_speed_enum.Silent"] 
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
            try:
                device.apply()
                while device.online == False and retries < 2: # retry 2 times on connection error
                    retries += 1
                    _LOGGER.warning("retry apply %s/2" %(retries))
                    time.sleep(5)
                    device.apply()
            except Exception as error:
                device._online = False
                _LOGGER.error(error)
                
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
    
    if MQTT == 1 and support_mode == 0: # publish over MQTT
        if device.online == True:
            for eachArg in addresses:
                MQTTpublish = eachArg.replace(address_loxone,'Midea2Lox/')
                MQTTpublish = MQTTpublish.split(',')
                client.publish(MQTTpublish[0],MQTTpublish[1],qos=2, retain=True)#publish
        else: # Send Device Offline state to Loxone over MQTT
            MQTTpublish = addresses[10].replace(address_loxone,'Midea2Lox/')
            MQTTpublish = MQTTpublish.split(',')
            client.publish(MQTTpublish[0],MQTTpublish[1],qos=2, retain=True)#publish
        
        if mqtt_error == 0:
            _LOGGER.info("send status to MQTTGateway for Midea.{} @ {} succesful".format(device.id, device.ip))
            
    else: #Publish to Loxone Inputs over HTTP
        if device.online == True:
            for eachArg in addresses:
                HTTPrequest = eachArg.replace(',' , '/')
                if support_mode == 0: # support Loxoneconfigs created with Midea2Lox V2.x
                    HTTPrequest = HTTPrequest.replace('Midea',  'Midea2Lox_Midea')
                r = requests.get(HTTPrequest)                
                if r.status_code != 200:
                    r_error = 1
                    Loxinput = HTTPrequest.replace(address_loxone,'')
                    _LOGGER.error("Error {} on set Loxone Input '{}', please Check User PW and IP from Miniserver in Loxberry config and the Names of Loxone Inputs.".format(r.status_code, Loxinput.split("/")[0]))
        
        else: # Send Device Offline state to Loxone over HTTP
            HTTPrequest = addresses[10].replace(',' , '/')
            if support_mode == 0:
                HTTPrequest = HTTPrequest.replace('Midea',  'Midea2Lox_Midea')
            r = requests.get(HTTPrequest)
            if r.status_code != 200:
                r_error = 1
                _LOGGER.error("Error {} on set Loxone Input Midea.{}.online, please Check User PW and IP from Miniserver in Loxberry config and the Names of Loxone Inputs.".format(r.status_code, device.id))
        
        if r_error == 0:
            _LOGGER.info("Set Loxone Inputs over HTTP for Midea.{} @ {} successful".format(device.id, device.ip))



# Ist ein Callback, der ausgeführt wird, wenn sich mit dem Broker verbunden wird
def on_connect(client, userdata, flags, rc):
    global mqtt_error
    if rc == 0:
        _LOGGER.debug("MQTT: Verbindung akzeptiert")
        mqtt_error = 0
        client.publish('Midea2Lox/connection/status','connected',qos=2, retain=True)
    elif rc == 1:
        _LOGGER.error("MQTT: Falsche Protokollversion")
        mqtt_error = 1
    elif rc == 2:
        _LOGGER.error("MQTT: Identifizierung fehlgeschlagen")
        mqtt_error = 1
    elif rc == 3:
        _LOGGER.error("MQTT: Server nicht erreichbar")
        mqtt_error = 1
    elif rc == 4:
        _LOGGER.error("MQTT: Falscher benutzername oder Passwort")
        mqtt_error = 1
    elif rc == 5:
        _LOGGER.error("MQTT: Nicht autorisiert")
        mqtt_error = 1
    else:
        _LOGGER.error("MQTT: Ungültiger Returncode")
        mqtt_error = 1

def on_disconnect(client, userdata, flags, rc):
    client.publish('Midea2Lox/connection/status','disconnected',qos=2, retain=True)

# Ist ein Callback, der ausgeführt wird, wenn gesendet wird
def on_publish(client, userdata, mid):
    _LOGGER.debug("on_publish, mid {}".format(mid))


##########

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
    
    #MQTT
    with open('REPLACELBHOMEDIR/config/system/general.json') as jsonFile:
        jsonObject = json.load(jsonFile)
        jsonFile.close()
    try: # check if MQTTgateway is installed or not and set MQTT Client settings
        MQTTuser = jsonObject["Mqtt"]["Brokeruser"]
        MQTTpass = jsonObject["Mqtt"]["Brokerpass"]
        MQTTport = jsonObject["Mqtt"]["Brokerport"]
        MQTThost = jsonObject["Mqtt"]["Brokerhost"]
        client = mqtt.Client(client_id='Midea2Lox')
        client.username_pw_set(MQTTuser, MQTTpass)
        client.on_connect = on_connect
        client.on_disconnect = on_disconnect
        client.on_publish = on_publish
        client.will_set('Midea2Lox/connection/status','disconnected',qos=2, retain=True)
        _LOGGER.debug('found MQTT Gateway Plugin')
        client.connect(MQTThost, int(MQTTport))
        client.loop_start()
        MQTT = 1
    except:
        _LOGGER.debug('cant find MQTT Gateway use HTTP requests to set Loxone inputs')
        MQTT = 0

except:
    _LOGGER = logging.getLogger("Midea2Lox.py")
    logging.basicConfig(level=logging.INFO, filename='REPLACELBPLOGDIR/midea2lox.log', format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s', datefmt='%d.%m %H:%M')
    print('Error : ' + str(sys.exc_info()))
    _LOGGER.error(str(sys.exc_info()))
    sys.exit()

# Start script
start_server()
