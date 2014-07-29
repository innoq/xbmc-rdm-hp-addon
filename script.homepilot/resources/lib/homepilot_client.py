#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json
import xbmc
from models import Device, Meter, Group, HomePilotBaseObject

TIMEOUT = 3
SHORT_TIMEOUT = 2
class HomepilotClient:


    """
    Implementation of a client for the HomePilot REST API
    """

    def __init__(self, homepilot_host):
        """
        constructor of the class

        Arguments:
        
        homepilot_host -- the ip address of the homepilot
        """
        self.set_ip_address(homepilot_host)

    def set_ip_address(self, homepilot_host):
        self._base_url = 'http://' + homepilot_host + '/rest2/Index?'


    def __map_response_to_devices(self, response):
        data = json.loads(response.content)
        device_list = data['devices']
        device_objects = map(lambda x: Device(x), device_list)
        return device_objects

    def __map_response_to_meters(self, response):
        data = json.loads(response.content)
        device_list = data['meters']
        device_objects = map(lambda x: HomePilotBaseObject(x), device_list)
        return device_objects

    def __map_response_to_groups(self, response):
        data = json.loads(response.content)
        group_list = data['groups']
        device_objects = map(lambda x: Group(x), group_list)
        return device_objects

    def get_devices(self):
        """
        request a list of all devices from the homepilot
        """
        response = requests.get(self._base_url + 'do=/devices', timeout=TIMEOUT)
        return self.__map_response_to_devices(response)

    def get_meters(self):
        """
        request a list of all meters from the homepilot
        """
        response = requests.get(self._base_url + 'do=/meters', timeout=TIMEOUT)
        return self.__map_response_to_meters(response)


    def get_devices_by_device_group(self, group_id):
        """
        request a list of all devices for a specific devicegroup
        """
        response = requests.get(self._base_url + 'do=/devices/devicegroup/' + str(group_id), timeout=TIMEOUT)
        return self.__map_response_to_devices(response)

    def get_favorite_devices(self):
        """
        request favorite devices
        """
        response = requests.get(self._base_url + 'do=/devices/favorites/', timeout=TIMEOUT)
        return self.__map_response_to_devices(response)

    def get_groups(self):
        response = requests.get(self._base_url + 'do=/groups', timeout=TIMEOUT)
        return self.__map_response_to_groups(response)


    def get_device_by_id(self, device_id):
        """
        request device by id
        """
        response = requests.get(self._base_url + 'do=/devices/' + str(device_id), timeout=SHORT_TIMEOUT)
        data = json.loads(response.content)
        device = data['device']
        return Device(device)


    def get_meter_by_id(self, device_id):
        """
        request device by id
        """
        response = requests.get(self._base_url + 'do=/meters/' + str(device_id), timeout=SHORT_TIMEOUT)
        data = json.loads(response.content)
        device = data['meter']
        data = data['data']
        return Meter(device, data)

    def switch_on(self, device_id):
        """
        sends command 10 to a given device

        Arguments:
        
        device_id -- the id of the device that should be switched on
        """
        url = self._base_url + 'do=/devices/' + str(device_id) + '?do=use&cmd=10'
        try:
            response = requests.get(url, timeout=TIMEOUT)
            data = json.loads(response.content)
            return data["status"].lower() in ["ok"]
        except Exception, e:
            xbmc.log("Fehler beim Aufruf der Url: " + url + " " + str(e), level=xbmc.LOGWARNING)
            return False

    def switch_off(self, device_id):
        """
        sends command 11 to a given device
        
        Arguments:
        
        device_id -- the id of the device that should be switched off
        """
        url = self._base_url + 'do=/devices/' + str(device_id) + '?do=use&cmd=11'
        try:
            response = requests.get(url, timeout=TIMEOUT)
            data = json.loads(response.content)
            return data["status"].lower() in ["ok"]
        except Exception, e:
            xbmc.log("Fehler beim Aufruf der Url: " + url + " " + str(e), level=xbmc.LOGWARNING)
            return False

    def move_to_position(self, device_id, position):
        """
        sends command 9 and a position to a given device

        Arguments:

        device_id -- the id of the device that should be moved

        position -- the position to which the device should be moved
        """
        assert position >= 0 and position <= 100
        url = self._base_url + 'do=/devices/' + str(device_id) + '?do=use&cmd=9&pos=' + str(int(position))
        try:
            response = requests.get(url, timeout=TIMEOUT)
            xbmc.log("request an homepilot - move to position: " + str(url), level=xbmc.LOGNOTICE)
            data = json.loads(response.content)
            return data["status"].lower() in ["ok"]
        except Exception, e:
            xbmc.log("Fehler beim Aufruf der Url: " + url + " " + str(e), level=xbmc.LOGWARNING)
            return False

    def move_to_degree(self, device_id, position):
        assert position >= 30 and position <= 280
        url = self._base_url + 'do=/devices/' + str(device_id) + '?do=use&cmd=9&pos=' + str(int(position))
        try:
            response = requests.get(url, timeout=TIMEOUT)
            xbmc.log("request an homepilot: " + url, level=xbmc.LOGNOTICE)
            data = json.loads(response.content)
            return data["status"].lower() in ["ok"]
        except Exception, e:
            xbmc.log("Fehler beim Aufruf der Url: " + url + " " + str(e), level=xbmc.LOGWARNING)
            return False

    def ping(self, device_id):
        """
        sends command 12 to a given device

        Arguments:

        device_id -- the id of the device that should be pinged
        """
        response = requests.get(self._base_url + 'do=/devices/' + str(device_id) + '?do=use&cmd=12', timeout=TIMEOUT)
        data = json.loads(response.content)
        return data["status"].lower() in ["ok"]

    def ping(self):
        """
        Pings the homepilot
        """
        try:
            response = requests.get(self._base_url + 'do=/ping?var=1359030565', timeout=TIMEOUT)
            data = json.loads(response.content)
            return data["status"].lower() in ["ok"]
        except Exception, e:
            xbmc.log(str(e), level=xbmc.LOGWARNING)
            return False

    def favorize_device(self, device_id):
        """
        favorize a device

        Arguments:

        device_id -- the id of the device that should be favorized
        """
        response = requests.get(self._base_url + 'do=/devices/' + str(device_id) + '?do=setFavored', timeout=TIMEOUT)
        data = json.loads(response.content)
        return data["status"].lower() in ["ok"]

    def unfavorize_device(self, device_id):
        """
        unfavorize a device

        Arguments:

        device_id -- the id of the device that should be favorized
        """
        url = self._base_url + 'do=/devices/' + str(device_id) + '?do=setUnfavored'
        try:
            response = requests.get(url, timeout=TIMEOUT)
            data = json.loads(response.content)
            return data["status"].lower() in ["ok"]
        except Exception, e:
            xbmc.log("Fehler beim Aufruf der Url: " + url + " " + str(e), level=xbmc.LOGWARNING)
            return False

    def move_up(self, device_id):
        url = self._base_url + 'do=/devices/' + str(device_id) + '?do=use&cmd=1'
        try:
            response = requests.get(url, timeout=TIMEOUT)
            data = json.loads(response.content)
            return data["status"].lower() in ["ok"]
        except Exception, e:
            xbmc.log("Fehler beim Aufruf der Url: " + url + " " + str(e), level=xbmc.LOGWARNING)
            return False

    def move_down(self, device_id):
        url = self._base_url + 'do=/devices/' + str(device_id) + '?do=use&cmd=3'
        try:
            response = requests.get(url, timeout=TIMEOUT)
            data = json.loads(response.content)
            return data["status"].lower() in ["ok"]
        except Exception, e:
            xbmc.log("Fehler beim Aufruf der Url: " + url + " " + str(e), level=xbmc.LOGWARNING)
            return False
