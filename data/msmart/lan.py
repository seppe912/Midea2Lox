# -*- coding: UTF-8 -*-
import logging
import datetime
import socket
import sys
import time
from msmart.security import security

VERSION = '0.1.20'

_LOGGER = logging.getLogger(__name__)


class lan:
    def __init__(self, device_ip, device_id):
        self.device_ip = device_ip
        self.device_id = device_id
        self.device_port = 6444
        self.security = security()
        self._retries = 0

    def request(self, message):
        # Create a TCP/IP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(8)
        
        try:
            # Connect the Device
            device_address = (self.device_ip, self.device_port)
            sock.connect(device_address)
            # Send data
            _LOGGER.debug("Sending to {}:{} {}".format(
                self.device_ip, self.device_port, message.hex()))
            sock.sendall(message)

            # Received data
            response = sock.recv(512)
        except socket.timeout:
            self._retries += 1
            _LOGGER.error(str(sys.exc_info()))
            if(self._retries <= 2):
                _LOGGER.info("wait 3 seconds, and retry")
                time.sleep(3) #give it some time
                _LOGGER.info("retry %s/2 @ %s:%s " %(self._retries, self.device_ip, self.device_port))
                return self.request(message)
            else:
                return bytearray(0)
        except socket.error:
            self._retries += 1
            _LOGGER.error(str(sys.exc_info()))
            if(self._retries <= 10):
                _LOGGER.info("wait 10 seconds, and retry")
                time.sleep(10) #give it some time
                _LOGGER.info("retry %s/10 @ %s:%s " %(self._retries, self.device_ip, self.device_port))
                return self.request(message)
            else:
                sys.exit("Socket Error! Please Check your IP and ID from the AC and that your AC is connected to your Router")
        finally:
            sock.close()
        _LOGGER.debug("Received from {}:{} {}".format(
            self.device_ip, self.device_port, message.hex()))
        return response

    def encode(self, data: bytearray):
        normalized = []
        for b in data:
            if b >= 128:
                b = b - 256
            normalized.append(str(b))

        string = ','.join(normalized)
        return bytearray(string.encode('ascii'))

    def decode(self, data: bytearray):
        data = [int(a) for a in data]
        for i in range(len(data)):
            if data[i] < 0:
                data[i] = data[i] + 256
        return bytearray(data)

    def appliance_transparent_send(self, data):
        response = bytearray(self.request(data))
        if len(response) > 0:
            if len(response) == 88:
                reply = self.decode(self.security.aes_decrypt(response[40:72]))
            else:
                reply = self.decode(self.security.aes_decrypt(response[40:88]))
            return reply
        else:
            return bytearray(0)
