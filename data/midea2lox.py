#!/usr/bin/python3
# -*- coding: utf-8 -*-
import logging
import sys
    
try:
    from msmart.device import air_conditioning_device as ac
    from msmart.device import device as midea_device
    from msmart.device import convert_device_id_int
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

    import socket
    soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print('Socket created')

    try:
        soc.bind((LoxberryIP, UDP_Port))
        print('Socket bind complete, listen at' , LoxberryIP, ":", UDP_Port)
        _LOGGER.info("Socket bind complete, listen at {}:{}".format(LoxberryIP, UDP_Port))
    except socket.error as msg:
        print('Bind failed. Error : ' + str(sys.exc_info()))
        _LOGGER.error('Bind failed. Error : ' + str(sys.exc_info()))
        sys.exit()

    print('Socket now listening')

    while True:
        key = ["True", "False", "ac.operational_mode_enum.auto", "ac.operational_mode_enum.cool", "ac.operational_mode_enum.heat", "ac.operational_mode_enum.dry", "ac.operational_mode_enum.fan_only", "ac.fan_speed_enum.High", "ac.fan_speed_enum.Medium", "ac.fan_speed_enum.Low", "ac.fan_speed_enum.Auto", "ac.fan_speed_enum.Silent", "ac.swing_mode_enum.Off", "ac.swing_mode_enum.Vertical", "ac.swing_mode_enum.Horizontal", "ac.swing_mode_enum.Both"] 
        global data
        data, addr = soc.recvfrom(1024)
        data = data.decode('utf-8')
        data = data.split(' ')
        print("Incomming Message from Loxone: ", data)
        _LOGGER.info("Incomming Message from Loxone: {}".format(data))
        try:
            global Argumente
            Argumente = len(data)
            if Argumente == 8:
                print("On Midea2Lox V2.0 you need to send your Device ID and Device IP, please check your Loxone Config and see in Loxwiki: https://www.loxwiki.eu/display/LOXBERRY/Midea2Lox")
                _LOGGER.info("On Midea2Lox V2.0 you need to send your Device ID and Device IP, please check your Loxone Config and see in Loxwiki: https://www.loxwiki.eu/display/LOXBERRY/Midea2Lox")
                exit()
            elif Argumente == 10 and data[0] in key and data[1] in key and data[3] in key and data[4] in key and data[5] in key and data[6] in key and data[7] in key:
                print("send data to Midea Appliance")
                _LOGGER.info("send data to Midea Appliance %s @ %s" % (data[8], data[9]))
                send_to_midea()
            elif data[0] == "status" and Argumente == 3:
                print("starting Status update")
                _LOGGER.info("starting Status update")
                update_midea()
            elif data[0] == "status" and Argumente == 1:
                print("On Midea2Lox V2.0 you need to send your Device ID and Device IP, please check your Loxone Config and see in Loxwiki: https://www.loxwiki.eu/display/LOXBERRY/Midea2Lox")
                _LOGGER.info("On Midea2Lox V2.0 you need to send your Device ID and Device IP, please check your Loxone Config and see in Loxwiki: https://www.loxwiki.eu/display/LOXBERRY/Midea2Lox")
            else:
                if Argumente == 10:
                    for eachArg in data:
                        if eachArg not in key and eachArg != data[2] and eachArg != data[8] and eachArg != data[9]:
                            print("getting wrong Argument: ", eachArg)
                            _LOGGER.error("getting wrong Argument: '{}'. Please check your Loxone config.".format(eachArg))                        
                    _LOGGER.info("allowed Arguments: {}".format(key))
                else:
                    for eachArg in data:
                        if eachArg not in key and eachArg != data[2]:
                            print("getting wrong Argument: ", eachArg)
                            _LOGGER.error("getting wrong Argument: '{}'. Please check your Loxone config.".format(eachArg))                        
                    _LOGGER.info("allowed Arguments: {}".format(key))
        except:
            print('Error : ' + str(sys.exc_info()))
            _LOGGER.error(str(sys.exc_info()))
            requests.get("http://%s:%s@%s:%s/dev/sps/io/Midea.AC_script/0" % (LoxUser, LoxPassword, LoxIP, LoxPort))
    soc.close()


