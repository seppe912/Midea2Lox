#!REPLACELBPBINDIR/venv/bin/python3
# -*- coding: utf-8 -*-
import logging
import sys

Midea2Lox_Version = '3.1.4'

#set path
cfg_path = 'REPLACELBPCONFIGDIR' #### REPLACE LBPCONFIGDIR ####
log_path = 'REPLACELBPLOGDIR' #### REPLACE LBPLOGDIR ####
home_path = 'REPLACELBHOMEDIR' #### REPLACE LBHOMEDIR ####


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
        oldLox = 0
        protocol = 2
        device_port = 6444
        retries = 0
        statusupdate = 0
        support_mode = 0
        device_id = None
        device_ip = None
        device_key = None
        device_token = None

        for eachArg in data: # get device_id
            if len(eachArg) == 14 and eachArg.isdigit():
                device_id = eachArg
                _LOGGER.debug("Device ID: '{}'".format(device_id))
            elif len(eachArg) == 64:
                device_key = eachArg
                _LOGGER.debug("Device Key: '{}'".format(device_key))
                protocol = 3
                oldLox = 1
            elif len(eachArg) == 128:
                device_token = eachArg
                _LOGGER.debug("Device Token: '{}'".format(device_token))
                protocol = 3
                oldLox = 1
            elif eachArg == "status":
                statusupdate = 1
                _LOGGER.debug("statusupdate =: {}".format(statusupdate))
            try:
                if type(ip_address(eachArg)) is IPv4Address and not eachArg.isdigit():
                    device_ip = eachArg
                    _LOGGER.debug("Device ip: {}".format(device_ip))
                    oldLox = 1
            except:
                pass
                
        if len(data) == 10 and data[0] == 'True' or len(data) == 10 and data[0] == 'False': #support older Midea2Lox Versions <3.x
            support_mode = 1
            _LOGGER.debug("support Mode enabled")

        else:
            if device_id == None:                
                sys.exit("missing device_id, please check your Loxone config")
            try:
                _LOGGER.debug('get device informations')
                cfg_devices = configparser.RawConfigParser()
                cfg_devices.read(cfg_path + '/devices.cfg')   
                if device_ip == None:
                    device_ip = cfg_devices.get('Midea_' + device_id,'ip')
                    device_port = int(cfg_devices.get('Midea_' + device_id,'port'))
                protocol = int(cfg_devices.get('Midea_' + device_id,'version'))
                if protocol == 3:
                    if device_key == None or device_token == None:
                        device_key = cfg_devices.get('Midea_' + device_id,'key')
                        device_token = cfg_devices.get('Midea_' + device_id,'token')
            except:
                _LOGGER.warning('couldn´t find Device ID "%s", please do Discover or Check your Loxone config to send the right ID' % (device_id))
                
        if device_id == None:
            sys.exit('device ID unknown')
        elif device_ip == None:
            sys.exit('device IP unknown')
            
        if protocol == 3:
            if device_key == None:
                sys.exit('device Key unknown')
            elif device_token == None:
                sys.exit('device Token unknown')
            
            
        device = ac(device_ip, int(device_id), device_port)
        
        if protocol == 3: # support midea V3
            # If the device is using protocol 3 (aka 8370)
            # you must authenticate with device's Key and token.
            
            a = device.authenticate(device_key, device_token)
            if a == False:
                device._active = False
                send_to_loxone(device, support_mode)
                sys.exit(0)
        else:
            _LOGGER.info("use Midea V2")
            
        if statusupdate == 1: # refresh() AC State
            try:
                device.refresh()
                while device.active == False and retries < 2: # retry 2 times on connection error
                    retries += 1
                    _LOGGER.warning("retry refresh %s/2" %(retries))
                    time.sleep(5)
                    device.refresh()
            except Exception as error:
                device._active = False
                _LOGGER.error(error)

        else: # apply() AC changes
            if support_mode == 1:
                _LOGGER.info("apply() on support Mode for Loxone Configs createt with Midea2Lox V2.x --> MQTT disabled. If you want to use MQTT you need to update your Loxoneconfig")
                key = ["True", "False", "ac.operational_mode_enum.auto", "ac.operational_mode_enum.cool", "ac.operational_mode_enum.heat", "ac.operational_mode_enum.dry", "ac.operational_mode_enum.fan_only", "ac.fan_speed_enum.High", "ac.fan_speed_enum.Medium", "ac.fan_speed_enum.Low", "ac.fan_speed_enum.Auto", "ac.fan_speed_enum.Silent", "ac.swing_mode_enum.Off", "ac.swing_mode_enum.Vertical", "ac.swing_mode_enum.Horizontal", "ac.swing_mode_enum.Both"] 
                if data[0] in key and data[1] in key and data[3] in key and data[4] in key and data[5] in key and data[6] in key and data[7] in key:
                    device.power_state = eval(data[0])
                    device.prompt_tone = eval(data[1])
                    device.target_temperature = int(data[2])
                    device.operational_mode = eval(data[3])
                    device.fan_speed = eval(data[4])
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
                if oldLox == 1:
                    _LOGGER.warning("you dont need to send IP, Key and Token anymore, just do a discover and send your DeviceID")
                if protocol == 3 and len(data) != 12 or protocol == 2 and len(data) != 10: #if not all settings are sent from loxone, refresh() is neccessary.
                    try:
                        device.refresh()
                        while device.active == False and retries < 2: # retry 2 times on connection error
                            retries += 1
                            _LOGGER.warning("retry refresh %s/2" %(retries))
                            time.sleep(5)
                            device.refresh()
                    except Exception as error:
                        device._active = False
                        send_to_loxone(device, support_mode)
                        raise error
                    
                #set all allowed key´s for Loxone input
                power = ["power.True", "power.False"]
                tone = ["tone.True", "tone.False"]
                operation = ["ac.operational_mode_enum.auto", "ac.operational_mode_enum.cool", "ac.operational_mode_enum.heat", "ac.operational_mode_enum.dry", "ac.operational_mode_enum.fan_only"] 
                fan = ["ac.fan_speed_enum.High", "ac.fan_speed_enum.Medium", "ac.fan_speed_enum.Low", "ac.fan_speed_enum.Auto", "ac.fan_speed_enum.Silent"] 
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
                        if len(eachArg) != 64 and len(eachArg) != 128 and eachArg != device_id and eachArg != device_ip:
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
                while device.active == False and retries < 2: # retry 2 times on connection error
                    retries += 1
                    _LOGGER.warning("retry apply %s/2" %(retries))
                    time.sleep(5)
                    device.apply()
            except Exception as error:
                device._active = False
                _LOGGER.error(error)
                
        if device.active == True:
            if statusupdate == 1:
                _LOGGER.info("Statusupdate for Midea.{} @ {} successful".format(device.id, device.ip))
            else:
                _LOGGER.info("Set new state for Midea.{} @ {} successful".format(device.id, device.ip))
        else:
            _LOGGER.error("Device is offline")
            
        send_to_loxone(device, support_mode)
    
    finally:
        _LOGGER.debug("{}s".format(round(time.time()-runtime,2)))
        
        
