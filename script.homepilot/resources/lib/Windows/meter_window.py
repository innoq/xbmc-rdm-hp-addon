#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xbmc
import xbmcgui
import os
from .. import statics
import base_window


class MeterWindow(base_window.BaseWindow):
    def __init__(self, *args, **kwargs):
        xbmcgui.WindowXMLDialog.__init__(self)
        self.client = kwargs[statics.CLIENT]
        self.did = kwargs[statics.CLIENT]
        self.parent_window = kwargs[statics.PARENT]
        self.meter = None
        self.icon_control = None
        self.data_controls = None

    def onInit(self):
        xbmc.log("MeterWindow: onInit: ", level=xbmc.LOGDEBUG)
        self.__disable_favorite_and_automatik_control()
        self.__resize_window()
        try:
            self.meter = self.client.get_meter_by_id(self.did)
            self.__add__controls()
            self.errorcontrol = None
        except Exception, e:
            xbmc.log(str(e), level=xbmc.LOGWARNING)
            self.add_error_control()

    def __add__controls(self):
        xbmc.log("MeterWindow: __add__controls: ", level=xbmc.LOGDEBUG)
        controls = []
        self.icon_control = self.__get_icon_control()
        controls.append(self.icon_control)
        title = self.meter.get_name()
        self.title_control = xbmcgui.ControlLabel(310, 55, 600, 75, title, font="font16", textColor="white")
        controls.append(self.title_control)
        label = base_window.__addon__.getLocalizedString(32389)
        aktuell_control = xbmcgui.ControlLabel(300, 110, 600, 75, label, font="font12", textColor="white")
        controls.append(aktuell_control)
        self.data_controls = self.__get_data_controls()
        controls.extend(self.data_controls)
        self.addControls(controls)

    def __get_icon_control(self):
        xbmc.log("MeterWindow: __get_icon_control: ", level=xbmc.LOGDEBUG)
        icon = self.meter.get_icon()
        icon_img = os.path.join(base_window.images, icon)
        image_control = xbmcgui.ControlImage(260, 55, 40, 40, icon_img)
        return image_control

    def __get_data_controls(self):
        xbmc.log("MeterWindow: __get_data_controls: ", level=xbmc.LOGDEBUG)
        data = self.meter.get_data()
        y = 150
        data_controls = []
        for data_dict in data:
            for d in data_dict:
                label = d + ": " + data_dict[d]
                data_control = xbmcgui.ControlLabel(300, y, 600, 75, label, font="font12", textColor="white")
                y += 35
                data_controls.append(data_control)
        return data_controls

    def update(self):
        xbmc.log("MeterWindow: update: ", level=xbmc.LOGDEBUG)
        try:
            new_meter = self.client.get_meter_by_id(self.did)
            if new_meter.get_sync() != self.meter.get_sync():
                if new_meter.get_name() != self.meter.get_name():
                    xbmc.log("-- name has changed ", level=xbmc.LOGNOTICE)
                    self.title_control.setLabel(new_meter.get_name())
                if new_meter.get_icon() != self.meter.get_icon():
                    self.removeControl(self.icon_control)
                    self.icon_control = self.__get_icon_control()
                    self.addControl(self.icon_control)
                self.removeControls(self.data_controls)
                self.data_controls = self.__get_data_controls()
                self.addControls(self.data_controls)
                self.meter = new_meter
        except Exception, e:
            xbmc.log(str(e), level=xbmc.LOGWARNING)

    def __disable_favorite_and_automatik_control(self):
        xbmc.log("MeterWindow: __disable_favorite_and_automatik_control: ", level=xbmc.LOGDEBUG)
        automation_control = self.getControl(138)
        automation_control.setVisible(False)
        favorit_control = self.getControl(134)
        favorit_control.setVisible(False)
        automatik_control = self.getControl(130)
        automatik_control.setVisible(False)

    def __resize_window(self):
        xbmc.log("MeterWindow: __resize_window: ", level=xbmc.LOGDEBUG)
        background = self.getControl(1002)
        background.setWidth(600)
        separator = self.getControl(1004)
        if xbmc.getSkinDir() == "skin.confluence":
            separator.setWidth(620)
            close_icon = self.getControl(1003)
            close_icon.setPosition(780, close_icon.getY())
        else:
            separator.setWidth(540)

    def onAction(self, action):
        xbmc.log("MeterWindow: onAction: ", level=xbmc.LOGDEBUG)
        base_window.BaseWindow.onAction(self, action)

    def is_closed(self):
        return base_window.BaseWindow.is_closed()