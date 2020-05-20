#!/usr/bin/python3
# -*- coding: utf-8 -*-
from midea.client import client as midea_client
from midea.device import air_conditioning_device as ac
import sys
import requests
import configparser
import logging

# Miniserver Daten Laden
cfg = configparser.ConfigParser()
cfg.read('REPLACELBPCONFIGDIR/midea2lox.cfg')
MideaUser = cfg.get('default','MideaUser')
MideaPassword = cfg.get('default','MideaPassword')
UDP_Port = int(cfg.get('default','UDP_PORT'))
LoxberryIP = cfg.get('default','LoxberryIP')
DEBUG = cfg.get('default','DEBUG')
Miniserver = cfg.get('default','MINISERVER')

cfg.read('REPLACELBHOMEDIR/config/system/general.cfg')
LoxIP = cfg.get(Miniserver,'IPADDRESS')
LoxPort = cfg.get(Miniserver,'PORT')
LoxPassword = cfg.get(Miniserver,'PASS')
LoxUser = cfg.get(Miniserver,'ADMIN')

_LOGGER = logging.getLogger(__name__)
if DEBUG == "1":
    logging.basicConfig(level=logging.DEBUG, filename='REPLACELBPLOGDIR/midea2lox.log', format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s', datefmt='%d.%m %H:%M')
    print("Debug is True")
    _LOGGER.debug("Debug is True")
else:
    logging.basicConfig(level=logging.INFO, filename='REPLACELBPLOGDIR/midea2lox.log', format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s', datefmt='%d.%m %H:%M')

# Mainprogramm
def start_server():

    import socket
    soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # this is for easy starting/killing the app
    #soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print('Socket created')

    try:
        soc.bind((LoxberryIP, UDP_Port))
        print('Socket bind complete, listen at' , LoxberryIP, ":", UDP_Port)
        _LOGGER.info("Socket bind complete, listen at {}:{}".format(LoxberryIP, UDP_Port))
    except socket.error as msg:
        import sys
        print('Bind failed. Error : ' + str(sys.exc_info()))
        _LOGGER.error('Bind failed. Error : ' + str(sys.exc_info()))
        sys.exit()

    #Start listening on socket
    #soc.listen(2)
    print('Socket now listening')

    # for handling task in separate jobs we need threading
    #from threading import Thread

    # this will make an infinite loop needed for 
    # not reseting server for every client
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
            if Argumente == 8 or 9 and data[0] in key and data[1] in key and data[3] in key and data[4] in key and data[5] in key and data[6] in key and data[7] in key:
                print("send data to Midea Cloud")
                _LOGGER.info("send data to Midea Cloud")
                send_to_midea()
            elif data[0] == "status":
                print("starting Status update")
                _LOGGER.info("starting Status update")
                update_midea()
                _LOGGER.info("Status Update successful")
            else:
                for eachArg in data:
                    if eachArg not in key and eachArg != data[2]:
                        print("getting wrong Argument: ", eachArg)
                        _LOGGER.error("getting wrong Argument: '{}'. Please check your Loxone config.".format(eachArg))                        
                _LOGGER.info("allowed Arguments: {}".format(key))
        except:
            print("Error on send_to_midea")
            _LOGGER.info("Error on send_to_midea")
            requests.get("http://%s:%s@%s:%s/dev/sps/io/Midea.AC_script/0" % (LoxUser, LoxPassword, LoxIP, LoxPort))
    soc.close()

# send to Midea
def send_to_midea():

    #Start
    requests.get("http://%s:%s@%s:%s/dev/sps/io/Midea.AC_script/1" % (LoxUser, LoxPassword, LoxIP, LoxPort))
    
    # The client takes an App_Key, an account email address and a password
    client = midea_client('3742e9e5842d4ad59c2db887e12449f9', MideaUser, MideaPassword)
    
    # Log in right now, to check credentials (this step is optional, and will be called when listing devices)
    client.setup()
    
    # List devices. These are complex state holding objects, no other trickery needed from here. 
    devices = client.devices()
    
    for eachArg in data:   
            print(eachArg)
                
    # Midea AC only supports auto Fanspeed in auto-Operationalmode.
    if eval(data[3]) == ac.operational_mode_enum.auto:
        fanspeed = ac.fan_speed_enum.Auto
    else:
        fanspeed = eval(data[4])

    
    for device in devices:
    
    
        # Refresh the object with the actual state by querying it
        device.refresh()    
        print({
            'id': device.id,
            'name': device.name,
            'power_state': device.power_state,
            'audible_feedback': device.audible_feedback,
            'target_temperature': device.target_temperature,
            'operational_mode': device.operational_mode,
            'fan_speed': device.fan_speed,
            'swing_mode': device.swing_mode,
            'eco_mode': device.eco_mode,
            'turbo_mode': device.turbo_mode,
            'indoor_temperature': device.indoor_temperature,
            'outdoor_temperature': device.outdoor_temperature
        })

        # Set the state of the device and
        if Argumente == 9:            
            if device.id == str(data[8]):
                device.power_state = eval(data[0])
                device.audible_feedback = eval(data[1])
                device.target_temperature = int(data[2])
                device.operational_mode = eval(data[3])
                device.fan_speed = fanspeed
                device.swing_mode = eval(data[5])
                device.eco_mode = eval(data[6])
                device.turbo_mode = eval(data[7])
                # commit the changes with apply()
                device.apply()
                #prepare to finish
                #send to Loxone
                requests.get("http://%s:%s@%s:%s/dev/sps/io/Midea.%s.power_state/%s" % (LoxUser, LoxPassword, LoxIP, LoxPort, device.id, device.power_state))
                requests.get("http://%s:%s@%s:%s/dev/sps/io/Midea.%s.audible_feedback/%s" % (LoxUser, LoxPassword, LoxIP, LoxPort, device.id, device.audible_feedback))
                requests.get("http://%s:%s@%s:%s/dev/sps/io/Midea.%s.target_temperature/%s" % (LoxUser, LoxPassword, LoxIP, LoxPort, device.id, device.target_temperature))
                requests.get("http://%s:%s@%s:%s/dev/sps/io/Midea.%s.operational_mode/%s" % (LoxUser, LoxPassword, LoxIP, LoxPort, device.id, device.operational_mode))
                requests.get("http://%s:%s@%s:%s/dev/sps/io/Midea.%s.fan_speed/%s" % (LoxUser, LoxPassword, LoxIP, LoxPort, device.id, device.fan_speed))
                requests.get("http://%s:%s@%s:%s/dev/sps/io/Midea.%s.swing_mode/%s" % (LoxUser, LoxPassword, LoxIP, LoxPort, device.id, device.swing_mode))
                requests.get("http://%s:%s@%s:%s/dev/sps/io/Midea.%s.eco_mode/%s" % (LoxUser, LoxPassword, LoxIP, LoxPort, device.id, device.eco_mode))
                requests.get("http://%s:%s@%s:%s/dev/sps/io/Midea.%s.turbo_mode/%s" % (LoxUser, LoxPassword, LoxIP, LoxPort, device.id, device.turbo_mode))
                requests.get("http://%s:%s@%s:%s/dev/sps/io/Midea.%s.indoor_temperature/%s" % (LoxUser, LoxPassword, LoxIP, LoxPort, device.id, device.indoor_temperature))
                requests.get("http://%s:%s@%s:%s/dev/sps/io/Midea.%s.outdoor_temperature/%s" % (LoxUser, LoxPassword, LoxIP, LoxPort, device.id, device.outdoor_temperature))
                requests.get("http://%s:%s@%s:%s/dev/sps/io/Midea.%s.name/%s" % (LoxUser, LoxPassword, LoxIP, LoxPort, device.id, device.name))
                _LOGGER.info("Data sending to {} {} successful".format(device.id, device.name))
                
        elif Argumente == 8:
                _LOGGER.info("Bitte Loxone Config Updaten! Statuseingaenge muessen ab Midea2Lox V1.1 die ID vorangestellt haben, siehe LoxWiki. Auch beim senden muss die gewuenschte ID der zu steuernden Klimaanlage angegeben werden")
                device.power_state = eval(data[0])
                device.audible_feedback = eval(data[1])
                device.target_temperature = int(data[2])
                device.operational_mode = eval(data[3])
                device.fan_speed = fanspeed
                device.swing_mode = eval(data[5])
                device.eco_mode = eval(data[6])
                device.turbo_mode = eval(data[7])
                #send to Loxone
                device.apply()
                requests.get("http://%s:%s@%s:%s/dev/sps/io/Midea.power_state/%s" % (LoxUser, LoxPassword, LoxIP, LoxPort, device.power_state))
                requests.get("http://%s:%s@%s:%s/dev/sps/io/Midea.audible_feedback/%s" % (LoxUser, LoxPassword, LoxIP, LoxPort, device.audible_feedback))
                requests.get("http://%s:%s@%s:%s/dev/sps/io/Midea.target_temperature/%s" % (LoxUser, LoxPassword, LoxIP, LoxPort, device.target_temperature))
                requests.get("http://%s:%s@%s:%s/dev/sps/io/Midea.operational_mode/%s" % (LoxUser, LoxPassword, LoxIP, LoxPort, device.operational_mode))
                requests.get("http://%s:%s@%s:%s/dev/sps/io/Midea.fan_speed/%s" % (LoxUser, LoxPassword, LoxIP, LoxPort, device.fan_speed))
                requests.get("http://%s:%s@%s:%s/dev/sps/io/Midea.swing_mode/%s" % (LoxUser, LoxPassword, LoxIP, LoxPort, device.swing_mode))
                requests.get("http://%s:%s@%s:%s/dev/sps/io/Midea.eco_mode/%s" % (LoxUser, LoxPassword, LoxIP, LoxPort, device.eco_mode))
                requests.get("http://%s:%s@%s:%s/dev/sps/io/Midea.turbo_mode/%s" % (LoxUser, LoxPassword, LoxIP, LoxPort, device.turbo_mode))
                requests.get("http://%s:%s@%s:%s/dev/sps/io/Midea.indoor_temperature/%s" % (LoxUser, LoxPassword, LoxIP, LoxPort, device.indoor_temperature))
                requests.get("http://%s:%s@%s:%s/dev/sps/io/Midea.outdoor_temperature/%s" % (LoxUser, LoxPassword, LoxIP, LoxPort, device.outdoor_temperature))
                requests.get("http://%s:%s@%s:%s/dev/sps/io/Midea.id/%s" % (LoxUser, LoxPassword, LoxIP, LoxPort, device.id))
                requests.get("http://%s:%s@%s:%s/dev/sps/io/Midea.name/%s" % (LoxUser, LoxPassword, LoxIP, LoxPort, device.name))
                requests.get("http://%s:%s@%s:%s/dev/sps/io/Midea.AC_script/0" % (LoxUser, LoxPassword, LoxIP, LoxPort))
                _LOGGER.info("UEbertragung erfolgreich")

    requests.get("http://%s:%s@%s:%s/dev/sps/io/Midea.AC_script/0" % (LoxUser, LoxPassword, LoxIP, LoxPort))

# Update Midea status
def update_midea():
    #Start
    requests.get("http://%s:%s@%s:%s/dev/sps/io/Midea.AC_script/1" % (LoxUser, LoxPassword, LoxIP, LoxPort))
    
    # The client takes an App_Key, an account email address and a password
    client = midea_client('3742e9e5842d4ad59c2db887e12449f9', MideaUser, MideaPassword)
    
    # Log in right now, to check credentials (this step is optional, and will be called when listing devices)
    client.setup()
    
    # List devices. These are complex state holding objects, no other trickery needed from here. 
    devices = client.devices()
    
    
    for eachArg in data:   
            print(eachArg)
                
    for device in devices:
    
        # Refresh the object with the actual state by querying it
        device.refresh()    
        print({
            'id': device.id,
            'name': device.name,
            'power_state': device.power_state,
            'audible_feedback': device.audible_feedback,
            'target_temperature': device.target_temperature,
            'operational_mode': device.operational_mode,
            'fan_speed': device.fan_speed,
            'swing_mode': device.swing_mode,
            'eco_mode': device.eco_mode,
            'turbo_mode': device.turbo_mode,
            'indoor_temperature': device.indoor_temperature,
            'outdoor_temperature': device.outdoor_temperature
        })
        #prepare to finish
        #send to Loxone
        requests.get("http://%s:%s@%s:%s/dev/sps/io/Midea.%s.power_state/%s" % (LoxUser, LoxPassword, LoxIP, LoxPort, device.id, device.power_state))
        requests.get("http://%s:%s@%s:%s/dev/sps/io/Midea.%s.audible_feedback/%s" % (LoxUser, LoxPassword, LoxIP, LoxPort, device.id, device.audible_feedback))
        requests.get("http://%s:%s@%s:%s/dev/sps/io/Midea.%s.target_temperature/%s" % (LoxUser, LoxPassword, LoxIP, LoxPort, device.id, device.target_temperature))
        requests.get("http://%s:%s@%s:%s/dev/sps/io/Midea.%s.operational_mode/%s" % (LoxUser, LoxPassword, LoxIP, LoxPort, device.id, device.operational_mode))
        requests.get("http://%s:%s@%s:%s/dev/sps/io/Midea.%s.fan_speed/%s" % (LoxUser, LoxPassword, LoxIP, LoxPort, device.id, device.fan_speed))
        requests.get("http://%s:%s@%s:%s/dev/sps/io/Midea.%s.swing_mode/%s" % (LoxUser, LoxPassword, LoxIP, LoxPort, device.id, device.swing_mode))
        requests.get("http://%s:%s@%s:%s/dev/sps/io/Midea.%s.eco_mode/%s" % (LoxUser, LoxPassword, LoxIP, LoxPort, device.id, device.eco_mode))
        requests.get("http://%s:%s@%s:%s/dev/sps/io/Midea.%s.turbo_mode/%s" % (LoxUser, LoxPassword, LoxIP, LoxPort, device.id, device.turbo_mode))
        requests.get("http://%s:%s@%s:%s/dev/sps/io/Midea.%s.indoor_temperature/%s" % (LoxUser, LoxPassword, LoxIP, LoxPort, device.id, device.indoor_temperature))
        requests.get("http://%s:%s@%s:%s/dev/sps/io/Midea.%s.outdoor_temperature/%s" % (LoxUser, LoxPassword, LoxIP, LoxPort, device.id, device.outdoor_temperature))
        requests.get("http://%s:%s@%s:%s/dev/sps/io/Midea.%s.name/%s" % (LoxUser, LoxPassword, LoxIP, LoxPort, device.id, device.name))

    requests.get("http://%s:%s@%s:%s/dev/sps/io/Midea.AC_script/0" % (LoxUser, LoxPassword, LoxIP, LoxPort))

# Start script
start_server()  