def send_to_loxone(device, support_mode):
    r_error = 0
    
    address_loxone = ("http://%s:%s@%s:%s/dev/sps/io/" % (LoxUser, LoxPassword, LoxIP, LoxPort))    
    addresses = [
        ("Midea/%s/power_state,%s" % (device.id, int(device.power_state))),           #power_state
        ("Midea/%s/audible_feedback,%s" % (device.id, int(device.prompt_tone))),      #prompt_tone
        ("Midea/%s/target_temperature,%s" % (device.id, device.target_temperature)),  #target_temperature
        ("Midea/%s/operational_mode,%s" % (device.id, device.operational_mode)),      #operational_mode
        ("Midea/%s/fan_speed,%s" % (device.id, device.fan_speed)),                    #fan_speed
        ("Midea/%s/swing_mode,%s" % (device.id, device.swing_mode)),                  #swing_mode
        ("Midea/%s/eco_mode,%s" % (device.id, int(device.eco_mode))),                 #eco_mode
        ("Midea/%s/turbo_mode,%s" % (device.id, int(device.turbo_mode))),             #turbo_mode
        ("Midea/%s/indoor_temperature,%s" % (device.id, device.indoor_temperature)),  #indoor_temperature
        ("Midea/%s/outdoor_temperature,%s" % (device.id, device.outdoor_temperature)),#outdoor_temperature
        ("Midea/%s/online,%s" % (device.id, int(device.active)))                      #device.online --> device.active since msmart 0.1.32
        ]
    
    if MQTT == 1 and support_mode == 0 and mqtt_error == 0: # publish over MQTT
        if device.active == True:
            for eachArg in addresses:
                MQTTpublish = eachArg.split(',')
                publish = client.publish('Midea2Lox/' + MQTTpublish[0], MQTTpublish[1], qos=2, retain=True)#publish eachArg
                _LOGGER.debug("Publishing: MsgNum:%s: %s" % (publish[1], eachArg))
                publish.wait_for_publish()
        else: # Send Device Offline state to Loxone over MQTT
            MQTTpublish = addresses[10].split(',')
            publish = client.publish('Midea2Lox/' + MQTTpublish[0], MQTTpublish[1], qos=2, retain=True)#publish device offline
            _LOGGER.debug("Publishing: MsgNum:%s: %s" % (publish[1], addresses[10]))
            publish.wait_for_publish()
        _LOGGER.info("send status to MQTTGateway for Midea.{} @ {} succesful".format(device.id, device.ip))
            
    else: #Publish to Loxone Inputs over HTTP
        if device.active == True:
            for eachArg in addresses:
                if support_mode == 1: # support Loxoneconfigs created with Midea2Lox V2.x
                    HTTPrequest = eachArg.replace('/' , '.')
                else: 
                    HTTPrequest = 'Midea2Lox_' + eachArg.replace('/' , '_')
                HTTPrequest = address_loxone + HTTPrequest.replace(',' , '/')
                r = requests.get(HTTPrequest)                
                if r.status_code != 200:
                    r_error = 1
                    Loxinput = HTTPrequest.replace(address_loxone,'')
                    _LOGGER.error("Error {} on set Loxone Input '{}', please Check User PW and IP from Miniserver in Loxberry config and the Names of Loxone Inputs.".format(r.status_code, Loxinput.split("/")[0]))
        
        else: # Send Device Offline state to Loxone over HTTP
            if support_mode == 1: # support Loxoneconfigs created with Midea2Lox V2.x
                HTTPrequest = addresses[10].replace('/' , '.')
            else: 
                HTTPrequest = 'Midea2Lox_' + addresses[10].replace('/' , '_')
            HTTPrequest = address_loxone + HTTPrequest.replace(',' , '/')
            r = requests.get(HTTPrequest)
            if r.status_code != 200:
                r_error = 1
                _LOGGER.error("Error {} on set Loxone Input Midea_{}_online, please Check User PW and IP from Miniserver in Loxberry config and the Names of Loxone Inputs.".format(r.status_code, device.id))
        
        if r_error == 0:
            _LOGGER.info("Set Loxone Inputs over HTTP for Midea.{} @ {} successful".format(device.id, device.ip))


