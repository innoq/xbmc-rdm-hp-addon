#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import xbmc
import xbmcgui
import base_window
from .. import homepilot_utils
from .. import statics
from .. import local_favorites


class DeviceWindow(base_window.BaseWindow):
    """
    Parent class for all types of devices (Thermostat, Schalter, Dimmer, Tor, ...)
    """

    def __init__(self, *args, **kwargs):
        xbmc.log("DeviceWindow: __init__ ", level=xbmc.LOGDEBUG)
        xbmcgui.WindowXMLDialog.__init__(self)
        self.x = 250
        self.y = 40
        self.device = None
        self.client = None
        self.use_local_favorites = kwargs[statics.LOCAL_FAVS]
        xbmc.log("DeviceWindow: __init__ ", level=xbmc.LOGDEBUG)

    def get_base_device_controls(self, device):
        self.device = device
        xbmc.log("DeviceWindow: get_base_device_controls: ", level=xbmc.LOGDEBUG)
        control_dict = {}
        title = self.device.get_name()
        title_control = xbmcgui.ControlLabel(325, 55, 600, 75, title, font="font16", textColor="white")
        control_dict[statics.TITLE] = title_control
        icon = self.device.get_icon()
        icon_img = os.path.join(base_window.images, icon)
        image_control = xbmcgui.ControlImage(self.x + 80, self.y + 60, 50, 50, icon_img)
        control_dict[statics.ICON] = image_control
        auto_control = self.getControl(132)
        auto_control.setSelected(device.is_automated())
        control_dict[statics.AUTO] = auto_control
        fav_control = self.getControl(136)

        if self.use_local_favorites:
            favored_devices = local_favorites.get_devices_as_set()
            xbmc.log("DeviceWindow: get_base_device_controls: Local favored_devices: " + repr(favored_devices),
                     level=xbmc.LOGDEBUG)
            if favored_devices is not None:
                if device.get_device_id() in favored_devices:
                    fav_control.setSelected(True)
                else:
                    fav_control.setSelected(False)
        else:
            xbmc.log("DeviceWindow: get_base_device_controls: Keine lokalen Favoriten. ", level=xbmc.LOGDEBUG)
            fav_control.setSelected(device.is_favored())
        control_dict[statics.FAVORITEN] = fav_control
        return control_dict

    def get_slider(self):
        xbmc.log("DeviceWindow: get_slider: ", level=xbmc.LOGDEBUG)
        if xbmc.skinHasImage('settings/slider_back.png'):
            status_slider = xbmcgui.ControlSlider(self.x + 30, self.y + 130, 310, 15,
                                                 textureback='settings/slider_back.png',
                                                 texture='settings/orb_nofo.png', texturefocus='settings/orb_fo.png')
        elif xbmc.skinHasImage('slider.png'):
            status_slider = xbmcgui.ControlSlider(self.x + 80, self.y + 130, 240, 20, textureback='slider.png',
                                                 texture='osd_slider_nibNF.png', texturefocus='osd_slider_nib.png')
        else:
            status_slider = xbmcgui.ControlSlider(self.x + 80, self.y + 130, 240, 20,
                                                 textureback=base_window.sliderbarImg,
                                                 texture=base_window.sliderNibImgNF,
                                                 texturefocus=base_window.sliderNibImg)
        return status_slider

    def handle_automation(self, deviceId, is_selected, is_automated):
        xbmc.log("DeviceWindow: handle_automation: ", level=xbmc.LOGDEBUG)
        if is_selected and not is_automated:
            self.client.set_device_automation_on(deviceId)
        elif not is_selected and is_automated:
            self.client.set_device_automation_off(deviceId)

    def handle_favorit(self, deviceId, is_selected, is_favorited, use_local_favorites):
        xbmc.log("DeviceWindow: handle_favorit: ", level=xbmc.LOGDEBUG)
        favored_devices = local_favorites.get_devices_as_set()
        if use_local_favorites:
            if favored_devices is None:
                if is_selected:
                    local_favorites.add_device(deviceId)
                elif not is_selected:
                    local_favorites.remove_device(deviceId)
            elif favored_devices is not None:
                if is_selected:
                    if deviceId not in favored_devices:
                        local_favorites.add_device(deviceId)
                    elif not is_selected and deviceId in favored_devices:
                        local_favorites.remove_device(deviceId)
                elif not is_selected and deviceId in favored_devices:
                    local_favorites.remove_device(deviceId)
        else:
            if is_selected and not is_favorited:
                self.client.favorize_device(deviceId)
            elif not is_selected and is_favorited:
                self.client.unfavorize_device(deviceId)

    def set_navigation_handling_for_automatik_and_favorit(self, previous_control):
        xbmc.log("DeviceWindow: set_navigation_handling_for_automatik_and_favorit: ", level=xbmc.LOGDEBUG)
        autoButton = self.getControl(132)
        favorit_button = self.getControl(136)
        autoScrollbar = self.getControl(142)
        previous_control.controlRight(autoButton)
        previous_control.controlDown(autoButton)
        autoButton.controlLeft(previous_control)
        autoButton.controlUp(previous_control)
        autoButton.controlRight(favorit_button)
        autoButton.controlDown(favorit_button)
        favorit_button.controlLeft(autoButton)
        favorit_button.controlUp(autoButton)
        favorit_button.controlDown(autoScrollbar)
        favorit_button.controlRight(autoScrollbar)
        autoScrollbar.controlLeft(favorit_button)
        autoScrollbar.controlUp(favorit_button)

    def visualize_automations(self, device):
        xbmc.log("DeviceWindow: visualize_automations: ", level=xbmc.LOGDEBUG)
        automation_list = self.getControl(142)
        automation_list.reset()
        automations = device.get_automationen()
        homepilot_utils.add_device_to_automation_list(automation_list, automations, base_window.__addon__)
