#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from .. import statics
from .. import homepilot_utils
import xbmc
import xbmcgui
import device_window
import slider_updater
import base_window


class PercentageWindow(device_window.DeviceWindow):
    def __init__(self, *args, **kwargs):
        xbmc.log("PercentageWindow: __init__: ", level=xbmc.LOGDEBUG)
        super(PercentageWindow, self).__init__(*args, **kwargs)
        self.client = kwargs[statics.CLIENT]
        self.device = kwargs[statics.DEVICE]
        self.parent_window = kwargs[statics.PARENT]
        self.use_local_favorites = kwargs[statics.LOCAL_FAVS]
        self.updater = slider_updater.SliderUpdater(self.client, self.device, statics.PERCENT_TYPE)
        self.updater.start()
        self.has_error = False
        self.controls = {}
        self.errorcontrol = None

    def onInit(self):
        xbmc.log("PercentageWindow: onInit: ", level=xbmc.LOGDEBUG)
        base_device_controls = self.get_base_device_controls(self.device)
        percent_controls = self.__get_percent_controls()
        self.controls = base_device_controls
        self.controls.update(percent_controls)
        if self.device.get_devicegroup() == 2:
            button_group = self.getControl(1141)
        else:
            button_group = self.getControl(114)
        button_group.setPosition(330, 200)
        self.addControls([self.controls[statics.SLIDER],
                          self.controls[statics.STATUS],
                          self.controls[statics.TITLE],
                          self.controls[statics.ICON]])
        slider = self.controls[statics.SLIDER]
        slider.setPercent(self.device.get_position())
        xbmc.log("PercentageWindow: onInit: slider" + repr(slider), level=xbmc.LOGDEBUG)
        self.__set_focus_and_navigation_handling()
        self.visualize_automations(self.device)

    def __get_percent_controls(self):
        xbmc.log("PercentageWindow: __get_percent_controls: ", level=xbmc.LOGDEBUG)
        controls = {}
        # x = self.x
        # y = self.y
        status = self.device.get_display_value()
        status_control = xbmcgui.ControlLabel(self.x + 180, self.y + 65, 600, 75, status, font="font16",
                                              textColor="white")
        controls[statics.STATUS] = status_control
        slider = self.get_slider()
        controls[statics.SLIDER] = slider
        slider.setPercent(self.device.get_position())
        if self.device.get_devicegroup() == 2:
            down_button = self.getControl(1121)
            up_button = self.getControl(1131)
        else:
            down_button = self.getControl(112)
            up_button = self.getControl(113)
        controls[statics.DOWN] = down_button
        controls[statics.UP] = up_button
        return controls

    def update(self):
        xbmc.log("PercentageWindow: update: ", level=xbmc.LOGDEBUG)
        if self.getFocusId() == 0:
            if self.controls.get(statics.SLIDER) is not None:
                self.setFocus(self.controls.get(statics.SLIDER))
        if self.updater.get_status() != statics.UPDATE:
            xbmc.log("PercentageWindow: update:  no status update awaiting", xbmc.LOGNOTICE)
            try:
                new_device = self.client.get_device_by_id(self.device.get_device_id())
                if new_device.get_sync() != self.device.get_sync():  # device has changed
                    self.__update_position(new_device)
                    self.__update_name(new_device)
                    self.device = new_device
                if self.has_error and self.errorcontrol is not None:
                    self.removeControl(self.errorcontrol)
                    self.errorcontrol = None
                self.has_error = False
            except Exception, e:
                xbmc.log("PercentageWindow: update:" + repr(e.message), level=xbmc.LOGWARNING)
                self.has_error = True
        else:
            xbmc.log("PercentageWindow: update: Status update awaiting", xbmc.LOGNOTICE)
            try:
                new_device = self.client.get_device_by_id(self.device.get_device_id())
                if new_device.get_sync() != self.device.get_sync():  # device has changed
                    self.__update_icon(new_device)
                    self.__update_name(new_device)
                if self.has_error:
                    if self.errorcontrol is not None:
                        self.removeControl(self.errorcontrol)
                        self.errorcontrol = None
                    self.has_error = False
            except Exception, e:
                xbmc.log("PercentageWindow: update:" + repr(e.message), level=xbmc.LOGWARNING)
                self.has_error = True

        if self.has_error and self.errorcontrol is None:
            self.add_error_control()

    def __update_icon(self, new_device):
        xbmc.log("PercentageWindow: __update_icon: ", level=xbmc.LOGDEBUG)
        icon = self.controls[statics.ICON]
        image = new_device.get_icon()
        icon_img = os.path.join(base_window.images, image)
        icon.setImage(icon_img)

    def __update_position(self, new_device):
        xbmc.log("PercentageWindow: __update_position: ", level=xbmc.LOGDEBUG)
        self.__update_icon(new_device)
        if new_device.get_position() != self.device.get_position():
            statusSlider = self.controls[statics.SLIDER]
            statusSlider.setPercent(new_device.get_position())
            self.device = new_device
            statusLabel = self.controls[statics.STATUS]
            statusLabel.setLabel(new_device.get_display_value())

    def __update_name(self, new_device):
        xbmc.log("PercentageWindow: __update_name: ", level=xbmc.LOGDEBUG)
        if new_device.get_name() != self.device.get_name():
            title_label = self.controls[statics.TITLE]
            title_label.setLabel(new_device.get_name())

    def __set_focus_and_navigation_handling(self):
        xbmc.log("PercentageWindow: __set_focus_and_navigation_handling: ", level=xbmc.LOGDEBUG)
        statusSlider = self.controls[statics.SLIDER]
        downButton = self.controls[statics.DOWN]
        upButton = self.controls[statics.UP]

        self.setFocus(statusSlider)
        if self.device.get_devicegroup() == 2:
            statusSlider.controlDown(upButton)
            upButton.controlDown(downButton)
            upButton.controlRight(downButton)
            upButton.controlUp(statusSlider)
            upButton.controlLeft(statusSlider)
            downButton.controlUp(upButton)
            downButton.controlLeft(upButton)
            self.set_navigation_handling_for_automatik_and_favorit(downButton)
        else:
            statusSlider.controlDown(downButton)
            downButton.controlDown(upButton)
            downButton.controlRight(upButton)
            downButton.controlUp(statusSlider)
            downButton.controlLeft(statusSlider)
            upButton.controlUp(downButton)
            upButton.controlLeft(downButton)
            self.set_navigation_handling_for_automatik_and_favorit(upButton)

    def onClick(self, controlId):
        xbmc.log("PercentageWindow: onClick: controlId: " + repr(controlId), level=xbmc.LOGDEBUG)
        status_slider = self.controls[statics.SLIDER]
        down_button = self.controls[statics.DOWN]
        up_button = self.controls[statics.UP]
        auto_button = self.controls[statics.AUTO]
        favoriten_radio_control = self.controls[statics.FAVORITEN]
        status = self.device.get_status()
        # handle up-down-buttons
        device_group = self.device.get_devicegroup()
        try:
            if device_group == 2 or device_group == 4 or device_group == 8:  # rollo,dimmer,tore
                if controlId == down_button.getId():
                    self.client.move_down(self.device.get_device_id())
                elif controlId == up_button.getId():
                    self.client.move_up(self.device.get_device_id())
            else:
                if controlId == down_button.getId():
                    if status <= 95:
                        self.client.move_to_position(self.device.get_device_id(), status + 5)
                elif controlId == up_button.getId():
                    if status >= 5:
                        self.client.move_to_position(self.device.get_device_id(), status - 5)
        except Exception, e:
            xbmc.log("PercentageWindow: onClick" + str(e), level=xbmc.LOGWARNING)
            self.has_error = True

        # handle slider
        if controlId == status_slider.getId():
            current_slider_value = status_slider.getPercent()
            statusLabel = self.controls[statics.STATUS]
            device_group = self.device.get_devicegroup()
            display_value = homepilot_utils.get_display_value(int(current_slider_value), device_group)
            statusLabel.setLabel(display_value)
            if current_slider_value > status:
                new_position = current_slider_value
                self.updater.update_slider(new_position)
            elif current_slider_value < status:
                new_position = current_slider_value
                self.updater.update_slider(new_position)

        if controlId == auto_button.getId():
            self.handle_automation(self.device.get_device_id(), auto_button.isSelected(), self.device.is_automated())

        if controlId == favoriten_radio_control.getId():
            self.handle_favorit(self.device.get_device_id(), favoriten_radio_control.isSelected(),
                                self.device.is_favored(), self.use_local_favorites)

    def onAction(self, action):
        xbmc.log("PercentageWindow: onAction: ", level=xbmc.LOGDEBUG)
        if action == 92 or action == 10:
            self.updater.set_is_running(False)
        base_window.BaseWindow.onAction(self, action)

    def is_closed(self):
        return base_window.BaseWindow.is_closed(self)