# Ist ein Callback, der ausgeführt wird, wenn sich mit dem Broker verbunden wird
def on_connect(client, userdata, flags, rc):
    global mqtt_error
    mqtt_error = 1
    if rc == 0:
        _LOGGER.info("MQTT: Verbindung akzeptiert")
        mqtt_error = 0
        publish = client.publish('Midea2Lox/connection/status','connected',qos=2, retain=True)
        _LOGGER.debug("Publishing: MsgNum:%s: 'Midea2Lox/connection/status','connected'" % (publish[1]))
    elif rc == 1:
        _LOGGER.error("MQTT: Falsche Protokollversion")
    elif rc == 2:
        _LOGGER.error("MQTT: Identifizierung fehlgeschlagen")
    elif rc == 3:
        _LOGGER.error("MQTT: Server nicht erreichbar")
    elif rc == 4:
        _LOGGER.error("MQTT: Falscher benutzername oder Passwort")
    elif rc == 5:
        _LOGGER.error("MQTT: Nicht autorisiert")
    else:
        _LOGGER.error("MQTT: Ungültiger Returncode")

def on_disconnect(client, userdata, flags, rc):
    publish = client.publish('Midea2Lox/connection/status','disconnected',qos=2, retain=True)
    _LOGGER.debug("Publishing: MsgNum:%s: 'Midea2Lox/connection/status','disconnected'" % (publish[1]))
    

