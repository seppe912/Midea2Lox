#!/usr/bin/python3
from midea.client import client as midea_client
from midea.device import air_conditioning_device as ac
import sys
import requests
import configparser
import logging

#Miniserver Daten Laden
cfg = configparser.ConfigParser()
cfg.read('/opt/loxberry/config/plugins/Midea2Lox/midea2lox.cfg')
LoxIP = cfg.get('default','LoxIP')
LoxPassword = cfg.get('default','LoxPassword')
LoxUser = cfg.get('default','LoxUser')
MideaUser = cfg.get('default','MideaUser')
MideaPassword = cfg.get('default','MideaPassword')
UDP_Port = int(cfg.get('default','UDP_PORT'))
LoxberryIP = cfg.get('default','LoxberryIP')
DEBUG = cfg.get('default','DEBUG')

_LOGGER = logging.getLogger(__name__)
if DEBUG == "1":
	logging.basicConfig(level=logging.DEBUG, filename='/opt/loxberry/log/plugins/Midea2Lox/midea2lox.log')
	print("Debug is True")
	_LOGGER.debug("Debug is True")
else:
    logging.basicConfig(level=logging.INFO, filename='/opt/loxberry/log/plugins/Midea2Lox/midea2lox.log')

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
        global data
        data, addr = soc.recvfrom(1024)
        data = data.decode('utf-8')
        data = data.split(' ')
        print("Message: ", data)
        _LOGGER.info(data)
        try:
            Argumente = len(data)
            if Argumente == 8:
                print("Übertragung zu Midea wird gestartet")
                _LOGGER.info("Übertragung zu Midea wird gestartet")
                send_to_midea()
            elif data[0] == "status":
                print("Status Update wird gestartet")
                _LOGGER.info("Status Update wird gestartet")
                update_midea()
            else:
                print("Zu wenige Argumente")
                _LOGGER.error("Zu wenige Argumente erhalten! UEbertragung wird nicht gestartet")
        except:
            print("fehler beim uebertragen")
            _LOGGER.info("Fehler bei send_to_midea")
            import traceback
            traceback.print_exc()
            _LOGGER.info(traceback.print_exc())
            print("sende erneut")
            _LOGGER.info("sende erneut")
            requests.get("http://%s:%s@%s/dev/sps/io/Midea.AC_Fehlerschleife/1" % (LoxUser, LoxPassword, LoxIP,))
            while True:
                try:
                    if data[0] == "status":
                        update_midea()
                        requests.get("http://%s:%s@%s/dev/sps/io/Midea.AC_Fehlerschleife/0" % (LoxUser, LoxPassword, LoxIP,))
                        _LOGGER.info("Fehlerschleife beendet, erneutes senden OK")
                        break
                    else:
                        send_to_midea()
                        requests.get("http://%s:%s@%s/dev/sps/io/Midea.AC_Fehlerschleife/0" % (LoxUser, LoxPassword, LoxIP,))
                        _LOGGER.info("Fehlerschleife beendet, erneutes senden OK")
                        break
                except:
                    import time
                    time.sleep(30)
                    print("2. erneuter Versuch")
                    _LOGGER.error("Fehlerschleife aktiv! sende erneut, send_to_midea, solange bis kein Fehler mehr vorhanden ist")
					
    soc.close()
	
