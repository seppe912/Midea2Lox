#!/usr/bin/python3
# -*- coding: utf-8 -*-
import logging
import sys

Midea2Lox_Version = '3.0.0'
    
try:
    from msmart.device import air_conditioning_device as ac
    import requests
    import configparser


    # Miniserver Daten Laden
    cfg = configparser.RawConfigParser()
    cfg.read('REPLACELBPCONFIGDIR/midea2lox.cfg')
    UDP_Port = int(cfg.get('default','UDP_PORT'))
    LoxberryIP = cfg.get('default','LoxberryIP')
    DEBUG = cfg.get('default','DEBUG')
    Miniserver = cfg.get('default','MINISERVER')

    cfg.read('REPLACELBHOMEDIR/config/system/general.cfg')
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

# Mainprogramm
def start_server():
    _LOGGER.info("Midea2Lox Version: {}".format(Midea2Lox_Version))
    
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

    #Loxone Midea.AC_script reset to 0 on start from Midea2Lox
    requests.get("http://%s:%s@%s:%s/dev/sps/io/Midea.AC_script/0" % (LoxUser, LoxPassword, LoxIP, LoxPort))
    
    while True:
        global data
        data, addr = soc.recvfrom(1024)
        data = data.decode('utf-8')
        data = data.split(' ')
        if data[0] != '0':
            print("Incomming Message from Loxone: ", data)
            _LOGGER.info("Incomming Message from Loxone: {}".format(data))
            try:
                print("send Message to Midea Appliance")
                _LOGGER.info("send Message to Midea Appliance")
                send_to_midea()
            except:
                print('Error : ' + str(sys.exc_info()))
                _LOGGER.error(str(sys.exc_info()))
                requests.get("http://%s:%s@%s:%s/dev/sps/io/Midea.AC_script/0" % (LoxUser, LoxPassword, LoxIP, LoxPort))
    soc.close()


# send to Midea Appliance over LAN/WLAN
def send_to_midea():
    try: 
        #Start, set Loxone Script to active
        requests.get("http://%s:%s@%s:%s/dev/sps/io/Midea.AC_script/1" % (LoxUser, LoxPassword, LoxIP, LoxPort))
        retries = 0
        protocol = 2
        statusupdate = 0

        for eachArg in data:
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
            elif len(eachArg) == 14 and not eachArg.isdigit():
                device_ip = eachArg
                _LOGGER.debug("Device ip: {}".format(device_ip))
            elif eachArg == "status":
                statusupdate = 1
                _LOGGER.debug("statusupdate =: {}".format(statusupdate))
        
        try:
            device_id is not None
            device_ip is not None
        except:
            _LOGGER.error("On Midea2Lox V2.x and higher you need to send your Device ID and Device IP, please check your Loxone Config and see in Loxwiki: https://www.loxwiki.eu/display/LOXBERRY/Midea2Lox")
            exit()
        
        device = ac(device_ip, int(device_id), 6444)
        
        if protocol == 3: # support midea V3
            # If the device is using protocol 3 (aka 8370)
            # you must authenticate with device's k1 and token.
            # adb logcat | grep doKeyAgree
            # device.authenticate('YOUR_AC_K1', 'YOUR_AC_TOKEN')
            _LOGGER.info("use Midea V3 8370")
            _LOGGER.debug("AC token:{}; AC K1:{}".format(device_token, device_k1))
            device.authenticate(device_k1, device_token)
        else:
            _LOGGER.info("use Midea V2")

        if statusupdate == 1: # refresh() AC State
            device.refresh()

            while device.online == False and retries <= 10: # retry 10 times
                retries += 1
                _LOGGER.debug("retry %s" %(retries))
                time.sleep(5)
                device.refresh()

        else: # apply() AC changes
            if len(data) == 10: #support older Midea2Lox Versions <3.x
                key = ["True", "False", "ac.operational_mode_enum.auto", "ac.operational_mode_enum.cool", "ac.operational_mode_enum.heat", "ac.operational_mode_enum.dry", "ac.operational_mode_enum.fan_only", "ac.fan_speed_enum.High", "ac.fan_speed_enum.Medium", "ac.fan_speed_enum.Low", "ac.fan_speed_enum.Auto", "ac.fan_speed_enum.Silent", "ac.swing_mode_enum.Off", "ac.swing_mode_enum.Vertical", "ac.swing_mode_enum.Horizontal", "ac.swing_mode_enum.Both"] 
                if data[0] in key and data[1] in key and data[3] in key and data[4] in key and data[5] in key and data[6] in key and data[7] in key:
                    device_ip = str(data[9])
                    device_id = int(data[8])
                    device = ac(device_ip, int(device_id), 6444)

                    # Set the state of the device and
                    device.power_state = eval(data[0])
                    device.prompt_tone = eval(data[1])
                    
                    #device.target_temperature = int(data[2])
                    #Midea AC only supports Temperature from 17 to 30 °C

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


            else: # new find command logic. Need new Loxone config (power.True, tone.True, eco.True, turbo.True -- and False of each)
                device.refresh() # get actual state of the Device
                
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
                        if eachArg == "power.True":
                            device.power_state = True                
                        elif eachArg == "power.False":
                            device.power_state = False
                        _LOGGER.debug("Device Power state '{}'".format(device.power_state))
                    elif eachArg in tone:
                        if eachArg == "tone.True":
                            device.prompt_tone = True                
                        elif eachArg == "tone.False":
                            device.prompt_tone = False
                        _LOGGER.debug("Device promt Tone '{}'".format(device.prompt_tone))
                    elif eachArg in eco:
                        if eachArg == "eco.True":
                            device.eco_mode = True                
                        elif eachArg == "eco.False":
                            device.eco_mode = False
                        _LOGGER.debug("Device Eco Mode '{}'".format(device.eco_mode))
                    elif eachArg in turbo:
                        if eachArg == "turbo.True":
                            device.turbo_mode = True                
                        elif eachArg == "turbo.False":
                            device.turbo_mode = False
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
                    elif len(eachArg) == 2:
                        device.target_temperature = int(eachArg)
                        _LOGGER.debug(device.target_temperature)
                    else: #unknown key´s
                        if eachArg != device_k1 and eachArg != device_token and eachArg != device_id and eachArg != device_ip:
                            _LOGGER.error("Given command '{}'is unknown".format(eachArg))

            # Errorhandling
            try: # Midea AC only supports auto Fanspeed in auto-Operationalmode.
                if device.operational_mode == ac.operational_mode_enum.auto:                    
                    device.fan_speed = ac.fan_speed_enum.Auto
                    _LOGGER.info("set auto-Fanspeed because of Auto-Operational Mode")
            except:
                _LOGGER.debug("device.operational_mode not given, this is not a Bug")
                
            try: #Midea AC only supports Temperature from 17 to 30 °C
                if int(device.target_temperature) < 17:
                    _LOGGER.info("Get Temperature '{}'. Allowed Temperature: 17-30, set target Temperature to 17°C".format(device.target_temperature))
                    device.target_temperature = 17
                elif int(device.target_temperature) > 30:
                    _LOGGER.info("Get Temperature '{}'. Allowed Temperature: 17-30, set target Temperature to 30°C".format(device.target_temperature))
                    device.target_temperature = 30
            except:
                _LOGGER.debug("device.target_temperature not given, this is not a Bug")

            # commit the changes with apply()
            device.apply()
            while device.online == False and retries <= 10: # retry 10 times
                retries += 1
                _LOGGER.debug("retry %s" %(retries))
                time.sleep(5)
                device.apply()
            
        if device.online == True:
            send_to_loxone(device)
        else:
            _LOGGER.info("Device is offline")
            print("Device is offline")
    
    finally:
        requests.get("http://%s:%s@%s:%s/dev/sps/io/Midea.AC_script/0" % (LoxUser, LoxPassword, LoxIP, LoxPort))