# send to Midea Appliance over LAN/WLAN
def send_to_midea():

    #Start, set Loxone Script to active
    try: 
        requests.get("http://%s:%s@%s:%s/dev/sps/io/Midea.AC_script/1" % (LoxUser, LoxPassword, LoxIP, LoxPort))
        
        device_ip = str(data[9])
        device_id = int(data[8])

        client = midea_device(device_ip, int(device_id))
        device = client.setup()
        
        # Print Loxone sent Arguments
        for eachArg in data:   
            print(eachArg)
            _LOGGER.debug(eachArg)
                    
        # Midea AC only supports auto Fanspeed in auto-Operationalmode.
        if eval(data[3]) == ac.operational_mode_enum.auto:
            fanspeed = ac.fan_speed_enum.Auto
        else:
            fanspeed = eval(data[4])
     
        
        # Set the state of the device and
        device.power_state = eval(data[0])
        device.prompt_tone = eval(data[1])
        device.target_temperature = int(data[2])
        device.operational_mode = eval(data[3])
        device.fan_speed = fanspeed
        device.swing_mode = eval(data[5])
        device.eco_mode = eval(data[6])
        device.turbo_mode = eval(data[7])
        
        # commit the changes with apply()
        device.apply()
        
        if device.support == True:
            
            # msmart send hex ID, get it back to Decimal Number for Loxone Inputs
            id = convert_device_id_int(device.id)
            
            #send to Loxone
            requests.get("http://%s:%s@%s:%s/dev/sps/io/Midea.%s.power_state/%s" % (LoxUser, LoxPassword, LoxIP, LoxPort, id, device.power_state))
            requests.get("http://%s:%s@%s:%s/dev/sps/io/Midea.%s.audible_feedback/%s" % (LoxUser, LoxPassword, LoxIP, LoxPort, id, device.prompt_tone))
            requests.get("http://%s:%s@%s:%s/dev/sps/io/Midea.%s.target_temperature/%s" % (LoxUser, LoxPassword, LoxIP, LoxPort, id, device.target_temperature))
            requests.get("http://%s:%s@%s:%s/dev/sps/io/Midea.%s.operational_mode/%s" % (LoxUser, LoxPassword, LoxIP, LoxPort, id, device.operational_mode))
            requests.get("http://%s:%s@%s:%s/dev/sps/io/Midea.%s.fan_speed/%s" % (LoxUser, LoxPassword, LoxIP, LoxPort, id, device.fan_speed))
            requests.get("http://%s:%s@%s:%s/dev/sps/io/Midea.%s.swing_mode/%s" % (LoxUser, LoxPassword, LoxIP, LoxPort, id, device.swing_mode))
            requests.get("http://%s:%s@%s:%s/dev/sps/io/Midea.%s.eco_mode/%s" % (LoxUser, LoxPassword, LoxIP, LoxPort, id, device.eco_mode))
            requests.get("http://%s:%s@%s:%s/dev/sps/io/Midea.%s.turbo_mode/%s" % (LoxUser, LoxPassword, LoxIP, LoxPort, id, device.turbo_mode))
            requests.get("http://%s:%s@%s:%s/dev/sps/io/Midea.%s.indoor_temperature/%s" % (LoxUser, LoxPassword, LoxIP, LoxPort, id, device.indoor_temperature))
            requests.get("http://%s:%s@%s:%s/dev/sps/io/Midea.%s.outdoor_temperature/%s" % (LoxUser, LoxPassword, LoxIP, LoxPort, id, device.outdoor_temperature))
            _LOGGER.info("sending to Loxone for Midea.{} @ {} successful".format(id, device.ip))
            print("sending to Loxone for Midea.{} @ {} successful".format(id, device.ip))
        else:
            _LOGGER.info("Device Midea.{} @ {} is not supportet".format(id, device.ip))
            print("Device Midea.{} @ {} is not supportet".format(id, device.ip))
    finally:
        requests.get("http://%s:%s@%s:%s/dev/sps/io/Midea.AC_script/0" % (LoxUser, LoxPassword, LoxIP, LoxPort))


