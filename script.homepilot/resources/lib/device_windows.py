#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import time
import math
import xbmc
import xbmcgui
import xbmcaddon
import threading
import os
import xbmcaddon
import homepilot_utils
import local_favorites
__addon__ = xbmcaddon.Addon(id='script.homepilot')
__addon_path__        = __addon__.getAddonInfo('path').decode("utf-8")
_images = os.path.join(__addon_path__, 'resources', 'skins', 'Default', 'media', 'devices')
_control_images = os.path.join(__addon_path__, 'resources', 'skins', 'Default', 'media')

class BaseWindow(xbmcgui.WindowXMLDialog):

    def is_closed(self):
        return self.is_closed

    def onAction(self, action):
        if action == 92 or action == 160 or action == 21:
            self.close()
            self.is_closed = True
        if action == 10:
            self.parent_window.shutdown()
            self.close()
            self.is_closed = True

    def add_error_control(self):
        label = __addon__.getLocalizedString(32381)
        self.errorcontrol = xbmcgui.ControlLabel(280, 250, 350, 75, label, alignment=0x00000002)
        self.addControl(self.errorcontrol)


class ErrorWindow(BaseWindow):

    def __init__( self, *args, **kwargs ):
        self.parent_window = kwargs["parent"]

    def onInit(self):
        self.add_error_control()

    def onAction(self, action):
        BaseWindow.onAction(self, action)


class MeterWindow(BaseWindow):

    def __init__( self, *args, **kwargs ):
        xbmcgui.WindowXMLDialog.__init__( self )
        self.client = kwargs["client"]
        self.did = kwargs["did"]
        self.parent_window = kwargs["parent"]

    def onInit(self):
        self.controls = []
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
        icon = self.meter.get_icon()
        icon_img = os.path.join(_images, icon)
        image_control = xbmcgui.ControlImage(260, 55, 40,40, icon_img)
        self.controls.append(image_control)
        title = self.meter.get_name()
        data = self.meter.get_data()
        title_control = xbmcgui.ControlLabel(310, 55, 600, 75, title, font="font16", textColor="white")
        self.controls.append(title_control)
        label = __addon__.getLocalizedString(32389)
        aktuell_control = xbmcgui.ControlLabel(300, 110, 600, 75, label, font="font12", textColor="white")
        self.controls.append(aktuell_control)
        y = 150
        for data_dict in data:
            for d in data_dict:
                label = d + ": " + data_dict[d]
                data_control = xbmcgui.ControlLabel(300, y, 600, 75, label, font="font12", textColor="white")
                y += 35
                self.controls.append(data_control)
        self.addControls(self.controls)


    def update(self):
        try:
            new_meter = self.client.get_meter_by_id(self.did)
            #self.errorcontrol = None
        except Exception, e:
            xbmc.log(str(e), level=xbmc.LOGWARNING)
            #self.add_error_control()

    def __disable_favorite_and_automatik_control(self):
        automation_control = self.getControl(138)
        automation_control.setVisible(False)
        favorit_control = self.getControl(134)
        favorit_control.setVisible(False)
        automatik_control = self.getControl(130)
        automatik_control.setVisible(False)

    def __resize_window(self):
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
        BaseWindow.onAction(self, action)


sliderbarImg = os.path.join(_control_images, 'slider.png')
sliderNibImg = os.path.join(_control_images, 'osd_slider_nib.png')
sliderNibImgNF = os.path.join(_control_images, 'osd_slider_nibNF.png')
PERCENT_TYPE = "PERCENT"
DEGREE_TYPE = "DEGREE"


class SliderUpdater (threading.Thread):

    def __init__(self, client, device, type):
        threading.Thread.__init__(self)
        self.position = -1
        self.update_time = 0
        self.client = client
        self.device = device
        self.status = "NOTHING"
        self.type = type

    def update_slider (self, new_value):
        if self.position != new_value:
            #xbmc.log(str(self.position), xbmc.LOGNOTICE)
            #xbmc.log(str(new_value), xbmc.LOGNOTICE)
            self.update_time = time.time()
            self.position = new_value
            self.status = "UPDATE"

    def set_is_running (self, is_running):
        self.is_running = is_running

    def get_status(self):
        return self.status

    def run(self):
        self.is_running = 'True'
        count = 0
        while self.is_running:
            if self.update_time > 0 and time.time() - self.update_time > 0.4:
                if self.status == "UPDATE":
                    #xbmc.log("-- send move --" + str(self.position), xbmc.LOGNOTICE)
                    if self.type == PERCENT_TYPE and count < 3:
                        success = self.client.move_to_position(self.device.get_device_id(), self.position)
                        if success:
                            self.status = "UPDATE_SENT"
                            count = 0
                        else:
                            count += 1
                    elif count < 3:
                        success = self.client.move_to_degree(self.device.get_device_id(), self.position)
                        if success:
                            self.status = "UPDATE_SENT"
                            count = 0
                        else:
                            count += 1
            time.sleep(0.3)

