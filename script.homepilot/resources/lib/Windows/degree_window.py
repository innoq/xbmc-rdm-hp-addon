#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

import xbmc
import xbmcgui
from .. import statics
from .. import homepilot_utils
import device_window
import slider_updater
import base_window


class DegreeWindow(device_window.DeviceWindow):
    def __init__(self, *args, **kwargs):
        super(DegreeWindow, self).__init__(*args, **kwargs)
        self.client = kwargs[statics.CLIENT]
        self.device = kwargs[statics.DEVICE]
        self.parent_window = kwargs[statics.PARENT]
        self.use_local_favorites = kwargs[statics.LOCAL_FAVS]
        self.updater = slider_updater.SliderUpdater(self.client, self.device, statics.DEGREE_TYPE)
        self.updater.start()
        self.errorcontrol = None
        self.has_error = False
        self.controls = None

    def onInit(self):
        xbmc.log("DegreeWindow: onInit: ", level=xbmc.LOGDEBUG)
        base_device_controls = self.get_base_device_controls(self.device)
        degree_controls = self.__get_degree_controls()
        self.controls = base_device_controls
        self.controls.update(degree_controls)
        button_group = self.getControl(114)
        button_group.setPosition(330, 200)
        self.addControls(
            [self.controls[statics.SLIDER],
             self.controls[statics.STATUS],
             self.controls[statics.TITLE],
             self.controls[statics.ICON]])
        slider = self.controls[statics.SLIDER]
        slider_position = self.__get_slider_percent_from_position(self.device)
        slider.setPercent(slider_position)
        self.__set_focus_and_navigation_handling()
        self.visualize_automations(self.device)

    def __get_degree_controls(self):
        xbmc.log("DegreeWindow: __get_degree_controls: ", level=xbmc.LOGDEBUG)
        controls = {}
        # x = self.x
        # y = self.y
        status = self.device.get_display_value()
        status_control = xbmcgui.ControlLabel(self.x + 180, self.y + 60, 600, 75, status, font="font16",
                                              textColor="white")
        controls[statics.STATUS] = status_control
        controls[statics.SLIDER] = self.get_slider()
        controls[statics.DOWN] = self.getControl(112)
        controls[statics.UP] = self.getControl(113)
        return controls

    def __get_slider_percent_from_position(self, device):
        xbmc.log("DegreeWindow: __get_slider_percent_from_position: ", level=xbmc.LOGDEBUG)
        position = device.get_position()
        return (float(position) / 10 - 3) * 4

    def __set_focus_and_navigation_handling(self):
        xbmc.log("DegreeWindow: __set_focus_and_navigation_handling: ", level=xbmc.LOGDEBUG)
        statusSlider = self.controls[statics.SLIDER]
        downButton = self.controls[statics.DOWN]
        upButton = self.controls[statics.UP]
        self.setFocus(statusSlider)
        statusSlider.controlDown(downButton)
        downButton.controlDown(upButton)
        downButton.controlRight(upButton)
        downButton.controlUp(statusSlider)
        downButton.controlLeft(statusSlider)
        upButton.controlUp(downButton)
        upButton.controlLeft(downButton)
        self.set_navigation_handling_for_automatik_and_favorit(upButton)

    def update(self):
        xbmc.log("DegreeWindow: update: ", level=xbmc.LOGDEBUG)
        if self.getFocusId() == 0:
            self.setFocus(self.controls[statics.SLIDER])
        try:
            if self.updater.get_status() != "UPDATE":
                new_device = self.client.get_device_by_id(self.device.get_device_id())
                if new_device.get_sync() != self.device.get_sync():
                    self.__update_position(new_device)
                    self.__update_name(new_device)
                    self.device = new_device
            else:
                new_device = self.client.get_device_by_id(self.device.get_device_id())
                if new_device.get_sync() != self.device.get_sync():
                    self.__update_name(new_device)
                    self.__update_icon(new_device)
            if self.has_error and self.errorcontrol is not None:
                self.removeControl(self.errorcontrol)
                self.errorcontrol = None
            self.has_error = False
        except Exception, e:
            xbmc.log(str(e), level=xbmc.LOGERROR)
            self.has_error = True

        if self.has_error and self.errorcontrol is None:
            self.add_error_control()

    def __update_icon(self, new_device):
        xbmc.log("DegreeWindow: __update_icon: ", level=xbmc.LOGDEBUG)
        icon = self.controls[statics.ICON]
        image = new_device.get_icon()
        icon_img = os.path.join(base_window.images, image)
        icon.setImage(icon_img)

    def __update_position(self, new_device):
        xbmc.log("DegreeWindow: __update_position: ", level=xbmc.LOGDEBUG)
        if new_device.get_position() != self.device.get_position():
            statusSlider = self.controls[statics.SLIDER]
            new_position = self.__get_slider_percent_from_position(new_device)
            statusSlider.setPercent(new_position)
            self.device = new_device
            statusLabel = self.controls[statics.STATUS]
            statusLabel.setLabel(new_device.get_display_value())
            self.__update_icon(new_device)

    def __update_name(self, new_device):
        xbmc.log("DegreeWindow: __update_name: ", level=xbmc.LOGDEBUG)
        if new_device.get_name() != self.device.get_name():
            title_label = self.controls[statics.TITLE]
            title_label.setLabel(new_device.get_name())

    def onClick(self, controlId):
        xbmc.log("DegreeWindow: onClick: ", level=xbmc.LOGDEBUG)
        xbmc.log("window click " + str(controlId), level=xbmc.LOGNOTICE)
        statusSlider = self.controls[statics.SLIDER]
        downButton = self.controls[statics.DOWN]
        upButton = self.controls[statics.UP]
        autoButton = self.controls[statics.AUTO]
        favoriten_radio_control = self.controls["favoriten"]
        current_device_position = self.device.get_position()
        current_device_position_in_percent = self.__get_slider_percent_from_position(self.device)
        current_slider_position = statusSlider.getPercent()
        if controlId == downButton.getId():
            if current_slider_position >= 5:
                self.client.move_to_degree(self.device.get_device_id(), current_device_position - 5)
        elif controlId == upButton.getId():
            if current_slider_position <= 95:
                self.client.move_to_degree(self.device.get_device_id(), current_device_position + 5)
        elif controlId == statusSlider.getId():
            if current_slider_position != current_device_position_in_percent:
                statusLabel = self.controls[statics.STATUS]
                device_group = self.device.get_devicegroup()
                diff = current_slider_position - current_device_position_in_percent
                # thermostats can only be shifted in 0.5 degree steps over a range from 3°-28°
                # this results in 50 possible value. As the slider has 100 possible values
                # this requires some mappings
                if current_slider_position < 3:
                    current_slider_position = 3
                if diff == 1:
                    new_position = (float(current_slider_position + 1) * 5 + 60) / 2
                    if new_position % 5 == 0:
                        self.updater.update_slider(int(new_position))
                elif diff == -1:
                    new_position = (float(current_slider_position - 1) * 5 + 60) / 2
                    if new_position % 5 == 0:
                        self.updater.update_slider(int(new_position))
                else:
                    new_position = (float(current_slider_position) * 5 + 60) / 2
                    if new_position % 5 == 0:
                        self.updater.update_slider(int(new_position))

                if new_position % 5 == 0:
                    display_value = homepilot_utils.get_display_value(int(new_position), device_group)
                    statusLabel.setLabel(display_value)
        if controlId == autoButton.getId():
            self.handle_automation(self.device.get_device_id(), autoButton.isSelected(), self.device.is_automated())

        if controlId == favoriten_radio_control.getId():
            self.handle_favorit(self.device.get_device_id(), favoriten_radio_control.isSelected(),
                                self.device.is_favored(), self.use_local_favorites)

    def onAction(self, action):
        xbmc.log("DegreeWindow: onAction: ", level=xbmc.LOGDEBUG)
        if action == 92 or action == 10:
            self.updater.set_is_running = False
        base_window.BaseWindow.onAction(self, action)

    def is_closed(self):
        return base_window.BaseWindow.is_closed()