##########

try:
    from msmart.device import air_conditioning_device as ac, VERSION
    import requests
    import configparser
    import time
    from ipaddress import ip_address, IPv4Address
    import paho.mqtt.client as mqtt
    import json


    # Miniserver Daten Laden
    cfg = configparser.RawConfigParser()
    cfg.read(cfg_path + '/midea2lox.cfg')
    try:
        UDP_Port = int(cfg.get('default','UDP_PORT'))
        LoxberryIP = cfg.get('default','LoxberryIP')
        DEBUG = cfg.get('default','DEBUG')
        Miniserver = cfg.get('default','MINISERVER')
    except:
        sys.exit('wrong configuration, please set Miniserver and UDP-Port on Midea2Lox Webpage and click "save and restart"')

    # Credentials to set Loxone Inputs over HTTP
    cfg.read(home_path + '/config/system/general.cfg')
    LoxIP = cfg.get(Miniserver,'IPADDRESS')
    LoxPort = cfg.get(Miniserver,'PORT')
    LoxPassword = cfg.get(Miniserver,'PASS')
    LoxUser = cfg.get(Miniserver,'ADMIN')

    _LOGGER = logging.getLogger("Midea2Lox.py")
    if DEBUG == "1":
       logging.basicConfig(level=logging.DEBUG, filename= log_path + '/midea2lox.log', format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s', datefmt='%d.%m %H:%M')
       print("Debug is True")
       _LOGGER.debug("Debug is True")
    else:
       logging.basicConfig(level=logging.INFO, filename= log_path + '/midea2lox.log', format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s', datefmt='%d.%m %H:%M')
    
    #MQTT
    try: # check if MQTTgateway is installed or not and set MQTT Client settings
        with open(home_path + '/config/system/general.json') as jsonFile:
            jsonObject = json.load(jsonFile)
            jsonFile.close()
        MQTTuser = jsonObject["Mqtt"]["Brokeruser"]
        MQTTpass = jsonObject["Mqtt"]["Brokerpass"]
        MQTTport = jsonObject["Mqtt"]["Brokerport"]
        MQTThost = jsonObject["Mqtt"]["Brokerhost"]
        MQTTpsk = jsonObject["Mqtt"]["Brokerpsk"]
        client = mqtt.Client(client_id='Midea2Lox')
        client.username_pw_set(MQTTuser, MQTTpass)
        client.on_connect = on_connect
        client.on_disconnect = on_disconnect
        client.will_set('Midea2Lox/connection/status','disconnected',qos=2, retain=True)
        _LOGGER.info('found MQTT Gateway Plugin - publish over MQTT except on support_mode')
        client.connect(MQTThost, int(MQTTport))
        client.loop_start()
        MQTT = 1
    except:
        _LOGGER.debug('cant find MQTT Gateway use HTTP requests to set Loxone inputs')
        MQTT = 0

except:
    _LOGGER = logging.getLogger("Midea2Lox.py")
    logging.basicConfig(level=logging.INFO, filename= log_path + '/midea2lox.log', format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s', datefmt='%d.%m %H:%M')
    print('Error : ' + str(sys.exc_info()))
    _LOGGER.error(str(sys.exc_info()))
    sys.exit()

# Start script
start_server()
