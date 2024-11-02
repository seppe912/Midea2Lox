#!REPLACELBPBINDIR/venv/bin/python3
# -*- coding: utf-8 -*-
import logging
import sys
import os

#set path
cfg_path = 'REPLACELBPCONFIGDIR' #### REPLACE LBPCONFIGDIR ####
log_path = 'REPLACELBPLOGDIR' #### REPLACE LBPLOGDIR ####
home_path = 'REPLACELBHOMEDIR' #### REPLACE LBHOMEDIR ####

# TCP Socket
async def start_server():
    script_runtime = datetime.now()
    _LOGGER.info("Midea2Lox Version: {} msmart Version: {}".format(Midea2Lox_Version, __version__))
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
        #while datetime.now().hour in range(2,10) or datetime.now().weekday() == 5:
        if os.path.getsize(log_path + '/midea2lox.log') > 500000:
        #while datetime.now().weekday() == 5:
            #### clean log
            open(log_path + '/midea2lox.log', 'w+')
            _LOGGER.info('Debuglog cleaned')
            _LOGGER.info("Midea2Lox Version: {} msmart Version: {}".format(Midea2Lox_Version, __version__))
            script_runtime = datetime.now()
        data, addr = soc.recvfrom(1024)
        data = data.decode('utf-8')
        data = data.split(' ')
        if data[0] != '0' and data[0] != '':
            print("Incomming Message from Loxone: ", data)
            _LOGGER.info("Incomming Message from Loxone: {}".format(data))
            try:
                print("send Message to Midea Appliance")
                _LOGGER.info("send Message to Midea Appliance")
                await send_to_midea(data)
            except:
                print('Error : ' + str(sys.exc_info()))
                _LOGGER.error(str(sys.exc_info()))
    soc.close()