def send_to_midea():

	#Start
	requests.get("http://%s:%s@%s/dev/sps/io/Midea.AC_script/1" % (LoxUser, LoxPassword, LoxIP))
	
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
	requests.get("http://%s:%s@%s/dev/sps/io/Midea.power_state/%s" % (LoxUser, LoxPassword, LoxIP, device.power_state))
	requests.get("http://%s:%s@%s/dev/sps/io/Midea.audible_feedback/%s" % (LoxUser, LoxPassword, LoxIP, device.audible_feedback))
	requests.get("http://%s:%s@%s/dev/sps/io/Midea.target_temperature/%s" % (LoxUser, LoxPassword, LoxIP, device.target_temperature))
	requests.get("http://%s:%s@%s/dev/sps/io/Midea.operational_mode/%s" % (LoxUser, LoxPassword, LoxIP, device.operational_mode))
	requests.get("http://%s:%s@%s/dev/sps/io/Midea.fan_speed/%s" % (LoxUser, LoxPassword, LoxIP, device.fan_speed))
	requests.get("http://%s:%s@%s/dev/sps/io/Midea.swing_mode/%s" % (LoxUser, LoxPassword, LoxIP, device.swing_mode))
	requests.get("http://%s:%s@%s/dev/sps/io/Midea.eco_mode/%s" % (LoxUser, LoxPassword, LoxIP, device.eco_mode))
	requests.get("http://%s:%s@%s/dev/sps/io/Midea.turbo_mode/%s" % (LoxUser, LoxPassword, LoxIP, device.turbo_mode))
	requests.get("http://%s:%s@%s/dev/sps/io/Midea.indoor_temperature/%s" % (LoxUser, LoxPassword, LoxIP, device.indoor_temperature))
	requests.get("http://%s:%s@%s/dev/sps/io/Midea.outdoor_temperature/%s" % (LoxUser, LoxPassword, LoxIP, device.outdoor_temperature))
	requests.get("http://%s:%s@%s/dev/sps/io/Midea.id/%s" % (LoxUser, LoxPassword, LoxIP, device.id))
	requests.get("http://%s:%s@%s/dev/sps/io/Midea.name/%s" % (LoxUser, LoxPassword, LoxIP, device.name))
	requests.get("http://%s:%s@%s/dev/sps/io/Midea.AC_script/0" % (LoxUser, LoxPassword, LoxIP))

def update_midea():
	#Start
	requests.get("http://%s:%s@%s/dev/sps/io/Midea.AC_script/1" % (LoxUser, LoxPassword, LoxIP))
	
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
	requests.get("http://%s:%s@%s/dev/sps/io/Midea.power_state/%s" % (LoxUser, LoxPassword, LoxIP, device.power_state))
	requests.get("http://%s:%s@%s/dev/sps/io/Midea.audible_feedback/%s" % (LoxUser, LoxPassword, LoxIP, device.audible_feedback))
	requests.get("http://%s:%s@%s/dev/sps/io/Midea.target_temperature/%s" % (LoxUser, LoxPassword, LoxIP, device.target_temperature))
	requests.get("http://%s:%s@%s/dev/sps/io/Midea.operational_mode/%s" % (LoxUser, LoxPassword, LoxIP, device.operational_mode))
	requests.get("http://%s:%s@%s/dev/sps/io/Midea.fan_speed/%s" % (LoxUser, LoxPassword, LoxIP, device.fan_speed))
	requests.get("http://%s:%s@%s/dev/sps/io/Midea.swing_mode/%s" % (LoxUser, LoxPassword, LoxIP, device.swing_mode))
	requests.get("http://%s:%s@%s/dev/sps/io/Midea.eco_mode/%s" % (LoxUser, LoxPassword, LoxIP, device.eco_mode))
	requests.get("http://%s:%s@%s/dev/sps/io/Midea.turbo_mode/%s" % (LoxUser, LoxPassword, LoxIP, device.turbo_mode))
	requests.get("http://%s:%s@%s/dev/sps/io/Midea.indoor_temperature/%s" % (LoxUser, LoxPassword, LoxIP, device.indoor_temperature))
	requests.get("http://%s:%s@%s/dev/sps/io/Midea.outdoor_temperature/%s" % (LoxUser, LoxPassword, LoxIP, device.outdoor_temperature))
	requests.get("http://%s:%s@%s/dev/sps/io/Midea.id/%s" % (LoxUser, LoxPassword, LoxIP, device.id))
	requests.get("http://%s:%s@%s/dev/sps/io/Midea.name/%s" % (LoxUser, LoxPassword, LoxIP, device.name))
	requests.get("http://%s:%s@%s/dev/sps/io/Midea.AC_script/0" % (LoxUser, LoxPassword, LoxIP))

start_server()  
