import requests
import datetime
import json
import logging
import time

from threading import Lock

from midea.security import security

# The Midea cloud client is by far the more obscure part of this library, and without some serious reverse engineering
# this would not have been possible. Thanks Yitsushi for the ruby implementation. This is an adaptation to Python 3

VERSION = '0.1.7'
_LOGGER = logging.getLogger(__name__)

class cloud:
    SERVER_URL = "https://mapp.appsmb.com/v1/"
    CLIENT_TYPE = 1                 # Android
    FORMAT = 2                      # JSON
    LANGUAGE = 'en_US'
    APP_ID = 1017
    SRC = 17

    def __init__(self, app_key, email, password):
        # Get this from any of the Midea based apps, you can find one on Yitsushi's github page
        self.app_key = app_key
        self.login_account = email   # Your email address for your Midea account
        self.password = password

        # An obscure log in ID that is seperate to the email address
        self.login_id = None

        # A session dictionary that holds the login information of the current user
        self.session = {}

        # A list of home groups used by the API to seperate "zones"
        self.home_groups = []

        # A list of appliances associated with the account
        self.appliance_list = []

        self._api_lock = Lock()

        self.security = security(self.app_key)
        self._retries = 0

    def api_request(self, endpoint, args):
        """
        Sends an API request to the Midea cloud service and returns the results
        or raises ValueError if there is an error
        """
        self._api_lock.acquire()
        response = {}
        try:
            # Set up the initial data payload with the global variable set
            data = {
                'appId': self.APP_ID,
                'format': self.FORMAT,
                'clientType': self.CLIENT_TYPE,
                'language': self.LANGUAGE,
                'src': self.SRC,
                'stamp': datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            }
            # Add the method parameters for the endpoint
            data.update(args)

            # Add the sessionId if there is a valid session
            if self.session:
                data['sessionId'] = self.session['sessionId']

            url = self.SERVER_URL + endpoint

            data['sign'] = self.security.sign(url, data)

            # POST the endpoint with the payload
            r = requests.post(url=url, data=data)

            response = json.loads(r.text)
        finally:
            self._api_lock.release()

        # Check for errors, raise if there are any
        if response['errorCode'] != '0':
            self.handle_api_error(int(response['errorCode']), response['msg'])
            # If you don't throw, then retry
            #if(__debug__):
            _LOGGER.info("Retrying API call: '{}'".format(endpoint))
            self._retries += 1
            if(self._retries < 3):
                #self.get_login_id()
                #self.login()
                return self.api_request(endpoint, args)
            else:
                _LOGGER.error("RecursionError: '{}' - '{}'".format(response['errorCode'], response['msg']))
                #_LOGGER.info("RecursionError: '{}'".format(endpoint))
                raise RecursionError()

        self._retries = 0
        return response['result']

    def get_login_id(self):
        """
        Get the login ID from the email address
        """

        response = self.api_request("user/login/id/get", {
            'loginAccount': self.login_account
        })
        self.login_id = response['loginId']
        _LOGGER.info("self.get_login_id: Get the login ID from the email address: '{}'".format(self.login_id))
#        _LOGGER.info("self.get_login_id: Get the login ID from the email address")

    def login(self):
        """
        Performs a user login with the credentials supplied to the constructor
        """
        _LOGGER.info("Performs a user login with the credentials supplied to the constructor")
