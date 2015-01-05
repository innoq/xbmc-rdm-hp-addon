#!/usr/bin/env python
# -*- coding: utf-8 -*-

import homepilot_utils
import xbmc


class HomePilotBaseObject:
    """
    class which represents a single device
    """

    def __init__(self, device):
        """
        constructor of the class

        Arguments:

        device -- dictionary with the device attributes
        """
        self.device = device
        self._name = device["name"]
        self._descriprion = device["description"]
        self._did = device["did"]
        self._position = device["position"]
        self._deviceGroup = device["deviceGroup"]
        self._status = device["position"]
        self._sync = device["sync"]
        self._icon_set = device["iconsetKey"]
        self._icon_set_inverted = device.get("iconSetInverted")

    def get_name(self):
        """
        returns the device name
        """
        return self._name

    def get_device_id(self):
        """
        return the device id
        """
        return self._did

    def get_position(self):
        """
        gets the current position of the device on a scale from 0 to 100
        """
        return self._position

    def get_devicegroup(self):
        """
        returns the devicegroup the device belongs to

        Schalter:1,	Sensoren:3, Rollos:2, Thermostate:5, Dimmer:4, Tore:8
        """
        return self._deviceGroup

    def get_status(self):
        """
        returns the current status
        """
        return self._status

    def get_description(self):
        return self._descriprion

    def get_sync(self):
        return self._sync

    def get_iconset_inverted(self):
        return homepilot_utils.get_iconset_inverted(self._icon_set_inverted)

    def get_icon(self):

        return homepilot_utils.get_icon(self._icon_set, self._icon_set_inverted, self._position, self._deviceGroup)

    def get_display_value(self):
        position = self.get_position()
        group = self.get_devicegroup()
        return homepilot_utils.get_display_value(position, group)


class Automation():
    def __init__(self, properties):
        self.properties = properties

    def get_dawn(self):
        return self.properties["dawn"]

    def get_dusk(self):
        return self.properties["dusk"]

    def get_time(self):
        return self.properties["time"]

    def get_wind(self):
        return self.properties["wind"]

    def get_temperature(self):
        return self.properties["temperature"]

    def get_generic(self):
        return self.properties["generic"]

    def get_trigger(self):
        return self.properties["trigger"]

    def get_closing_contact(self):
        return self.properties["closingContact"]

    def get_smoke(self):
        return self.properties["smoke"]

    def get_sun(self):
        return self.properties["sun"]

    def get_manual(self):
        return self.properties["manual"]

    def get_dust(self):
        return self.properties["dust"]

    def get_favored(self):
        return self.properties["favored"]

    def get_smartphone(self):
        return self.properties["smartphone"]

    def get_motion(self):
        return self.properties["motion"]

    def get_temperator(self):
        return self.properties["temperator"]

    def get_warning(self):
        return self.properties["warning"]

    def get_rain(self):
        return self.properties["rain"]


class Device(HomePilotBaseObject):

    def __init__(self, device):
        HomePilotBaseObject.__init__(self, device)
        self._available = device["avail"]
        self._hasErrors = device["hasErrors"] != 0
        self._groups = device["groups"]
        self._favoredId = device["favoredId"]
        self._automated = device["automated"] != 0
        self._properties = device["properties"]

    def has_errors(self):
        """
        returns if the device has errors
        """
        return self._hasErrors

    def is_available(self):
        """
        returns if the device is available
        """
        return self._available

    def get_favoredId (self):
        return self._favoredId

    def get_icon(self):
        icon = HomePilotBaseObject.get_icon(self)
        if self.is_available() == False or self.has_errors():
            icon = "warnung_72.png"
        return icon

    def is_automated(self):
        return self._automated

    def get_automationen(self):
        return Automation(self._properties)

    def is_favored(self):
        return self._favoredId != -1

class Meter(HomePilotBaseObject):

    def __init__(self, device, data):
        """
        constructor of the class

        Arguments:

        meter -- dictionary with the sensor attributes
        """
        HomePilotBaseObject.__init__(self, device)
        self._data = data

    def get_data (self):
        return self._data


class Group:

    def __init__(self, group):
        self.group = group
        self._name = group["name"]
        self._description = group["description"]
        self._gid = group["gid"]

    def get_group_id(self):
        return self._gid

    def get_name(self):
        return self._name

    def get_description(self):
        return self._description


class Action:

    def __init__(self, action):
        self._did = action["did"]
        self._type = action["type"]
        self._name = action["name"]
        self._description = action["description"]
        self._iconset = action ["iconset"]
        self._iconsetInverted = action["iconsetInverted"]
        self._cmdId = action["cmdId"]
        if "param" in action:
            self._param = action["param"]
        else:
            self._param = None

    def get_did(self):
        return self._did

    def get_name(self):
        return self._name

    def get_description(self):
        return self._description

    def get_icon(self):
        if self._cmdId == 666:#Sensor
            return homepilot_utils.get_action_sensor_icon()
        elif self._param is not None:
            return homepilot_utils.get_icon(self._iconset, self._iconsetInverted, self._param, type)
        elif self._cmdId == 10 or self._cmdId == 2:
            return homepilot_utils.get_icon(self._iconset, self._iconsetInverted, 100, type)
        else:
            return homepilot_utils.get_icon(self._iconset, self._iconsetInverted, 0, type)

    def get_cmdId(self):
        return self._cmdId

    def get_device_group(self):
        return self._type

    def get_param(self):
        return self._param


class Scene:

    def __init__(self, scene):
        self._sid           = scene["sid"]
        self._name          = scene["name"]
        self._description   = scene["description"]
        self._is_executable = scene["isExecutable"]
        self._sync          = scene["sync"]
        self._groups        = scene["groups"]
        if 'actions' in scene:
            self._actions   = scene["actions"]
        self._properties    = scene["properties"]
        self._is_active     = scene["isActive"]
        self._favored       = scene["favoredId"]

    def get_id(self):
        return self._sid

    def get_name(self):
        return self._name

    def get_actions(self):
        return map(lambda x: Action(x), self._actions)

    def get_automationen(self):
        return Automation(self._properties)

    def is_executable(self):
        return self._is_executable == 1

    def is_active(self):
        return self._is_active == 1

    def is_favored(self):
        return self._favored > 0

    def get_sync(self):
        return self._sync

    def get_description(self):
        return self._description