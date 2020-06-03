import logging
import requests
import datetime
import json
import socket
import sys
import time

from msmart.security import security

# The Midea cloud client is by far the more obscure part of this library, and without some serious reverse engineering
# this would not have been possible. Thanks Yitsushi for the ruby implementation. This is an adaptation to Python 3

VERSION = '0.1.15'

_LOGGER = logging.getLogger(__name__)

class lan:
    def __init__(self, device_ip, device_id):
        # Get this from any of the Midea based apps, you can find one on Yitsushi's github page
        self.device_ip = device_ip
        self.device_id = device_id
        self.device_port = 6444
        self.security = security()
        self._retries = 0

    def request(self, message):
        # Create a TCP/IP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        # Connect the Device
        device_address = (self.device_ip, self.device_port)
        

        try:
            # Send data
            sock.connect(device_address)
            _LOGGER.debug("Sending to %s:%s %s." %(self.device_ip, self.device_port, message.hex()))
            sock.sendall(message)
            # Received data
            response = sock.recv(512)
        #except socket.timeout:
        #    _LOGGER.info("Connect the Device %s:%s TimeOut for 10s. don't care about a small amount of this. if many maybe not support." %(self.device_ip, self.device_port))
        #    return bytearray()
        except socket.error or socket.timeout:
            self._retries += 1
            import sys
            print(str(sys.exc_info()))
            _LOGGER.error(str(sys.exc_info()))
            if(self._retries < 10):
                _LOGGER.info("wait 10 seconds, and retry")
                time.sleep(10) #give it some time
                _LOGGER.info("retry %s @ %s:%s " %(self._retries, self.device_ip, self.device_port))
                return self.request(message)
            else:
                exit("Socket Error! Please Check your IP and ID from the AC and that your AC is connected to your Router")
        finally:
            sock.close()
        _LOGGER.debug("Received from %s:%s %s." %(self.device_ip, self.device_port, message.hex()))
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
        encoded = self.encode(data)
        response = bytearray(self.request(data))
        if len(response) > 0:
            reply = self.decode(self.security.aes_decrypt(response[40:88]))
            return reply
        else:
            return bytearray()