#        if self.login_id == None:
        if not self.login_id:
            self.get_login_id()
            _LOGGER.info("self.login: self.login_id == None - login.self using self.get_login_id")
            #_LOGGER.info("self.login: self.session before if self.session: '{}' - '{}'".format(self.session, self.security.accessToken))
        # if self.session:
            # _LOGGER.info("self.login: Don't try logging in again, someone beat this thread to it")
            # return  # Don't try logging in again, someone beat this thread to it

        # Log in and store the session
        self.session = self.api_request("user/login", {
            'loginAccount': self.login_account,
            'password': self.security.encryptPassword(self.login_id, self.password)
        })
 #       if not self.session:
 #          self.session = self.api_request("user/login", {
 #              'loginAccount': self.login_account,
 #              'password': self.security.encryptPassword(self.login_id, self.password)
 #          })
        #_LOGGER.info("Don't try logging in again, someone beat this thread to it")
        _LOGGER.info("self.login: self.session: '{}' - '{}'".format(self, self.security.accessToken))
        self.security.accessToken = self.session['accessToken']

    def loginfix(self):
        """
        Performs a user forced login with the credentials supplied to the constructor
        """
        _LOGGER.info("FIX Performs a user login with the credentials supplied to the constructor")
        self.get_login_id()
        #_LOGGER.info("FIX self.loginfix: self.login_id == None - login.self using self.get_login_id")
        #_LOGGER.info("FIX self.loginfix: self.session before if self.session : '{}' - '{}'".format(self.session, self.security.accessToken))

        # Log in and store the session
        _LOGGER.info("FIX Log in and store the session")
        self.session = self.api_request("user/login", {
            'loginAccount': self.login_account,
            'password': self.security.encryptPassword(self.login_id, self.password)
        })

        _LOGGER.info("FIX self.loginfix: self.session: '{}' - '{}'".format(self, self.security.accessToken))
        self.security.accessToken = self.session['accessToken']
        time.sleep(10) #Give it some time..

    def list(self, home_group_id=-1):
        """
        Lists all appliances associated with the account
        """

        # If a homeGroupId is not specified, use the default one
        if home_group_id == -1:
            li = self.list_homegroups()
            home_group_id = next(
                x for x in li if x['isDefault'] == '1')['id']

        response = self.api_request('appliance/list/get', {
            'homegroupId': home_group_id
        })

        self.appliance_list = response['list']
        #if(__debug__):
        _LOGGER.info("Device list: {}".format(self.appliance_list))
        return self.appliance_list

    def encode(self, data: bytearray):
        normalized = []
        for b in data:
            if b >= 128:
                b = b - 256
            normalized.append(str(b))

        string = ','.join(normalized)
        return bytearray(string.encode('ascii'))

    def decode(self, data: bytearray):
        data = [int(a) for a in data.decode('ascii').split(',')]
        for i in range(len(data)):
            if data[i] < 0:
                data[i] = data[i] + 256
        return bytearray(data)

    def appliance_transparent_send(self, id, data):
        if not self.session:
            self.login()

        #if(__debug__):
        _LOGGER.debug("Sending to {}: {}".format(id, data.hex()))
        encoded = self.encode(data)
        order = self.security.aes_encrypt(encoded)
        response = self.api_request('appliance/transparent/send', {
            'order': order.hex(),
            'funId': '0000',
            'applianceId': id
        })

        reply = self.decode(self.security.aes_decrypt(
            bytearray.fromhex(response['reply'])))

        #if(__debug__):
        _LOGGER.debug("Recieved from {}: {}".format(id, reply.hex()))
        return reply

    def list_homegroups(self, force_update=False):
        """
        Lists all home groups
        """

        # Get all home groups (I think the API supports multiple zones or something)
        if not self.home_groups or force_update:
            response = self.api_request('homegroup/list/get', {})
            self.home_groups = response['list']

        return self.home_groups

    def handle_api_error(self, error_code, message: str):

        def restart_full():
            #if(__debug__):
            _LOGGER.info("Restarting full: '{}' - '{}'".format(error_code, message))
            #self.session = None
            if not self.session:
                self.get_login_id()
                self.loginfix()

        def restart_fullfix():
            #if(__debug__):
            _LOGGER.info("Restarting fullfix: '{}' - '{}'".format(error_code, message))
            #self.session = None
            #self.get_login_id()
            self.loginfix()
            self.list()

        def session_restart():
            #if(__debug__):
            _LOGGER.info("Restarting session: '{}' - '{}'".format(error_code, message))
            #self.session = None
            if not self.session:
                self.login()

        def throw():
            raise ValueError(error_code, message)
            _LOGGER.info("throw: '{}' - '{}'".format(error_code, message))

        def ignore():
            #if(__debug__):
            _LOGGER.info("Error ignored: '{}' - '{}'".format(error_code, message))

        error_handlers = {
            3176: ignore,          # The asyn reply does not exist.
            #3106: session_restart,  # invalidSession.
            3106: restart_fullfix,  # invalidSession.
            3144: restart_full,
            3004: session_restart,  # value is illegal.
            9999: session_restart,  # system error.
        }

        handler = error_handlers.get(error_code, throw)
        handler()