# Update Midea status
def update_midea():
    #Start, set Loxone Script to active
    try:
        requests.get("http://%s:%s@%s:%s/dev/sps/io/Midea.AC_script/1" % (LoxUser, LoxPassword, LoxIP, LoxPort))
        
        device_ip = str(data[2])
        device_id = int(data[1])
        
        client = midea_device(device_ip, int(device_id))
        device = client.setup()
        
        # Refresh the object with the actual state by querying it
        device.refresh()   
        if device.support == True:
            print({
                'id hex': device.id,
                #'name': device.name,
                'power_state': device.power_state,
                'audible_feedback': device.prompt_tone,
                'target_temperature': device.target_temperature,
                'operational_mode': device.operational_mode,
                'fan_speed': device.fan_speed,
                'swing_mode': device.swing_mode,
                'eco_mode': device.eco_mode,
                'turbo_mode': device.turbo_mode,
                'indoor_temperature': device.indoor_temperature,
                'outdoor_temperature': device.outdoor_temperature
            })
            
            # msmart send hex ID, get it back to Decimal Number for Loxone Inputs
            id = convert_device_id_int(device.id)

            _LOGGER.info("Status Update for Midea.{} @ {} successful".format(id, device.ip))
            #send to Loxone
            requests.get("http://%s:%s@%s:%s/dev/sps/io/Midea.%s.power_state/%s" % (LoxUser, LoxPassword, LoxIP, LoxPort, id, device.power_state))
            requests.get("http://%s:%s@%s:%s/dev/sps/io/Midea.%s.audible_feedback/%s" % (LoxUser, LoxPassword, LoxIP, LoxPort, id, device.prompt_tone))
            requests.get("http://%s:%s@%s:%s/dev/sps/io/Midea.%s.target_temperature/%s" % (LoxUser, LoxPassword, LoxIP, LoxPort, id, device.target_temperature))
            requests.get("http://%s:%s@%s:%s/dev/sps/io/Midea.%s.operational_mode/%s" % (LoxUser, LoxPassword, LoxIP, LoxPort, id, device.operational_mode))
            requests.get("http://%s:%s@%s:%s/dev/sps/io/Midea.%s.fan_speed/%s" % (LoxUser, LoxPassword, LoxIP, LoxPort, id, device.fan_speed))
            requests.get("http://%s:%s@%s:%s/dev/sps/io/Midea.%s.swing_mode/%s" % (LoxUser, LoxPassword, LoxIP, LoxPort, id, device.swing_mode))
            requests.get("http://%s:%s@%s:%s/dev/sps/io/Midea.%s.eco_mode/%s" % (LoxUser, LoxPassword, LoxIP, LoxPort, id, device.eco_mode))
            requests.get("http://%s:%s@%s:%s/dev/sps/io/Midea.%s.turbo_mode/%s" % (LoxUser, LoxPassword, LoxIP, LoxPort, id, device.turbo_mode))
            requests.get("http://%s:%s@%s:%s/dev/sps/io/Midea.%s.indoor_temperature/%s" % (LoxUser, LoxPassword, LoxIP, LoxPort, id, device.indoor_temperature))
            requests.get("http://%s:%s@%s:%s/dev/sps/io/Midea.%s.outdoor_temperature/%s" % (LoxUser, LoxPassword, LoxIP, LoxPort, id, device.outdoor_temperature))
            _LOGGER.info("sending to Loxone for Midea.{} @ {} successful".format(id, device.ip))
            print("sending to Loxone for Midea.{} @ {} successful".format(id, device.ip))
        else:
            _LOGGER.info("Device Midea.{} @ {} is not supportet".format(id, device.ip))
            print("Device Midea.{} @ {} is not supportet".format(id, device.ip))
    finally:
        requests.get("http://%s:%s@%s:%s/dev/sps/io/Midea.AC_script/0" % (LoxUser, LoxPassword, LoxIP, LoxPort))


# Start script
start_server()  