# send to Midea Appliance over LAN/WLAN
async def send_to_midea(data):
    try: 
        #Start, set Loxone Script to online
        runtime = time.time()
        oldLox = 0
        #protocol = 2
        device_port = 6444
        retries = 0
        statusupdate = 0
        support_mode = 0
        device_id = None
        device_ip = None
        device_key = None
        device_token = None
        
        support_msmart_ng = {
            'ac.operational_mode_enum.auto' : 'ac.OperationalMode.AUTO', 
            'ac.operational_mode_enum.cool' : 'ac.OperationalMode.COOL', 
            'ac.operational_mode_enum.heat' : 'ac.OperationalMode.HEAT', 
            'ac.operational_mode_enum.dry' : 'ac.OperationalMode.DRY', 
            'ac.operational_mode_enum.fan_only' : 'ac.OperationalMode.FAN_ONLY', 
            'ac.fan_speed_enum.Auto' : 'ac.FanSpeed.AUTO',
            'ac.fan_speed_enum.Full' : 'ac.FanSpeed.FULL',
            'ac.fan_speed_enum.High' : 'ac.FanSpeed.HIGH',
            'ac.fan_speed_enum.Medium' : 'ac.FanSpeed.MEDIUM',
            'ac.fan_speed_enum.Low' : 'ac.FanSpeed.LOW',
            'ac.fan_speed_enum.Silent' : 'ac.FanSpeed.SILENT',
            'ac.swing_mode_enum.Horizontal' : 'ac.SwingMode.HORIZONTAL',
            'ac.swing_mode_enum.Off' : 'ac.SwingMode.OFF',
            'ac.swing_mode_enum.Vertical' : 'ac.SwingMode.VERTICAL',
            'ac.swing_mode_enum.Both' : 'ac.SwingMode.BOTH',
            }

        for eachArg in data: ### get device_id
            if len(eachArg) in range(10,20) and eachArg.isdigit():
                device_id = eachArg
                _LOGGER.debug("Device ID: '{}'".format(device_id))
            elif len(eachArg) == 64:
                device_key = eachArg
                _LOGGER.debug("Device Key: '{}'".format(device_key))
                #protocol = 3
                oldLox = 1
            elif len(eachArg) == 128:
                device_token = eachArg
                _LOGGER.debug("Device Token: '{}'".format(device_token))
                #protocol = 3
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
                
        if len(data) == 10 and data[0] == 'True' or len(data) == 10 and data[0] == 'False': ### support older Midea2Lox Versions <3.x
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
                    try: ##try to get Token and Key, skip for V2 Devices without Token/Key
                        device_key = cfg_devices.get('Midea_' + device_id,'key')
                        device_token = cfg_devices.get('Midea_' + device_id,'token')
                    except:
                        _LOGGER.debug('cant get Token/Key')
                        pass
            except:
                _LOGGER.warning('couldn´t find Device ID "%s", please do Discover or Check your Loxone config to send the right ID' % (device_id))
                
        if device_id == None:
            sys.exit('device ID unknown')
        elif device_ip == None:
            sys.exit('device IP unknown')
            
        
        if int(device_id) not in device_id_list: ### Init nur von neuen Devices
            _LOGGER.debug('Init eines neuen Devices')
            device = ac(ip=device_ip, device_id=int(device_id), port=device_port)
            try: ### support old configs without max_connection_lifetime
                device.set_max_connection_lifetime(int(cfg.get('default','maxConnectionLifetime')))
            except:
                _LOGGER.error('set maxConnectionLifetime to 90s. Please set maxConnectionLifetime and click "save and restart"')
                device.set_max_connection_lifetime(90)
            if device_key and device_token: ### support midea V3
                try:
                    await device.authenticate(device_token, device_key)
                except:
                    device._online = False
                    await send_to_loxone(device, 0)
                    sys.exit("Error on Authenticate")
                retries = 0
                
            else:
                _LOGGER.debug("use Midea V2")
                
            await device.get_capabilities()
            device.enable_energy_usage_requests = True   ### msmart-ng: Early tests have shown that many devices report energy usage without claiming support
            
            _LOGGER.info("%s", str({
                "device-id": device.id,
                "supported_modes": [str(mode.name) for mode in device.supported_operation_modes],
                "supported_swing_modes": [str(swingmode.name) for swingmode in device.supported_swing_modes],
                "supported_fan_speeds": [str(fanspeed.name) for fanspeed in device.supported_fan_speeds],
                "max_target_temperature": device.max_target_temperature,
                "min_target_temperature": device.min_target_temperature,
                "supports_custom_fan_speed": device.supports_custom_fan_speed,
                "supports_eco_mode": device.supports_eco,
                "supports_turbo": device.supports_turbo,
                "supports_freeze_protection": device.supports_freeze_protection,
                "supports_display_control": device.supports_display_control,
                "supports_filter_reminder": device.supports_filter_reminder,
                "supports_purifier": device.supports_purifier,
                "supports_humidity": device.supports_humidity,
                "supports_target_humidity": device.supports_target_humidity,    ###
                "supports_self_clean": device.supports_self_clean,              ###
                "supports_horizontal_swing_angle" : device.supports_horizontal_swing_angle,
                "supports_vertical_swing_angle" : device.supports_vertical_swing_angle,
                "supports_rate_selects": [str(rate.name) for rate in device.supported_rate_selects], ### ToDo
                "supports_breeze_away": device.supports_breeze_away, ### ToDo
                "supports_breeze_mild": device.supports_breeze_mild, ### ToDo
                "supports_breezeless": device.supports_breezeless, ### ToDo
                "supports_ieco": device.supports_ieco ### ToDo
            }))

            device_id_list.append(device.id)
            device_list.append(device)
            
        else:
            for devices in device_list:
                if int(device_id) == devices.id:
                    device = devices
            
        if statusupdate == 1: ### refresh() AC State
            try:
                await device.refresh()
                while device.online == False and retries < 2: ### retry 2 times on connection error
                    retries += 1
                    _LOGGER.warning("retry refresh %s/2" %(retries))
                    time.sleep(5)
                    await device.refresh()
            except Exception as error:
                device._online = False
                _LOGGER.error(error)

        else: ### apply() AC changes
            if support_mode == 1:
                _LOGGER.info("apply() on support Mode for Loxone Configs createt with Midea2Lox V2.x --> MQTT disabled. If you want to use MQTT you need to update your Loxoneconfig")
                key = ["True", "False", "ac.operational_mode_enum.auto", "ac.operational_mode_enum.cool", "ac.operational_mode_enum.heat", "ac.operational_mode_enum.dry", "ac.operational_mode_enum.fan_only", "ac.fan_speed_enum.High", "ac.fan_speed_enum.Medium", "ac.fan_speed_enum.Low", "ac.fan_speed_enum.Auto", "ac.fan_speed_enum.Silent", "ac.swing_mode_enum.Off", "ac.swing_mode_enum.Vertical", "ac.swing_mode_enum.Horizontal", "ac.swing_mode_enum.Both"] 
                if data[0] in key and data[1] in key and data[3] in key and data[4] in key and data[5] in key and data[6] in key and data[7] in key:
                    device.power_state = eval(data[0])
                    device.beep = eval(data[1])
                    device.target_temperature = int(data[2])
                    device.operational_mode = eval(support_msmart_ng[data[3]])
                    device.fan_speed = eval(support_msmart_ng[data[4]])
                    device.swing = eval(support_msmart_ng[data[5]])
                    device.eco = eval(data[6])
                    device.turbo = eval(data[7])
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
                if ((device_key and device_token) and len(data) != 12) or len(data) != 10: #if not all settings are sent from loxone, refresh() is neccessary.
                    try:
                        await device.refresh()
                        while device.online == False and retries < 2: # retry 2 times on connection error
                            retries += 1
                            _LOGGER.warning("retry refresh %s/2" %(retries))
                            time.sleep(5)
                            await device.refresh()
                    except Exception as error:
                        device._online = False
                        await send_to_loxone(device, support_mode)
                        raise error
                    
                #set all allowed key´s for Loxone input
                power = ["power.True", "power.False"]
                tone = ["tone.True", "tone.False"]
                operation = ["ac.operational_mode_enum.auto", "ac.operational_mode_enum.cool", "ac.operational_mode_enum.heat", "ac.operational_mode_enum.dry", "ac.operational_mode_enum.fan_only"] 
                swing_modes = ["ac.swing_mode_enum.Off", "ac.swing_mode_enum.Vertical", "ac.swing_mode_enum.Horizontal", "ac.swing_mode_enum.Both"]
                eco = ["eco.True", "eco.False"]
                turbo = ["turbo.True", "turbo.False"]
                display = ["toggle_Display"]
                freeze = ["freeze.True", "freeze.False"]
                sleep = ["sleep.True", "sleep.False"]
                follow = ["follow.True", "follow.False"]
                purifier = ["purifier.True", "purifier.False"]
                self_clean = ["self_clean.True", "self_clean.False"]
                rate_select = ["rate_select.OFF", "rate_select.GEAR_50", "rate_select.GEAR_75", "rate_select.LEVEL_1", "rate_select.LEVEL_2", "rate_select.LEVEL_3", "rate_select.LEVEL_4", "rate_select.LEVEL_5"]
                #BreezeModes = ["BreezeMode.OFF","BreezeMode.BREEZE_AWAY","BreezeMode.BREEZE_MILD","BreezeMode.BREEZELESS"]
                breeze_away = ["breeze_away.True","breeze_away.False"]
                breeze_mild = ["breeze_mild.True","breeze_mild.False"]
                breezeless = ["breezeless.True","breezeless.False"]
                ieco = ["ieco.True", "ieco.False"]
                
                for eachArg in data: #find keys from Loxone to msmart
                    if eachArg in power:
                        device.power_state = eval(eachArg.split(".")[1])
                        _LOGGER.debug("Device Power state '{}'".format(device.power_state))
                    elif eachArg in tone:
                        device.beep = eval(eachArg.split(".")[1])                
                        _LOGGER.debug("Device promt Tone '{}'".format(device.beep))
                    elif eachArg in eco:
                        if device.supports_eco:
                            device.eco = eval(eachArg.split(".")[1])                
                            _LOGGER.debug("Device Eco Mode '{}'".format(device.eco))
                        else:
                            _LOGGER.warning("device is not capable of property {}".format(eachArg))
                    elif eachArg in turbo:
                        if device.supports_turbo:
                            device.turbo = eval(eachArg.split(".")[1])                
                            _LOGGER.debug("Device Turbo Mode '{}'".format(device.turbo))
                        else:
                            _LOGGER.warning("device is not capable of property {}".format(eachArg))
                    elif eachArg in operation:
                        device.operational_mode = eval(support_msmart_ng[eachArg])
                        _LOGGER.debug(device.operational_mode)
                    elif "fan_speed_enum" in eachArg:
                        if eachArg.split(".")[2].isdigit():
                            if device.supports_custom_fan_speed:
                                device.fan_speed = int(eachArg.split(".")[2])
                            else:
                                _LOGGER.warning("device is not capable of property {}".format(eachArg))
                        else:
                            device.fan_speed = eval('ac.FanSpeed.' + str(eachArg.split(".")[2].upper()))
                        _LOGGER.debug(device.fan_speed)
                    elif eachArg in swing_modes:
                        device.swing_mode = eval(support_msmart_ng[eachArg])
                        _LOGGER.debug(device.swing)
                    elif len(eachArg) == 2 and eachArg.isdigit():
                        device.target_temperature = int(eachArg)
                        _LOGGER.debug(device.target_temperature)
                    elif eachArg in display:
                        if device.supports_display_control:
                            device.toggle_display()
                            _LOGGER.debug('toggle_Display')
                        else:
                            _LOGGER.warning("device is not capable of property {}".format(eachArg))
                    elif eachArg.split(".")[0] == "humidity":
                        if device.supports_humidity:
                            device.target_humidity = eval(eachArg.split(".")[1])
                            _LOGGER.debug(device.target_humidity)
                        else:
                            _LOGGER.warning("device is not capable of property {}".format(eachArg))
                    elif eachArg.split(".")[0] == "h_swing_angle":
                        if device.supports_horizontal_swing_angle:
                            device.horizontal_swing_angle = eval('ac.SwingAngle.' + eachArg.split(".")[1])
                            _LOGGER.debug(device.horizontal_swing_angle)
                        else:
                            _LOGGER.warning("device is not capable of property {}".format(eachArg))
                    elif eachArg.split(".")[0] == "v_swing_angle":
                        if device.supports_vertical_swing_angle:
                            device.vertical_swing_angle = eval('ac.SwingAngle.' + eachArg.split(".")[1])
                            _LOGGER.debug(device.vertical_swing_angle)
                        else:
                            _LOGGER.warning("device is not capable of property {}".format(eachArg))
                    elif eachArg in freeze:
                        if device.supports_freeze_protection:
                            device.freeze_protection = eval(eachArg.split(".")[1])
                            _LOGGER.debug(device.freeze_protection)
                        else:
                            _LOGGER.warning("device is not capable of property {}".format(eachArg))
                    elif eachArg in sleep:
                        device.sleep = eval(eachArg.split(".")[1])
                        _LOGGER.debug(device.sleep)
                    elif eachArg in follow:
                        device.follow_me = eval(eachArg.split(".")[1])
                        _LOGGER.debug(device.follow_me)
                    elif eachArg in purifier:
                        if device.supports_purifier:
                            device.purifier = eval(eachArg.split(".")[1])
                            _LOGGER.debug(device.purifier)
                        else:
                            _LOGGER.warning("device is not capable of property {}".format(eachArg))
                    elif eachArg in self_clean:
                        if device.supports_self_clean:
                            device.self_clean_active = eval(eachArg.split(".")[1])
                            _LOGGER.debug(device.self_clean_active)
                        else:
                            _LOGGER.warning("device is not capable of property {}".format(eachArg))
                    elif eachArg in rate_select: ### ToDo
                        if eachArg in device.supported_rate_selects:
                            device.rate_select = eval(eachArg.split(".")[1])
                            _LOGGER.debug(device.rate_select)
                        else:
                            _LOGGER.warning("device is not capable of property {}".format(eachArg))
                    # elif eachArg in BreezeModes: ### ToDo
                        # device.BreezeMode = eval(eachArg.split(".")[1])
                        # _LOGGER.debug(device.BreezeMode)
                    elif eachArg in breeze_away: ### ToDo
                        if device.supports_breeze_away:
                            device.breeze_away = eval(eachArg.split(".")[1])
                            _LOGGER.debug(device.breeze_away)
                        else:
                            _LOGGER.warning("device is not capable of property {}".format(eachArg))
                    elif eachArg in breeze_mild: ### ToDo
                        if device.supports_breeze_mild:
                            device.breeze_mild = eval(eachArg.split(".")[1])
                            _LOGGER.debug(device.breeze_mild)
                        else:
                            _LOGGER.warning("device is not capable of property {}".format(eachArg))
                    elif eachArg in breezeless: ### ToDo
                        if device.supports_breezeless:
                            device.breezeless = eval(eachArg.split(".")[1])
                            _LOGGER.debug(device.breezeless)
                        else:
                            _LOGGER.warning("device is not capable of property {}".format(eachArg))
                    elif eachArg in ieco: ### ToDo
                        if device.supports_ieco:
                            device.ieco = eval(eachArg.split(".")[1])
                            _LOGGER.debug(device.ieco)
                        else:
                            _LOGGER.warning("device is not capable of property {}".format(eachArg))
                    else: #unknown key´s
                        if len(eachArg) != 64 and len(eachArg) != 128 and eachArg != device_id and eachArg != device_ip:
                            _LOGGER.error("Given command '{}' is unknown".format(eachArg))
                                
            # Errorhandling
            # Midea AC only supports auto Fanspeed in auto-Operationalmode.
            if (device.operational_mode.name == support_msmart_ng['ac.operational_mode_enum.auto']) and (device.fan_speed.name != support_msmart_ng['ac.fan_speed.auto']):                    
                device.fan_speed = ac.FanSpeed.AUTO
                _LOGGER.info("set auto-Fanspeed because of Auto-Operational Mode")
            if (device.freeze_protection == True) and (device.operational_mode.name != support_msmart_ng['ac.operational_mode_enum.heat']):
                device.operational_mode = ac.OperationalMode.HEAT
                _LOGGER.info("set Heatmode to get into Freezeprotection Mode")
            
            #set only accepted temperatures
            if int(device.target_temperature) < device.min_target_temperature:
                _LOGGER.warning("Get Temperature {}. Allowed Temperature: {}-{}, set target Temperature to {}".format(device.target_temperature,device.min_target_temperature,device.max_target_temperature,device.min_target_temperature))
                device.target_temperature = device.min_target_temperature
            elif int(device.target_temperature) > device.max_target_temperature:
                _LOGGER.warning("Get Temperature {}. Allowed Temperature: {}-{}, set target Temperature to {}".format(device.target_temperature,device.min_target_temperature,device.max_target_temperature,device.max_target_temperature))
                device.target_temperature = device.max_target_temperature

            # commit the changes with apply()
            try:
                await device.apply()
                while device.online == False and retries < 2: # retry 2 times on connection error
                    retries += 1
                    _LOGGER.warning("retry apply %s/2" %(retries))
                    time.sleep(5)
                    await device.apply()
            except Exception as error:
                device._online = False
                _LOGGER.error(error)
                
        if device.online == True:
            if statusupdate == 1:
                _LOGGER.info("Statusupdate for Midea.{} @ {} successful. Runtime: {}s".format(device.id, device.ip,round(time.time()-runtime,2)))
            else:
                _LOGGER.info("Set new state for Midea.{} @ {} successful. Runtime: {}s".format(device.id, device.ip,round(time.time()-runtime,2)))
        else:
            _LOGGER.error("Device is offline")
  
        await send_to_loxone(device, support_mode)

    except Exception as e:
        _LOGGER.error(e)
    
    finally:
        _LOGGER.debug("{}s".format(round(time.time()-runtime,2)))
        
        