def send_to_loxone(device):
    requests.get("http://%s:%s@%s:%s/dev/sps/io/Midea.%s.power_state/%s" % (LoxUser, LoxPassword, LoxIP, LoxPort, device.id, device.power_state))
    requests.get("http://%s:%s@%s:%s/dev/sps/io/Midea.%s.audible_feedback/%s" % (LoxUser, LoxPassword, LoxIP, LoxPort, device.id, device.prompt_tone))
    requests.get("http://%s:%s@%s:%s/dev/sps/io/Midea.%s.target_temperature/%s" % (LoxUser, LoxPassword, LoxIP, LoxPort, device.id, device.target_temperature))
    requests.get("http://%s:%s@%s:%s/dev/sps/io/Midea.%s.operational_mode/%s" % (LoxUser, LoxPassword, LoxIP, LoxPort, device.id, device.operational_mode))
    requests.get("http://%s:%s@%s:%s/dev/sps/io/Midea.%s.fan_speed/%s" % (LoxUser, LoxPassword, LoxIP, LoxPort, device.id, device.fan_speed))
    requests.get("http://%s:%s@%s:%s/dev/sps/io/Midea.%s.swing_mode/%s" % (LoxUser, LoxPassword, LoxIP, LoxPort, device.id, device.swing_mode))
    requests.get("http://%s:%s@%s:%s/dev/sps/io/Midea.%s.eco_mode/%s" % (LoxUser, LoxPassword, LoxIP, LoxPort, device.id, device.eco_mode))
    requests.get("http://%s:%s@%s:%s/dev/sps/io/Midea.%s.turbo_mode/%s" % (LoxUser, LoxPassword, LoxIP, LoxPort, device.id, device.turbo_mode))
    requests.get("http://%s:%s@%s:%s/dev/sps/io/Midea.%s.indoor_temperature/%s" % (LoxUser, LoxPassword, LoxIP, LoxPort, device.id, device.indoor_temperature))
    requests.get("http://%s:%s@%s:%s/dev/sps/io/Midea.%s.outdoor_temperature/%s" % (LoxUser, LoxPassword, LoxIP, LoxPort, device.id, device.outdoor_temperature))
    _LOGGER.info("sending to Loxone for Midea.{} @ {} successful".format(device.id, device.ip))
    print("sending to Loxone for Midea.{} @ {} successful".format(device.id, device.ip))


# Start script
start_server()  
