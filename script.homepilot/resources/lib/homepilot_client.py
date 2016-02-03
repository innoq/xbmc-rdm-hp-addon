#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json
import xbmc

from Models import device as import_device, home_pilot_base_object, group, scene as import_scene, meter

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
        # self._base_url = None

    def set_ip_address(self, homepilot_host):
        xbmc.log("HomepilotClient: set_ip_address: " + repr(homepilot_host), level=xbmc.LOGDEBUG)
        self._base_url = 'http://' + str(homepilot_host) + '/rest2/Index?'

    def __map_response_to_devices(self, response):
        xbmc.log("HomepilotClient: __map_response_to_devices: ", level=xbmc.LOGDEBUG)
        data = json.loads(response.content)
        device_list = data['devices']
        device_objects = map(lambda x: import_device.Device(x), device_list)
        return device_objects

    def __map_response_to_meters(self, response):
        xbmc.log("HomepilotClient: __map_response_to_meters: ", level=xbmc.LOGDEBUG)
        data = json.loads(response.content)
        device_list = data['meters']
        device_objects = map(lambda x: home_pilot_base_object.HomePilotBaseObject(x), device_list)
        return device_objects

    def __map_response_to_groups(self, response):
        xbmc.log("HomepilotClient: __map_response_to_groups: ", level=xbmc.LOGDEBUG)
        data = json.loads(response.content)
        group_list = data['groups']
        device_objects = map(lambda x: group.Group(x), group_list)
        return device_objects

    def __map_response_to_scenes(self, scene_list):
        xbmc.log("HomepilotClient: __map_response_to_scenes: ", level=xbmc.LOGDEBUG)
        scene_objects = map(lambda x: import_scene.Scene(x), scene_list)
        return scene_objects

    def get_devices(self):
        """
        request a list of all devices from the homepilot
        """
        xbmc.log("HomepilotClient: get_devices: ", level=xbmc.LOGDEBUG)
        response = requests.get(self._base_url + 'do=/devices', timeout=TIMEOUT)
        return self.__map_response_to_devices(response)

    def get_meters(self):
        """
        request a list of all meters from the homepilot
        """
        xbmc.log("HomepilotClient: get_meters: ", level=xbmc.LOGDEBUG)
        response = requests.get(self._base_url + 'do=/meters', timeout=TIMEOUT)
        return self.__map_response_to_meters(response)

    def get_scenes(self):
        xbmc.log("HomepilotClient: get_scenes: ", level=xbmc.LOGDEBUG)
        response = requests.get(self._base_url + 'do=/scenes', timeout=TIMEOUT)
        data = json.loads(response.content)
        return self.__map_response_to_scenes(data[u'scenes'])

    def get_manual_scenes(self):
        xbmc.log("HomepilotClient: get_manual_scenes: ", level=xbmc.LOGDEBUG)
        response = requests.get(self._base_url + 'do=/scenes', timeout=TIMEOUT)
        data = json.loads(response.content)
        scene_list = [i for i in data[u'scenes'] if i[u'isExecutable'] == 1]
        return self.__map_response_to_scenes(scene_list)

    def get_non_manual_scenes(self):
        xbmc.log("HomepilotClient: get_non_manual_scenes: ", level=xbmc.LOGDEBUG)
        response = requests.get(self._base_url + 'do=/scenes', timeout=TIMEOUT)
        data = json.loads(response.content)
        scene_list = [i for i in data[u'scenes'] if i[u'isExecutable'] == 0]
        return self.__map_response_to_scenes(scene_list)

    def get_scene_by_id(self, scene_id):
        xbmc.log("HomepilotClient: get_scene_by_id: ", level=xbmc.LOGDEBUG)
        response = requests.get(self._base_url + 'do=/scenes/' + str(scene_id), timeout=TIMEOUT)
        data = json.loads(response.content)
        scene = data['scene']
        return import_scene.Scene(scene)

    def favorize_scene(self, scene_id):
        xbmc.log("HomepilotClient: favorize_scene: ", level=xbmc.LOGDEBUG)
        xbmc.log("---home_client.py-- favorisiere Szene " + str(scene_id), level=xbmc.LOGNOTICE)
        url = self._base_url + 'do=/scenes/' + str(scene_id) + '?do=setFavored'
        return self._call_url(url)

    def unfavorize_scene(self, scene_id):
        xbmc.log("HomepilotClient: unfavorize_scene: ", level=xbmc.LOGDEBUG)
        xbmc.log("---home_client.py-- unfavorisiere Szene " + str(scene_id), level=xbmc.LOGNOTICE)
        url = self._base_url + 'do=/scenes/' + str(scene_id) + '?do=setUnfavored'
        return self._call_url(url)

    def get_favorite_scenes(self):
        xbmc.log("HomepilotClient: get_favorite_scenes: ", level=xbmc.LOGDEBUG)
        response = requests.get(self._base_url + 'do=/scenes/favorites/', timeout=TIMEOUT)
        data = json.loads(response.content)
        return self.__map_response_to_scenes(data[u'scenes'])

    def execute_scene(self, scene_id):
        xbmc.log("HomepilotClient: execute_scene: ", level=xbmc.LOGDEBUG)
        url = self._base_url + 'do=/scenes/' + str(scene_id) + '?do=use'
        return self._call_url(url)

    def set_scene_active(self, scene_id):
        xbmc.log("HomepilotClient: set_scene_active: ", level=xbmc.LOGDEBUG)
        url = self._base_url + 'do=/scenes/' + str(scene_id) + '?do=setActive&state=1'
        return self._call_url(url)

    def set_scene_inactive(self, scene_id):
        xbmc.log("HomepilotClient: set_scene_inactive: ", level=xbmc.LOGDEBUG)
        url = self._base_url + 'do=/scenes/' + str(scene_id) + '?do=setActive&state=0'
        return self._call_url(url)

    def unfavorize_device(self, device_id):
        xbmc.log("HomepilotClient: unfavorize_device: ", level=xbmc.LOGDEBUG)
        url = self._base_url + 'do=/devices/' + str(device_id) + '?do=setUnfavored'
        return self._call_url(url)

    def get_devices_by_device_group(self, group_id):
        """
        request a list of all devices for a specific devicegroup
        :param group_id:
        """
        xbmc.log("HomepilotClient: get_devices_by_device_group: ", level=xbmc.LOGDEBUG)
        response = requests.get(self._base_url + 'do=/devices/devicegroup/' + str(group_id), timeout=TIMEOUT)
        return self.__map_response_to_devices(response)

    def get_devices_by_group(self, group_id):
        """
        request a list of all devices for a specific devicegroup
        :param group_id:
        """
        xbmc.log("HomepilotClient: get_devices_by_group: ", level=xbmc.LOGDEBUG)
        response = requests.get(self._base_url + 'do=/groups/' + str(group_id), timeout=TIMEOUT)
        return self.__map_response_to_devices(response)

    def get_favorite_devices(self):
        """
        request favorite devices
        """
        xbmc.log("HomepilotClient: get_favorite_devices: ", level=xbmc.LOGDEBUG)
        response = requests.get(self._base_url + 'do=/devices/favorites/', timeout=TIMEOUT)
        return self.__map_response_to_devices(response)

    def get_groups(self):
        xbmc.log("HomepilotClient: get_groups: ", level=xbmc.LOGDEBUG)
        response = requests.get(self._base_url + 'do=/groups', timeout=TIMEOUT)
        return self.__map_response_to_groups(response)

    def get_device_by_id(self, device_id):
        """
        request device by id
        :param device_id:
        """
        xbmc.log("HomepilotClient: get_device_by_id: ", level=xbmc.LOGDEBUG)
        response = requests.get(self._base_url + 'do=/devices/' + str(device_id), timeout=SHORT_TIMEOUT)
        data = json.loads(response.content)
        device = data['device']
        return import_device.Device(device)

    def get_meter_by_id(self, device_id):
        """
        request device by id
        :param device_id:
        """
        xbmc.log("HomepilotClient: get_meter_by_id: ", level=xbmc.LOGDEBUG)
        response = requests.get(self._base_url + 'do=/meters/' + str(device_id), timeout=SHORT_TIMEOUT)
        data = json.loads(response.content)
        device = data['meter']
        data = data['data']
        return meter.Meter(device, data)

    def switch_on(self, device_id):
        """
        sends command 10 to a given device

        Arguments:
        
        device_id -- the id of the device that should be switched on
        :param device_id:
        """
        xbmc.log("HomepilotClient: switch_on: ", level=xbmc.LOGDEBUG)
        url = self._base_url + 'do=/devices/' + str(device_id) + '?do=use&cmd=10'
        return self._call_url(url)

    def set_device_automation_on(self, device_id):
        xbmc.log("HomepilotClient: set_device_automation_on: ", level=xbmc.LOGDEBUG)
        url = self._base_url + 'do=/devices/' + str(device_id) + '?do=setAutomation&state=1'
        return self._call_url(url)

    def set_device_automation_off(self, device_id):
        xbmc.log("HomepilotClient: set_device_automation_off: ", level=xbmc.LOGDEBUG)
        url = self._base_url + 'do=/devices/' + str(device_id) + '?do=setAutomation&state=0'
        return self._call_url(url)

    def switch_off(self, device_id):
        xbmc.log("HomepilotClient: switch_off: ", level=xbmc.LOGDEBUG)
        url = self._base_url + 'do=/devices/' + str(device_id) + '?do=use&cmd=11'
        return self._call_url(url)

    def move_to_position(self, device_id, position):
        """
        sends command 9 and a position to a given device

        Arguments:

        device_id -- the id of the device that should be moved

        position -- the position to which the device should be moved
        :param position:
        :param device_id:
        """
        xbmc.log("HomepilotClient: move_to_position: ", level=xbmc.LOGDEBUG)
        assert 0 <= position <= 100
        url = self._base_url + 'do=/devices/' + str(device_id) + '?do=use&cmd=9&pos=' + str(int(position))
        return self._call_url(url)

    def move_to_degree(self, device_id, position):
        xbmc.log("HomepilotClient: move_to_degree: ", level=xbmc.LOGDEBUG)
        assert 30 <= position <= 280
        url = self._base_url + 'do=/devices/' + str(device_id) + '?do=use&cmd=9&pos=' + str(int(position))
        return self._call_url(url)

    def ping(self, device_id):
        """
        sends command 12 to a given device

        Arguments:

        device_id -- the id of the device that should be pinged
        :param device_id:
        """
        xbmc.log("HomepilotClient: ping: device_id: " + str(device_id), level=xbmc.LOGDEBUG)
        url = self._base_url + 'do=/devices/' + str(device_id) + '?do=use&cmd=12'
        return self._call_url(url)

    @property
    def ping(self):
        xbmc.log("HomepilotClient: ping: ", level=xbmc.LOGDEBUG)
        url = self._base_url + 'do=/ping?var=1359030565'
        return self._call_url(url)

    def favorize_device(self, device_id):
        xbmc.log("HomepilotClient: favorize_device: ", level=xbmc.LOGDEBUG)
        url = self._base_url + 'do=/devices/' + str(device_id) + '?do=setFavored'
        return self._call_url(url)

    def move_up(self, device_id):
        xbmc.log("HomepilotClient: move_up: ", level=xbmc.LOGDEBUG)
        url = self._base_url + 'do=/devices/' + str(device_id) + '?do=use&cmd=1'
        return self._call_url(url)

    def move_down(self, device_id):
        xbmc.log("HomepilotClient: move_down: ", level=xbmc.LOGDEBUG)
        url = self._base_url + 'do=/devices/' + str(device_id) + '?do=use&cmd=3'
        return self._call_url(url)

    def _call_url(self, url):
        xbmc.log("HomepilotClient: _call_url: ", level=xbmc.LOGDEBUG)
        try:
            response = requests.get(url, timeout=TIMEOUT)
            data = json.loads(response.content)
            return data["status"].lower() in ["ok"]
        except Exception, e:
            xbmc.log("Fehler beim Aufruf der Url: " + url + " " + str(e), level=xbmc.LOGWARNING)
            return False
