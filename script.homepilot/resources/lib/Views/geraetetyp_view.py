#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import xbmcaddon
import xbmcgui
import xbmc
from .. import homepilot_utils
from .. import statics
import base_view

__addon__ = xbmcaddon.Addon(id='script.homepilot')
__addon_path__ = __addon__.getAddonInfo('path').decode("utf-8")
_images_device = os.path.join(__addon_path__, 'resources', 'skins', 'Default', 'media', 'devices')
_images = os.path.join(__addon_path__, 'resources', 'skins', 'Default', 'media')


class GeraetetypView(base_view.BaseView):
    def __init__(self, home_pilot_client):
        base_view.BaseView.__init__(self)
        self.client = home_pilot_client
        self.geraetetypen_list = None
        self.rolladen_item = None
        self.schalter_item = None
        self.dimmer_item = None
        self.thermostat_item = None
        self.tore_item = None
        self.alle_item = None
        self.gruppen_control = None
        self.errorcontrol = None
        self.geraetelabel_control = None
        self.gruppen_group_control = None

    def get_id(self):
        return statics.geraetetyp_view_id

    def remove_everything(self, window):
        xbmc.log("GeraetetypView: remove_everything: window: " + str(window), level=xbmc.LOGDEBUG)
        window.removeControls([self.geraetelabel_control, self.gruppen_control])
        self.geraetetypen_list.setVisible(False)
        self.gruppen_group_control.setVisible(False)
        if self.errorcontrol is not None:
            window.removeControl(self.errorcontrol)

    def visualize(self, window, addon):
        xbmc.log("GeraetetypView: visualize: window: " + str(window), level=xbmc.LOGDEBUG)
        self.geraetelabel_control = homepilot_utils.get_title_control(32009, addon)

        self.geraetetypen_list = window.getControl(257)
        self.geraetetypen_list.reset()

        self.__build_device_groups(self.__get_device_groups(), addon)

        self.alle_item = xbmcgui.ListItem(label=addon.getLocalizedString(statics.ALLE))
        self.alle_item.setIconImage(base_view.logo_img)
        self.alle_item.setProperty(statics.TYPE, str(statics.ALLE))
        self.geraetetypen_list.addItem(self.alle_item)

        self.geraetetypen_list.setVisible(True)

        label = addon.getLocalizedString(32015)
        self.gruppen_control = xbmcgui.ControlLabel(400, 380, 600, 75, label, font="font16")
        window.addControls([self.geraetelabel_control, self.gruppen_control])

        gruppen_list = window.getControl(4)
        gruppen_list.reset()
        self.gruppen_group_control = window.getControl(251)
        try:
            groups = self.client.get_groups()
            if len(groups) > 0:
                for group in groups:
                    xbmc.log("GeraetetypView: visualize: group: " + repr(group.get_name()), level=xbmc.LOGDEBUG)
                    group_item = xbmcgui.ListItem(label=group.get_name())
                    group_item.setProperty("gid", str(group.get_group_id()))
                    gruppen_list.addItem(group_item)

                self.gruppen_group_control.setPosition(350, 420)
                self.gruppen_group_control.setVisible(True)
                self.errorcontrol = None
            else:
                errorlabel = addon.getLocalizedString(32380)
                self.errorcontrol = xbmcgui.ControlLabel(450, 450, 600, 75, errorlabel)
                window.addControl(self.errorcontrol)
        except Exception, e:
            xbmc.log("GeraetetypView: visualize: " + str(e), level=xbmc.LOGERROR)
            errorlabel = self.get_communication_error_label()
            self.errorcontrol = xbmcgui.ControlLabel(450, 450, 600, 75, errorlabel)
            window.addControl(self.errorcontrol)

    def __get_device_groups(self):
        xbmc.log("GeraetetypView: __get_device_groups:", level=xbmc.LOGDEBUG)
        devices = self.client.get_devices()
        device_groups = []
        for device in devices:
            device_groups.append(device.get_devicegroup())
        return set(device_groups)

    def __build_device_groups(self, device_groups, addon):
        if 2 in device_groups:
            self.rolladen_item = xbmcgui.ListItem(label=addon.getLocalizedString(statics.ROLLADEN))
            self.rolladen_item.setIconImage(base_view.rollo_img)
            self.rolladen_item.setProperty(statics.TYPE, str(statics.ROLLADEN))
            self.geraetetypen_list.addItem(self.rolladen_item)

        if 1 in device_groups:
            self.schalter_item = xbmcgui.ListItem(label=addon.getLocalizedString(statics.SCHALTER))
            self.schalter_item.setIconImage(base_view.schalter_img)
            self.schalter_item.setProperty(statics.TYPE, str(statics.SCHALTER))
            self.geraetetypen_list.addItem(self.schalter_item)

        if 4 in device_groups:
            self.dimmer_item = xbmcgui.ListItem(label=addon.getLocalizedString(statics.DIMMER))
            self.dimmer_item.setIconImage(base_view.dimmer_img)
            self.dimmer_item.setProperty(statics.TYPE, str(statics.DIMMER))
            self.geraetetypen_list.addItem(self.dimmer_item)

        if 5 in device_groups:
            self.thermostat_item = xbmcgui.ListItem(label=addon.getLocalizedString(statics.THERMOSTATE))
            self.thermostat_item.setIconImage(base_view.thermostat_img)
            self.thermostat_item.setProperty(statics.TYPE, str(statics.THERMOSTATE))
            self.geraetetypen_list.addItem(self.thermostat_item)

        if 8 in device_groups:
            self.tore_item = xbmcgui.ListItem(label=addon.getLocalizedString(statics.TORE))
            self.tore_item.setIconImage(base_view.tore_img)
            self.tore_item.setProperty(statics.TYPE, str(statics.TORE))
            self.geraetetypen_list.addItem(self.tore_item)

    def handle_click(self, position):
        xbmc.log("GeraetetypView: visualize: handle_click: " + str(position) +
                 "\nposition.getProperty(statics.TYPE):" + repr(position.getProperty(statics.TYPE)), level=xbmc.LOGDEBUG)
        if position.getProperty(statics.TYPE) == str(statics.ALLE):
            return statics.ALLE
        elif position.getProperty(statics.TYPE) == str(statics.ROLLADEN):
            return statics.ROLLADEN
        elif position.getProperty(statics.TYPE) == str(statics.SCHALTER):
            return statics.SCHALTER
        elif position.getProperty(statics.TYPE) == str(statics.DIMMER):
            return statics.DIMMER
        elif position.getProperty(statics.TYPE) == str(statics.THERMOSTATE):
            return statics.THERMOSTATE
        elif position.getProperty(statics.TYPE) == str(statics.TORE):
            return statics.TORE
        pass