class DeviceWindow(BaseWindow):
    '''
    Parent class for all types of devices (Thermostat, Schalter, Dimmer, Tor, ...)
    '''

    def __init__( self, *args, **kwargs ):
        xbmcgui.WindowXMLDialog.__init__( self )
        self.x = 250
        self.y = 40

    def get_base_device_controls(self, device):
        control_dict = {}
        title = self.device.get_name()
        title_control = xbmcgui.ControlLabel(325, 55, 600, 75, title, font="font16", textColor="white")
        control_dict["title"] = title_control
        icon = self.device.get_icon()
        icon_img = os.path.join(_images, icon)
        image_control = xbmcgui.ControlImage ( self.x + 80, self.y + 60, 50, 50, icon_img)
        control_dict["icon"] = image_control
        auto_control = self.getControl(132)
        auto_control.setSelected(device.is_automated())
        control_dict["auto"] = auto_control
        fav_control = self.getControl(136)
        if self.use_local_favorites:
            favored_devices = local_favorites.get_devices_as_set()
            if device.get_device_id() in favored_devices:
                fav_control.setSelected(True)
            else:
                fav_control.setSelected(False)
        else:
            fav_control.setSelected(device.is_favored())
        control_dict["favoriten"] = fav_control
        return control_dict

    def get_slider (self):
        if xbmc.skinHasImage ('settings/slider_back.png'):
            statusSlider = xbmcgui.ControlSlider(self.x + 30, self.y + 130, 310, 15, textureback = 'settings/slider_back.png', texture = 'settings/orb_nofo.png', texturefocus = 'settings/orb_fo.png')
            return statusSlider
        elif xbmc.skinHasImage ('slider.png'):
            statusSlider = xbmcgui.ControlSlider(self.x + 80, self.y + 130, 240, 20, textureback = 'slider.png', texture = 'osd_slider_nibNF.png', texturefocus = 'osd_slider_nib.png')
            return statusSlider
        else:
            statusSlider = xbmcgui.ControlSlider(self.x + 80, self.y + 130, 240, 20, textureback = sliderbarImg, texture = sliderNibImgNF, texturefocus = sliderNibImg)
            return statusSlider

    def handle_automation(self, deviceId, is_selected, is_automated):
        if is_selected and not is_automated:
            self.client.set_device_automation_on(deviceId)
        elif not is_selected and is_automated:
            self.client.set_device_automation_off(deviceId)

    def handle_favorit(self, deviceId, is_selected, is_favorited, use_local_favorites):
        favored_devices = local_favorites.get_devices_as_set()
        if use_local_favorites:
            if is_selected and not deviceId in favored_devices:
                local_favorites.add_device(deviceId)
            elif not is_selected and deviceId in favored_devices:
                local_favorites.remove_device(deviceId)
        else:
            if is_selected and not is_favorited:
                self.client.favorize_device(deviceId)
            elif not is_selected and is_favorited:
                self.client.unfavorize_device(deviceId)

    def set_navigation_handling_for_automatik_and_favorit(self, previous_control):
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
        automation_list = self.getControl(142)
        automation_list.reset()
        automations = device.get_automationen()
        homepilot_utils.add_device_to_automation_list(automation_list, automations, __addon__)

