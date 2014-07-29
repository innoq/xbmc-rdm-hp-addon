#!/usr/bin/env python
# -*- coding: utf-8 -*-

import homepilot_utils

icons = {}
icons["iconset1"] = "aquarium_72_"
icons["iconset22"] = "bargraph_horizontal_72_"
icons["iconset2"] = "bargraph_vertikal_72_"
icons["iconset23"] = "bewegungsmelder_72_"
icons["iconset4"] = "deckenlampe_72_"
icons["iconset5"] = "ein_aus_schalter1_72_"
icons["iconset24"] = "fenster_72_"
icons["iconset18"] = "gartensprenkler_72_"
icons["iconset21"] = "birne1_72_"
icons["iconset6"] = "jalousie_72_"
icons["iconset17"] = "kaffeemaschine_72_"
icons["iconset32"] = "lichterkette_72"
icons["iconset7"] = "markise_72_"
icons["iconset16"] = "pumpe_72_"
icons["iconset26"] = "rauchmelder_72_"
icons["iconset8"] = "rollladen1_72_"
icons["iconset15"] = "rollladen2_72_"
icons["iconset9"] = "schiebetuer_72_"
icons["iconset14"] = "schiebeladen_72_"
icons["iconset27"] = "schliesskontakt_72_"
icons["iconset30"] = "garage_72_"
icons["iconset31"] = "sektionaltor_72_"
icons["iconset25"] = "genericsensor_72_"
#icons["iconset19"]      -> Standard
icons["iconset10"] = "steckdose_72_"
icons["iconset13"] = "stehlampe_72_"
icons["iconset20"] = "sunscreen_72_"
icons["iconset28"] = "thermostat_72_"
icons["iconset11"] = "tischlampe_72_"
icons["iconset12"] = "tuer_72_"
icons["iconset33"] = "weihnachtsbaum_72_"
icons["iconset34"] = "dachfenster_72_"
icons["iconset35"] = "handsender_72_"
icons["iconset36"] = "leinwand_72_"
icons["iconset37"] = "radio_72_"
icons["iconset38"] = "smartphone_72_"
icons["iconset39"] = "ventilator_72_"



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
        return self._icon_set_inverted is not None and self._icon_set_inverted != 0

    def get_icon(self):
        if self._icon_set in icons:
            base_icon = icons[self._icon_set]
            #An-/Aus-Icons
            position = self._position
            if self._deviceGroup == 5:
                position = (float(position)/10 - 3) * 4
            an_aus = set(
                ["iconset1", "iconset23", "iconset5", "iconset24", "iconset18", "iconset17", "iconset16", "iconset26",
                 "iconset27", "iconset25", "iconset10", "iconset12", "iconset32", "iconset33", "iconset34",
                 "iconset37", "iconset38", "iconset39"])
            if self._icon_set in an_aus:
                if self.get_iconset_inverted():
                    return self.__get_icon_switch_inverted(position, base_icon)
                else:
                    return self.__get_icon_switch(position, base_icon)

            # Icons für Werte 0, 25, 50, 75, 100
            else:
                if self.get_iconset_inverted():
                    return self.__get_icon_percent_inverted(position, base_icon)
                else:
                    return self.__get_icon_percent(position, base_icon)
        else:
            return "gruppe_32.png"


    def __get_icon_switch(self, position, base_icon):
        if position < 50:
            return base_icon + "0.png"
        else:
            return base_icon + "1.png"


    def __get_icon_switch_inverted(self, position, base_icon):
        if position < 50:
            return base_icon + "1.png"
        else:
            return base_icon + "0.png"


    def __get_icon_percent(self, position, base_icon):
        if position < 12:
            return base_icon + "0.png"
        elif position < 37:
            return base_icon + "25.png"
        elif position < 62:
            return base_icon + "50.png"
        elif position < 87:
            return base_icon + "75.png"
        else:
            return base_icon + "100.png"


    def __get_icon_percent_inverted(self, position, base_icon):
        if position < 12:
            return base_icon + "100.png"
        elif position < 37:
            return base_icon + "75.png"
        elif position < 62:
            return base_icon + "50.png"
        elif position < 87:
            return base_icon + "25.png"
        else:
            return base_icon + "0.png"

    def get_display_value(self):
        position = self.get_position()
        group = self.get_devicegroup()
        return homepilot_utils.get_display_value(position, group)


class Device(HomePilotBaseObject):
    def __init__(self, device):
        HomePilotBaseObject.__init__(self, device)
        self._available = device["avail"]
        self._hasErrors = device["hasErrors"] != 0
        self._groups = device["groups"]
        self._favoredId = device["favoredId"]

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