async def send_to_loxone(device, support_mode):
    r_error = 0

    address_loxone = ("http://%s:%s@%s:%s/dev/sps/io/" % (LoxUser, LoxPassword, LoxIP, LoxPort))    

    try:
        addresses = [
            ("Midea/%s/power_state,%s" % (device.id, int(device.power_state))),                                                                     #power_state
            ("Midea/%s/audible_feedback,%s" % (device.id, int(device.beep))),                                                                       #prompt_tone
            ("Midea/%s/target_temperature,%s" % (device.id, device.target_temperature)),                                                            #target_temperature
            ("Midea/%s/operational_mode,operational_mode_enum.%s" % (device.id, device.operational_mode.name.lower())),                             #operational_mode
            ("Midea/%s/fan_speed,fan_speed_enum.%s" % (device.id, device.fan_speed.name.capitalize() if type(device.fan_speed) != int else device.fan_speed)),#fan_speed
            ("Midea/%s/swing_mode,swing_mode_enum.%s" % (device.id, device.swing_mode.name.capitalize())),                                          #swing_mode
            ("Midea/%s/eco_mode,%s" % (device.id, int(device.eco))),                                                                                #eco_mode
            ("Midea/%s/turbo_mode,%s" % (device.id, int(device.turbo))),                                                                            #turbo_mode
            ("Midea/%s/indoor_temperature,%s" % (device.id, device.indoor_temperature)),                                                            #indoor_temperature
            ("Midea/%s/outdoor_temperature,%s" % (device.id, device.outdoor_temperature)),                                                          #outdoor_temperature
            ("Midea/%s/display_on,%s" % (device.id, int(device.display_on))),                                                                       #display_on
            ("Midea/%s/online,%s" % (device.id, int(device.online))),                                                                               #device.online --> device.online since msmart 0.1.32
            ("Midea/%s/target_humidity,%s" % (device.id, device.target_humidity)),                                                                  #Humidity
            ("Midea/%s/indoor_humidity,%s" % (device.id, device.indoor_humidity)),                                                                  #Humidity
            ("Midea/%s/filter_alert,%s" % (device.id, device.filter_alert)),                                                                        #Filter Alert --untestet--
            ("Midea/%s/horizontal_swing_angle,%s" % (device.id, device.horizontal_swing_angle.name)),                                               #Horizontal swing Angle
            ("Midea/%s/vertical_swing_angle,%s" % (device.id, device.vertical_swing_angle.name)),                                                   #Vertical swing Angle
            ("Midea/%s/freeze_protection_mode,%s" % (device.id, device.freeze_protection)),                                                         #Freeze Protection
            ("Midea/%s/sleep_mode,%s" % (device.id, device.sleep)),                                                                                 #Sleep Mode
            ("Midea/%s/follow_me,%s" % (device.id, device.follow_me)),                                                                              #Follow Me
            ("Midea/%s/purifier,%s" % (device.id, device.purifier)),                                                                                #Purifier
            ("Midea/%s/total_energy_usage,%s" % (device.id, device.total_energy_usage)),                                                            #Total Energy in KWh
            ("Midea/%s/current_energy_usage,%s" % (device.id, device.current_energy_usage)),                                                        #current Energy in KWh
            ("Midea/%s/real_time_power_usage,%s" % (device.id, device.real_time_power_usage)),                                                      #real time Power usage
            ("Midea/%s/self_clean_active,%s" % (device.id, device.self_clean_active)),                                                              #self clean
            ("Midea/%s/rate_select,%s" % (device.id, device.rate_select)),                                                                          #rate select
            ("Midea/%s/breeze_mode,%s" % (device.id, device._breeze_mode)),                                                                         #BreezeMode
            ("Midea/%s/ieco,%s" % (device.id, device.ieco))                                                                                         #ieco
            ]
    except Exception as e:
        _LOGGER.error(e)

    if MQTT == 1 and support_mode == 0 and mqtt_error == 0: # publish over MQTT
        if device.online == True:
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
        _LOGGER.info("Device is {}! Send status to MQTTGateway for Midea.{} @ {} succesful".format("Online" if device.online else "Offline",device.id, device.ip))
            
    else: #Publish to Loxone Inputs over HTTP
        if device.online == True:
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
            _LOGGER.info("Device is {}! Set Loxone Inputs over HTTP for Midea.{} @ {} successful".format("Online" if device.online else "Offline",device.id, device.ip))


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
    _LOGGER.info("MQTT Disconnected")
    _LOGGER.debug("Publishing: MsgNum:%s: 'Midea2Lox/connection/status','disconnected'" % (publish[1]))
    