class PercentageWindow(DeviceWindow):

    def __init__( self, *args, **kwargs ):
        DeviceWindow.__init__( self )
        self.client = kwargs["client"]
        self.device = kwargs["device"]
        self.parent_window = kwargs["parent"]
        self.use_local_favorites = kwargs["local_favs"]
        self.updater = SliderUpdater(self.client, self.device, PERCENT_TYPE)
        self.updater.start()
        self.has_error = False
        self.controls = {}
        self.errorcontrol = None

    def onInit(self):
        base_device_controls = self.get_base_device_controls(self.device)
        percent_controls = self.__get_percent_controls()
        self.controls = base_device_controls
        self.controls.update(percent_controls)
        if self.device.get_devicegroup() == 2:
            button_group = self.getControl(1141)
        else:
            button_group = self.getControl(114)
        button_group.setPosition(330,200)
        self.addControls([self.controls["slider"], self.controls["status"], self.controls["title"], self.controls["icon"]])
        slider = self.controls["slider"]
        slider.setPercent(self.device.get_position())
        self.__set_focus_and_navigation_handling()
        self.visualize_automations(self.device)

    def __get_percent_controls (self):
        controls = {}
        x = self.x
        y = self.y
        status = self.device.get_display_value()
        status_control = xbmcgui.ControlLabel(self.x+ 180, self.y + 65, 600, 75, status, font="font16", textColor="white")
        controls["status"] = status_control
        slider = self.get_slider()
        controls["slider"] = slider
        slider.setPercent(self.device.get_position())
        if self.device.get_devicegroup() == 2:
            down_button = self.getControl(1121)
            up_button = self.getControl(1131)
        else:
            down_button = self.getControl(112)
            up_button = self.getControl(113)
        controls["down"] = down_button
        controls["up"] = up_button
        return controls

    def update(self):
        if self.getFocusId() == 0:
            if self.controls.get("slider") is not None:
                self.setFocus(self.controls.get("slider"))
        if self.updater.get_status() != "UPDATE":
            #xbmc.log("-- update -- no status update awaiting", xbmc.LOGNOTICE)
            try:
                new_device = self.client.get_device_by_id(self.device.get_device_id())
                if new_device.get_sync() != self.device.get_sync():#device has changed
                    self.__update_position(new_device)
                    self.__update_name(new_device)
                    self.device = new_device
                if self.has_error and self.errorcontrol is not None:
                    self.removeControl(self.errorcontrol)
                    self.errorcontrol = None
                self.has_error = False
            except Exception, e:
                xbmc.log(str(e), level=xbmc.LOGWARNING)
                self.has_error = True
        else:
            try:
                new_device = self.client.get_device_by_id(self.device.get_device_id())
                if new_device.get_sync() != self.device.get_sync():#device has changed
                    self.__update_icon(new_device)
                    self.__update_name(new_device)
                if self.has_error:
                    if self.errorcontrol is not None:
                        self.removeControl(self.errorcontrol)
                        self.errorcontrol = None
                    self.has_error = False
            except Exception, e:
                xbmc.log(str(e), level=xbmc.LOGWARNING)
                self.has_error = True

        if self.has_error and self.errorcontrol is None:
            self.add_error_control()


    def __update_icon(self, new_device):
        icon = self.controls["icon"]
        image = new_device.get_icon()
        icon_img = os.path.join(_images, image)
        icon.setImage(icon_img)

    def __update_position (self, new_device):
        self.__update_icon(new_device)
        if new_device.get_position() != self.device.get_position():
            statusSlider = self.controls["slider"]
            #xbmc.log("set slider to position: " + str(new_device.get_position()), xbmc.LOGNOTICE)
            statusSlider.setPercent(new_device.get_position())
            self.device = new_device
            statusLabel = self.controls["status"]
            statusLabel.setLabel(new_device.get_display_value())


    def __update_name(self, new_device):
        if new_device.get_name() != self.device.get_name():
            title_label = self.controls["title"]
            title_label.setLabel(new_device.get_name())


    def __set_focus_and_navigation_handling(self):
        statusSlider = self.controls["slider"]
        downButton = self.controls["down"]
        upButton = self.controls["up"]

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


    def onClick (self, controlId):
        statusSlider = self.controls["slider"]
        down_button = self.controls["down"]
        up_button = self.controls["up"]
        auto_button = self.controls["auto"]
        favoriten_radio_control = self.controls["favoriten"]
        status = self.device.get_status()
        #handle up-down-buttons
        device_group = self.device.get_devicegroup()
        try:
            if device_group == 2 or device_group == 4 or device_group == 8:#rollo,dimmer,tore
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
            xbmc.log(str(e), level=xbmc.LOGWARNING)
            self.has_error = True

        #handle slider
        if controlId == statusSlider.getId():
            current_slider_value = statusSlider.getPercent()
            statusLabel = self.controls["status"]
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
            self.handle_favorit(self.device.get_device_id(), favoriten_radio_control.isSelected(), self.device.is_favored(), self.use_local_favorites)


    def onAction(self, action):
        if action == 92 or action == 10:
            self.updater.set_is_running(False)
        BaseWindow.onAction(self, action)

