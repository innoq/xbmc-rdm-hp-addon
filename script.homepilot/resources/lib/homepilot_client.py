#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json
import xbmc
from models import Device, Meter, Group, HomePilotBaseObject


class HomepilotClient:
    """
    Implementation of a client for the HomePilot REST API
    
    TODO
    - StatusCode prüfen
    - Rückgabewert OK prüfen
    - Verhalten bei leerer DeviceId
    - Verhalten bei ungültiger url
    - url prüfen
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
        response = requests.get(self._base_url + 'do=/devices', timeout=5)
        return self.__map_response_to_devices(response)

    def get_meters(self):
        """
        request a list of all meters from the homepilot
        """
        response = requests.get(self._base_url + 'do=/meters', timeout=5)
        return self.__map_response_to_meters(response)


    def get_devices_by_device_group(self, group_id):
        """
        request a list of all devices for a specific devicegroup
        """
        response = requests.get(self._base_url + 'do=/devices/devicegroup/' + str(group_id), timeout=5)
        return self.__map_response_to_devices(response)

    def get_favorite_devices(self):
        """
        request favorite devices
        """
        response = requests.get(self._base_url + 'do=/devices/favorites/', timeout=5)
        return self.__map_response_to_devices(response)

    def get_groups(self):
        response = requests.get(self._base_url + 'do=/groups', timeout=5)
        return self.__map_response_to_groups(response)


    def get_device_by_id(self, device_id):
        """
        request device by id
        """
        response = requests.get(self._base_url + 'do=/devices/' + str(device_id), timeout=5)
        data = json.loads(response.content)
        device = data['device']
        return Device(device)


    def get_meter_by_id(self, device_id):
        """
        request device by id
        """
        response = requests.get(self._base_url + 'do=/meters/' + str(device_id), timeout=5)
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
        response = requests.get(self._base_url + 'do=/devices/' + str(device_id) + '?do=use&cmd=10', timeout=5)
        data = json.loads(response.content)
        return data["status"].lower() in ["ok"]

    def switch_off(self, device_id):
        """
        sends command 11 to a given device
        
        Arguments:
        
        device_id -- the id of the device that should be switched off
        """
        response = requests.get(self._base_url + 'do=/devices/' + str(device_id) + '?do=use&cmd=11', timeout=5)
        data = json.loads(response.content)
        return data["status"].lower() in ["ok"]

    def move_to_position(self, device_id, position):
        """
        sends command 9 and a position to a given device

        Arguments:

        device_id -- the id of the device that should be moved
        
        position -- the position to which the device should be moved
        """
        assert position >= 0 and position <= 100
        response = requests.get(
            self._base_url + 'do=/devices/' + str(device_id) + '?do=use&cmd=9&pos=' + str(int(position)),
            timeout=5)
        xbmc.log("request an homepilot: " + str(
            self._base_url + 'do=/devices/' + str(device_id) + '?do=use&cmd=9&pos=' + str(int(position))),
                 level=xbmc.LOGNOTICE)
        data = json.loads(response.content)
        return data["status"].lower() in ["ok"]


    def move_to_degree(self, device_id, position):
        assert position >= 30 and position <= 280
        response = requests.get(
            self._base_url + 'do=/devices/' + str(device_id) + '?do=use&cmd=9&pos=' + str(int(position)),
            timeout=5)
        xbmc.log("request an homepilot: " + str(
            self._base_url + 'do=/devices/' + str(device_id) + '?do=use&cmd=9&pos=' + str(int(position))),
                 level=xbmc.LOGNOTICE)
        data = json.loads(response.content)
        return data["status"].lower() in ["ok"]

    def ping(self, device_id):
        """
        sends command 12 to a given device

        Arguments:

        device_id -- the id of the device that should be pinged
        """
        response = requests.get(self._base_url + 'do=/devices/' + str(device_id) + '?do=use&cmd=12', timeout=5)
        data = json.loads(response.content)
        return data["status"].lower() in ["ok"]

    def ping(self):
        """
        Pings the homepilot
        """
        try:
            response = requests.get(self._base_url + 'do=/ping?var=1359030565', timeout=5)
            data = json.loads(response.content)
            return data["status"].lower() in ["ok"]
        except:
            return False


    def favorize_device(self, device_id):
        """
        favorize a device

        Arguments:

        device_id -- the id of the device that should be favorized
        """
        response = requests.get(self._base_url + 'do=/devices/' + str(device_id) + '?do=setFavored', timeout=5)
        data = json.loads(response.content)
        return data["status"].lower() in ["ok"]

    def unfavorize_device(self, device_id):
        """
        unfavorize a device

        Arguments:

        device_id -- the id of the device that should be favorized
        """
        response = requests.get(self._base_url + 'do=/devices/' + str(device_id) + '?do=setUnfavored', timeout=5)
        data = json.loads(response.content)
        return data["status"].lower() in ["ok"]

