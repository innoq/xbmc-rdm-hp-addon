#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import xbmcgui
import xbmc
import base_view
from .. import homepilot_utils
from .. import statics

device_types = {statics.SCHALTER: 1, statics.ROLLADEN: 2, statics.SENSOREN: 3, statics.DIMMER: 4,
                statics.THERMOSTATE: 5, statics.TORE: 8}


class ParametrizedGeraeteView(base_view.BaseView):
    def __init__(self, home_pilot_client, device_type, group=None):
        base_view.BaseView.__init__(self)
        self.client = home_pilot_client
        self.total = 0
        self.controldict = {}
        self.type = device_type
        self.list_item_dict = {}
        self.hp_error = False
        self.errorcontrol = None
        self.group = group
        self.title_control = None
        self.gerate_group_control = None

    def get_id(self):
        return str(self.type) + "_view"

    def get_group(self):
        return self.group

    def visualize(self, window, addon, title=None):
        xbmc.log("ParametrizedGeraeteView: visualize: window: " + str(window), level=xbmc.LOGDEBUG)
        if title is None:
            self.title_control = homepilot_utils.get_title_control(self.type, addon)
        else:
            self.title_control = homepilot_utils.get_title_control(title, addon)
        window.addControl(self.title_control)
        if not hasattr(self, "gerate_group_control"):
            self.gerate_group_control = window.getControl(252)
            window.setProperty('GeraeteScrollHeight', '480')
        elif self.gerate_group_control is None:
            xbmc.log(
                "ParametrizedGeraeteView: visualize: gerate_group_control will be None. ", level=xbmc.LOGWARNING)
            self.gerate_group_control = window.getControl(252)
            window.setProperty('GeraeteScrollHeight', '480')
        homepilot_is_reachable = self.client.ping
        if not homepilot_is_reachable:
            self.hp_error = True
            errorlabel = self.get_communication_error_label()
            self.errorcontrol = xbmcgui.ControlLabel(400, 250, 700, 100, errorlabel)
            window.addControl(self.errorcontrol)
        else:
            self.hp_error = False
            self.__visualize_devices(window, addon)

    def __visualize_devices(self, window, addon):
        xbmc.log("ParametrizedGeraeteView: __visualize_devices: window: " + str(window), level=xbmc.LOGDEBUG)
        try:
            devices = self.__get_devices()
            if len(devices) > 0:
                self.geraete_list = window.getControl(5)
                if self.type == statics.SENSOREN:
                    self.geraete_list.controlLeft(self.__get_menu_control(window))
                else:
                    xbmc.log(
                        "ParametrizedGeraeteView: __visualize_devices: set a fake control to prevent xbmc from setting it back to the main menu. ",
                        level=xbmc.LOGDEBUG)
                    control = window.getControl(111)
                    self.geraete_list.controlLeft(control)
                self.geraete_list.reset()
                self.__add_listitems(devices)
                xbmc.log("ParametrizedGeraeteView: __visualize_devices: listItems geladen. ", level=xbmc.LOGDEBUG)
                if self.gerate_group_control is not None:
                    self.gerate_group_control.setPosition(350, 100)
                    self.gerate_group_control.setVisible(True)
                else:
                    xbmc.log("ParametrizedGeraeteView: __visualize_devices: gerate_group_control is None. ",
                             level=xbmc.LOGWARNING)
                if self.type != statics.FAVORITEN and self.type != statics.FAVORITEN_LOKAL and self.type != statics.SENSOREN:
                    window.setFocus(self.geraete_list)
        except Exception as inst:
            self.hp_error = True
            errorlabel = self.get_communication_error_label()
            self.errorcontrol = xbmcgui.ControlLabel(400, 250, 600, 75, errorlabel, font="font13")
            window.addControl(self.errorcontrol)
            xbmc.log("ParametrizedGeraeteView: __visualize_devices: Exception: " + str(inst), level=xbmc.LOGWARNING)

    def __get_menu_control(self, window):
        xbmc.log("ParametrizedGeraeteView: __get_menu_control: window: " + str(window), level=xbmc.LOGDEBUG)
        if self.type == statics.SENSOREN:
            return window.getControl(97)
        else:
            return window.getControl(96)

    def __add_listitems(self, devices):
        xbmc.log("ParametrizedGeraeteView: __add_listitems: devices: " + repr(devices), level=xbmc.LOGDEBUG)
        try:
            for device in devices:
                devicename = device.get_name()
                device_display_value = device.get_display_value()
                if self.type == statics.SENSOREN:
                    item = xbmcgui.ListItem(label=devicename)
                else:
                    item = xbmcgui.ListItem(label=devicename, label2=device_display_value)
                icon_name = device.get_icon()
                item.setIconImage(os.path.join(base_view.images_device, icon_name))
                item.setProperty("description", device.get_description())
                item.setProperty("did", str(device.get_device_id()))
                item.setProperty("sync", str(device.get_sync()))
                self.list_item_dict[device.get_device_id()] = item
                self.geraete_list.addItem(item)
        except Exception, e:
            xbmc.log("ParametrizedGeraeteView: __add_listitems: Exception: " + str(e.args), level=xbmc.LOGWARNING)

    def __get_devices(self):
        xbmc.log("ParametrizedGeraeteView: __get_devices: ", level=xbmc.LOGDEBUG)
        if self.type == statics.ALLE:
            devices = self.client.get_devices()
        elif self.type == statics.SENSOREN:
            devices = self.client.get_meters()
        elif self.type == statics.GRUPPEN:
            devices = self.client.get_devices_by_group(self.group)
        else:
            devices = self.client.get_devices_by_device_group(device_types[self.type])
        return devices

    def remove_everything(self, window):
        xbmc.log("ParametrizedGeraeteView: remove_everything: window: " + str(window), level=xbmc.LOGDEBUG)
        if self.hp_error and self.errorcontrol is not None:
            window.removeControls([self.errorcontrol, self.title_control])
            self.errorcontrol = None
        try:
            window.removeControls([self.title_control])
        except RuntimeError, e:
            xbmc.log("Control does not exist in window: " + str(e), level=xbmc.LOGWARNING)
        if self.gerate_group_control is not None:
            self.gerate_group_control.setVisible(False)

    def update(self, window, addon, menuControl):
        xbmc.log("ParametrizedGeraeteView: update: window: " + str(window) +
                 "\nhp_error: " + repr(self.hp_error), level=xbmc.LOGDEBUG)
        try:
            if self.hp_error:
                self.remove_everything(window)
                self.visualize(window, addon)
            else:
                new_devices = self.__get_devices()
                list_item_ids = self.list_item_dict.keys()
                xbmc.log("ParametrizedGeraeteView: update:\n new_devices: " + repr(new_devices) +
                         "\nlist_item_ids: " + repr(list_item_ids) +
                         "\nlist_item_dict: " + repr(self.list_item_dict), level=xbmc.LOGDEBUG)
                for new_device in new_devices:
                    new_sync_value = str(new_device.get_sync())
                    device_listitem = self.list_item_dict.get(new_device.get_device_id())
                    if device_listitem is not None:
                        list_item_ids.remove(new_device.get_device_id())
                        old_sync_value = device_listitem.getProperty("sync")
                        old_status = device_listitem.getLabel2()
                        new_status = new_device.get_display_value()
                        if new_sync_value != old_sync_value or old_status != new_status:
                            new_icon = new_device.get_icon()
                            if old_status != new_status:
                                device_listitem.setLabel2(new_status)
                                device_listitem.setIconImage(os.path.join(base_view.images_device, new_icon))
                            else:
                                device_listitem.setIconImage(os.path.join(base_view.images_device, new_icon))
                            old_label = device_listitem.getLabel()
                            new_label = new_device.get_name()
                            if old_label != new_label.encode('utf8'):
                                device_listitem.setLabel(new_label)
                            old_label2 = device_listitem.getProperty("description")
                            new_label2 = new_device.get_description()
                            if old_label2 != new_label2.encode('utf8'):
                                device_listitem.setProperty("description", new_label2)
                    else:
                        xbmc.log("ParametrizedGeraeteView: update: device_listitem is None: " + repr(device_listitem), level=xbmc.LOGDEBUG)
                        self.__add_listitems([new_device])
                # remove items from list when devices are no longer present
                # workaround implementation as the ControlList.removeItem didn't work
                if len(list_item_ids) > 0:
                    self.list_item_dict = {}
                    self.geraete_list.reset()
                    self.__add_listitems(new_devices)
            self.hp_error = False
        except Exception, e:
            xbmc.log("Problem beim Updaten des views: " + str(self.type) + "  " + str(e), level=xbmc.LOGERROR)
            self.remove_everything(window)
            self.visualize(window, addon)
            self.hp_error = True

    def _get_list_item_position(self, item):
        xbmc.log("ParametrizedGeraeteView: _get_list_item_position: item: " + str(item), level=xbmc.LOGDEBUG)
        for i in range(0, self.geraete_list.size()):
            if self.geraete_list.getListItem(i) == item:
                return i
        return -1

    def handle_click(self, position):
        pass