class SwitchWindow(DeviceWindow):

    def __init__( self, *args, **kwargs ):
        DeviceWindow.__init__( self )
        self.client = kwargs["client"]
        self.device = kwargs["device"]
        self.parent_window = kwargs["parent"]
        self.use_local_favorites = kwargs["local_favs"]
        self.wait_for_response = False
        self.updater = SliderUpdater(self.client, self.device, DEGREE_TYPE)
        self.errorcontrol = None
        self.has_error = False

    def onInit(self):
        base_device_controls = self.get_base_device_controls(self.device)
        switch_controls = self.__get_switch_controls()

        self.controls = base_device_controls
        self.controls.update(switch_controls)
        self.addControls([self.controls["title"], self.controls["icon"]])
        self.__set_focus_and_navigation_handling()
        self.visualize_automations(self.device)

    def __get_switch_controls(self):
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
        controls["group"] = group_control
        controls["radio"] = radio
        controls["on"] = on
        controls["off"] = off
        return controls

    def update (self):
        if self.getFocusId() == 0:
            self.setFocusId(116)
        try:
            new_device = self.client.get_device_by_id(self.device.get_device_id())
            if new_device.get_sync() != self.device.get_sync():
                if new_device.get_position() != self.device.get_position():
                    self.__set_state(new_device)
                if new_device.get_name() != self.device.get_name():
                    title_label = self.controls["title"]
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
        radio = self.getControl(116)
        on = self.getControl(115)
        off = self.getControl(117)
        icon = self.controls["icon"]
        if new_device.get_position() > 0:
            radio.setSelected(True)
            on.setEnabled(True)
            off.setEnabled(False)
        else:
            radio.setSelected(False)
            on.setEnabled(False)
            off.setEnabled(True)
        image = new_device.get_icon()
        icon_img = os.path.join(_images, image)
        icon.setImage(icon_img)

    def __set_focus_and_navigation_handling(self):
        button = self.controls["radio"]
        self.set_navigation_handling_for_automatik_and_favorit(button)
        self.setFocus(button)

    def onClick (self, controlId):
        button = self.controls["radio"]
        autoButton = self.controls["auto"]
        favoriten_radio_control = self.controls["favoriten"]
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
            self.handle_favorit(self.device.get_device_id(), favoriten_radio_control.isSelected(), self.device.is_favored(), self.use_local_favorites)

    def onAction(self, action):
        BaseWindow.onAction(self, action)

class DegreeWindow(DeviceWindow):

    def __init__( self, *args, **kwargs ):
        DeviceWindow.__init__( self )
        self.client = kwargs["client"]
        self.device = kwargs["device"]
        self.parent_window = kwargs["parent"]
        self.use_local_favorites = kwargs["local_favs"]
        self.updater = SliderUpdater(self.client, self.device, DEGREE_TYPE)
        self.updater.start()
        self.errorcontrol = None
        self.has_error = False

    def onInit(self):
        base_device_controls = self.get_base_device_controls(self.device)
        degree_controls = self.__get_degree_controls()
        self.controls = base_device_controls
        self.controls.update(degree_controls)
        button_group = self.getControl(114)
        button_group.setPosition(330,200)
        self.addControls([self.controls["slider"], self.controls["status"], self.controls["title"], self.controls["icon"]])
        slider = self.controls["slider"]
        slider_position = self.__get_slider_percent_from_position(self.device)
        slider.setPercent(slider_position)
        self.__set_focus_and_navigation_handling()
        self.visualize_automations(self.device)

    def __get_degree_controls (self):
        controls = {}
        x = self.x
        y = self.y
        status = self.device.get_display_value()
        status_control = xbmcgui.ControlLabel(self.x+ 180, self.y + 60, 600, 75, status, font="font16", textColor="white")
        controls["status"] = status_control
        controls["slider"] = self.get_slider()
        controls["down"] = self.getControl(112)
        controls["up"] = self.getControl(113)
        return controls

    def __get_slider_percent_from_position (self, device):
        position = device.get_position()
        return (float(position)/10 - 3) * 4


    def __set_focus_and_navigation_handling(self):
        statusSlider = self.controls["slider"]
        downButton = self.controls["down"]
        upButton = self.controls["up"]
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
        if self.getFocusId() == 0:
            self.setFocus(self.controls["slider"])
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
            xbmc.log(str(e), level=xbmc.LOGWARNING)
            self.has_error = True

        if self.has_error and self.errorcontrol is None:
            self.add_error_control()

    def __update_icon(self, new_device):
        icon = self.controls["icon"]
        image = new_device.get_icon()
        icon_img = os.path.join(_images, image)
        icon.setImage(icon_img)

    def __update_position(self, new_device):
        if new_device.get_position() != self.device.get_position():
            statusSlider = self.controls["slider"]
            new_position = self.__get_slider_percent_from_position(new_device)
            statusSlider.setPercent(new_position)
            self.device = new_device
            statusLabel = self.controls["status"]
            statusLabel.setLabel(new_device.get_display_value())
            self.__update_icon(new_device)

    def __update_name (self, new_device):
        if new_device.get_name() != self.device.get_name():
            title_label = self.controls["title"]
            title_label.setLabel(new_device.get_name())

    def onClick (self, controlId):
        xbmc.log("window click " + str(controlId), level=xbmc.LOGNOTICE)
        statusSlider = self.controls["slider"]
        downButton = self.controls["down"]
        upButton = self.controls["up"]
        autoButton = self.controls["auto"]
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
                statusLabel = self.controls["status"]
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
            self.handle_favorit(self.device.get_device_id(), favoriten_radio_control.isSelected(), self.device.is_favored(), self.use_local_favorites)

    def onAction(self, action):
        if action == 92 or action == 10:
            self.updater.set_is_running = False
        BaseWindow.onAction(self, action)
