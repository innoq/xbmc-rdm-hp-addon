#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import device_window
import xbmc
from .. import statics
import slider_updater
import base_window


class SwitchWindow(device_window.DeviceWindow):
    def __init__(self, *args, **kwargs):
        super(SwitchWindow, self).__init__(*args, **kwargs)
        self.client = kwargs[statics.CLIENT]
        self.device = kwargs[statics.DEVICE]
        self.parent_window = kwargs[statics.PARENT]
        self.use_local_favorites = kwargs[statics.LOCAL_FAVS]
        self.wait_for_response = False
        self.updater = slider_updater.SliderUpdater(self.client, self.device, statics.DEGREE_TYPE)
        self.errorcontrol = None
        self.has_error = False
        self.controls = None

    def onInit(self):
        xbmc.log("SwitchWindow: onInit: ", level=xbmc.LOGDEBUG)
        base_device_controls = self.get_base_device_controls(self.device)
        switch_controls = self.__get_switch_controls()

        self.controls = base_device_controls
        self.controls.update(switch_controls)
        self.addControls([self.controls[statics.TITLE], self.controls[statics.ICON]])
        self.__set_focus_and_navigation_handling()
        self.visualize_automations(self.device)

    def __get_switch_controls(self):
        xbmc.log("SwitchWindow: __get_switch_controls: ", level=xbmc.LOGDEBUG)
        controls = {}
        group_control = self.getControl(118)
        group_control.setPosition(350, 100)

        radio = self.getControl(116)
        on = self.getControl(115)
        off = self.getControl(117)
        if self.device.get_position() > 0:
            radio.setSelected(True)
            on.setEnabled(True)
            off.setEnabled(False)
        else:
            radio.setSelected(False)
            on.setEnabled(False)
            off.setEnabled(True)
        controls[statics.GROUP] = group_control
        controls[statics.RADIO] = radio
        controls[statics.ON] = on
        controls[statics.OFF] = off
        return controls

    def update(self):
        xbmc.log("SwitchWindow: update: ", level=xbmc.LOGDEBUG)
        if self.getFocusId() == 0:
            self.setFocusId(116)
        try:
            new_device = self.client.get_device_by_id(self.device.get_device_id())
            if new_device.get_sync() != self.device.get_sync():
                if new_device.get_position() != self.device.get_position():
                    self.__set_state(new_device)
                if new_device.get_name() != self.device.get_name():
                    title_label = self.controls[statics.TITLE]
                    title_label.setLabel(new_device.get_name())
                self.device = new_device
            if self.has_error:
                self.has_error = False
                if self.errorcontrol is not None:
                    self.removeControl(self.errorcontrol)
                    self.errorcontrol = None
        except Exception, e:
            xbmc.log(str(e), level=xbmc.LOGWARNING)
            self.has_error = True

        if self.has_error and self.errorcontrol is None:
            self.add_error_control()

    def __set_state(self, new_device):
        xbmc.log("SwitchWindow: __set_state: ", level=xbmc.LOGDEBUG)
        radio = self.getControl(116)
        on = self.getControl(115)
        off = self.getControl(117)
        icon = self.controls[statics.ICON]
        if new_device.get_position() > 0:
            radio.setSelected(True)
            on.setEnabled(True)
            off.setEnabled(False)
        else:
            radio.setSelected(False)
            on.setEnabled(False)
            off.setEnabled(True)
        image = new_device.get_icon()
        icon_img = os.path.join(base_window.images, image)
        icon.setImage(icon_img)

    def __set_focus_and_navigation_handling(self):
        xbmc.log("SwitchWindow: __set_focus_and_navigation_handling: ", level=xbmc.LOGDEBUG)
        button = self.controls[statics.RADIO]
        self.set_navigation_handling_for_automatik_and_favorit(button)
        self.setFocus(button)

    def onClick(self, controlId):
        xbmc.log("SwitchWindow: onClick: controlls: " + repr(self.controls), level=xbmc.LOGDEBUG)
        button = self.controls[statics.RADIO]
        autoButton = self.controls[statics.AUTO]
        if statics.FAVORITEN not in self.controls:
            self.controls.update(self.get_base_device_controls(self.device))
        favoriten_radio_control = self.controls[statics.FAVORITEN]
        on = self.getControl(115)
        off = self.getControl(117)
        if controlId == button.getId():
            if button.isSelected():
                on.setEnabled(True)
                off.setEnabled(False)
                self.client.switch_on(self.device.get_device_id())
            else:
                on.setEnabled(False)
                off.setEnabled(True)
                self.client.switch_off(self.device.get_device_id())
        if controlId == autoButton.getId():
            self.handle_automation(self.device.get_device_id(), autoButton.isSelected(), self.device.is_automated())

        if controlId == favoriten_radio_control.getId():
            self.handle_favorit(self.device.get_device_id(), favoriten_radio_control.isSelected(),
                                self.device.is_favored(), self.use_local_favorites)

    def onAction(self, action):
        xbmc.log("SwitchWindow: onAction: ", level=xbmc.LOGDEBUG)
        base_window.BaseWindow.onAction(self, action)

    def is_closed(self):
        return base_window.BaseWindow.is_closed()