##########

try:
    from msmart.device import AirConditioner as ac
    from msmart import __version__
    import requests
    import configparser
    import time
    from ipaddress import ip_address, IPv4Address
    import paho.mqtt.client as mqtt
    import json
    import asyncio
    from datetime import datetime, timedelta

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
       logging.basicConfig(level=logging.DEBUG, filename= log_path + '/midea2lox.log', format='%(asctime)s %(name)-12s %(levelname)-8s :%(lineno)d %(message)s', datefmt='%d.%m %H:%M')
       print("Debug is True")
       _LOGGER.debug("Debug is True")
    else:
       logging.basicConfig(level=logging.INFO, filename= log_path + '/midea2lox.log', format='%(asctime)s %(name)-12s %(levelname)-8s :%(lineno)d %(message)s', datefmt='%d.%m %H:%M')
    
    ###Version
    try: # check if MQTTgateway is installed or not and set MQTT Client settings
        with open(home_path + '/data/system/plugindatabase.json') as jsonFile:
            jsonObject = json.load(jsonFile)
            jsonFile.close()
        Midea2Lox_Version = str(jsonObject["plugins"]["ef8d4aab121cb54f6379fff540319792"]["version"])
    except:
        _LOGGER.debug('cant find Midea2Lox Version')
        Midea2Lox_Version = 'Unknown'
    
    #MQTT
    try: # check if MQTTgateway is installed or not and set MQTT Client settings
        with open(home_path + '/config/system/general.json') as jsonFile:
            jsonObject = json.load(jsonFile)
            jsonFile.close()
        LoxberryVersion = int(str(jsonObject["Base"]["Version"])[:1])
        MQTTuser = jsonObject["Mqtt"]["Brokeruser"]
        MQTTpass = jsonObject["Mqtt"]["Brokerpass"]
        MQTTport = jsonObject["Mqtt"]["Brokerport"]
        MQTThost = jsonObject["Mqtt"]["Brokerhost"]
        client = mqtt.Client(client_id='Midea2Lox')
        client.username_pw_set(MQTTuser, MQTTpass)
        client.on_connect = on_connect
        client.on_disconnect = on_disconnect
        client.will_set('Midea2Lox/connection/status','disconnected',qos=2, retain=True)
        if LoxberryVersion <= 2:
            _LOGGER.info('found MQTT Gateway Plugin - publish over MQTT except on Midea2Lox support_mode')
        else:
            _LOGGER.info('got MQTT Settings - publish over MQTT except on Midea2Lox support_mode')
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
device_list = []
device_id_list = []
asyncio.run(start_server())
