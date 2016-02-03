#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xbmcgui
import xbmc
import os
import base_view
from .. import homepilot_utils
from .. import statics
from .. import local_favorites


class FavoritenView(base_view.BaseView):
    def __init__(self, home_pilot_client, useLocalFavoritesBool, menu_control, group=None):
        base_view.BaseView.__init__(self)
        self.client = home_pilot_client
        self.total = 0
        self.controldict = {}
        if useLocalFavoritesBool:
            self.type = statics.FAVORITEN_LOKAL
        else:
            self.type = statics.FAVORITEN
        self.useLocalFavoritesBool = useLocalFavoritesBool
        self.list_item_dict = {}
        self.hp_error = False
        self.errorcontrol = None
        self.errorcontrol2 = None
        self.group = group
        self.menu_control = menu_control
        self.scene_group = None
        self.geraete_group = None
        self.szenen_control = None
        self.title_control = None
        xbmc.log("FavoritenView: __init__: type:" + repr(self.type), level=xbmc.LOGDEBUG)

    def get_id(self):
        return str(self.type) + "_view"

    def get_group(self):
        return self.group

    def visualize(self, window, addon, title=None):
        xbmc.log("FavoritenView: visualize: titel: "+repr(title), level=xbmc.LOGDEBUG)
        if title is None:
            self.title_control = homepilot_utils.get_title_control(self.type, addon)
        else:
            self.title_control = homepilot_utils.get_title_control(title, addon)

        label = addon.getLocalizedString(statics.SZENEN)
        self.szenen_control = xbmcgui.ControlLabel(400, 380, 600, 75, label, font="font16")
        window.addControls([self.title_control, self.szenen_control])
        homepilot_is_reachable = self.client.ping
        xbmc.log("reachable " + str(homepilot_is_reachable), level=xbmc.LOGNOTICE)
        self.scene_group = window.getControl(262)
        self.geraete_group = window.getControl(254)
        if not homepilot_is_reachable:
            xbmc.log("not reachable " + str(homepilot_is_reachable), level=xbmc.LOGNOTICE)
            self.hp_error = True
            errorlabel = self.get_communication_error_label()
            self.errorcontrol = xbmcgui.ControlLabel(400, 250, 700, 100, errorlabel, font="font12")
            window.addControl(self.errorcontrol)
            self.errorcontrol2 = xbmcgui.ControlLabel(400, 450, 700, 100, errorlabel, font="font12")
            window.addControl(self.errorcontrol2)
        else:
            self.hp_error = False
            self.__visualize_devices(window, addon)

    def __visualize_devices(self, window, addon):
        xbmc.log("FavoritenView: __visualize_devices: DEVICES", level=xbmc.LOGDEBUG)
        try:
            devices = self.__get_devices()
            if len(devices) > 0:
                self.geraete_list = window.getControl(255)
                self.geraete_list.reset()
                self.__add_listitems(devices)
                self.geraete_group.setVisible(True)
            xbmc.log("FavoritenView: __visualize_devices: SCENES", level=xbmc.LOGDEBUG)
            scenes = self.__get_scenes()
            if len(scenes) > 0:
                self.scene_list = window.getControl(264)
                self.scene_list.reset()
                self.__add_scene_item(scenes)
                self.scene_group.setVisible(True)

            if len(devices) > 0:
                self.menu_control.controlRight(self.geraete_list)
            elif len(scenes) > 0:
                self.menu_control.controlRight(self.scene_list)

        except Exception as inst:
            self.hp_error = True
            errorlabel = self.get_communication_error_label()
            self.errorcontrol = xbmcgui.ControlLabel(400, 250, 600, 75, errorlabel)
            window.addControl(self.errorcontrol)
            xbmc.log("FavoritenView: __visualize_devices: Exception: " + str(inst.message), level=xbmc.LOGWARNING)

    def __add_listitems(self, devs):
        xbmc.log("FavoritenView: __add_listitems: ", level=xbmc.LOGDEBUG)
        devices = self.sort_set(devs)
        try:
            for device in devices:
                item = xbmcgui.ListItem(label=device.get_name(), label2=device.get_display_value())
                icon_name = device.get_icon()
                xbmc.log("FavoritenView: __add_listitems: device: " + repr(device.get_favoredId()) +
                         "\ndevicename: " + repr(device.get_name()) +
                         "\nicon_name: " + repr(icon_name), level=xbmc.LOGDEBUG)
                item.setIconImage(os.path.join(base_view.images_device, icon_name))
                item.setProperty(statics.DESCRIPTION, device.get_description())
                item.setProperty(statics.DID, str(device.get_device_id()))
                item.setProperty(statics.SYNC, str(device.get_sync()))
                self.list_item_dict[device.get_device_id()] = item
                self.geraete_list.addItem(item)
        except Exception, e:
            xbmc.log("FavoritenView: __add_listitems: Exception: " + str(e.args), level=xbmc.LOGWARNING)

    def __add_scene_item(self, scens):
        xbmc.log("FavoritenView: __add_scene_item: ", level=xbmc.LOGDEBUG)
        scenes = self.sort_set(scens)
        for scene in scenes:
            xbmc.log("FavoritenView: __add_scene_item: scenes: " + repr(scene.get_id()) +
                         "\nscene name: " + repr(scene.get_name()), level=xbmc.LOGDEBUG)
            scene_item = xbmcgui.ListItem(label=scene.get_name())
            scene_item.setIconImage(base_view.szene_img)
            scene_item.setProperty(statics.SID, str(scene.get_id()))
            scene_item.setProperty(statics.DESCRIPTION, scene.get_description())
            self.scene_list.addItem(scene_item)

    def sort_set(self, set_to_sort):
        return sorted(set_to_sort, key=lambda obt: obt.get_name())

    def __get_devices(self):
        xbmc.log("FavoritenView: __get_devices: suseLocalFavoritesBool:" + repr(self.useLocalFavoritesBool), level=xbmc.LOGDEBUG)
        if self.useLocalFavoritesBool:
            devices = self.__get_local_favorit_devices()
        else:
            devices = self.client.get_favorite_devices()
        return devices

    def __get_scenes(self):
        xbmc.log("FavoritenView: __get_scenes: useLocalFavoritesBool: " + repr(self.useLocalFavoritesBool), level=xbmc.LOGDEBUG)
        if self.useLocalFavoritesBool:
            scenes = self.__get_local_favorit_scenes()
        else:
            scenes = self.client.get_favorite_scenes()
        return scenes

    def __get_local_favorit_devices(self):
        local_favorites_device_ids = local_favorites.get_devices_as_set()
        all_devices = self.client.get_devices()
        favorite_devices = []
        xbmc.log("FavoritenView: __get_local_favorit_devices: local_favorites_device_ids: " +
                 repr(local_favorites_device_ids), level=xbmc.LOGDEBUG)

        if local_favorites_device_ids is not None:
            for device in all_devices:
                if device.get_device_id() in local_favorites_device_ids:
                    xbmc.log("FavoritenView: __get_local_favorit_devices: device id: " + repr(device.get_device_id()), level=xbmc.LOGDEBUG)
                    favorite_devices.append(device)
        return set(favorite_devices)

    def __get_local_favorit_scenes(self):
        local_favorites_scene_ids = local_favorites.get_scenes_as_set()
        all_scenes = self.client.get_scenes()
        favorite_scenes = []
        xbmc.log("FavoritenView: __get_local_favorit_scenes: local_favorites_scene_ids: " +
                 repr(local_favorites_scene_ids), level=xbmc.LOGDEBUG)

        if local_favorites_scene_ids is not None:
            for scene in all_scenes:
                if scene.get_id() in local_favorites_scene_ids:
                    xbmc.log("FavoritenView: __get_local_favorit_scenes: scene id: " + repr(scene.get_id()), level=xbmc.LOGDEBUG)
                    favorite_scenes.append(scene)
        return set(favorite_scenes)

    def remove_everything(self, window):
        xbmc.log("FavoritenView: remove_everything: errorcontrol: " + repr(self.errorcontrol) +
                 "\nerrorcontrol2: " + repr(self.errorcontrol2) +
                 "\nhp_error: " + repr(self.hp_error) +
                 "\ntitle_control: " +repr(self.title_control) +
                 "\nszenen_control: " +repr(self.szenen_control) +
                 "\nscene_group: " +repr(self.scene_group) +
                 "\ngeraete_group: " +repr(self.geraete_group), level=xbmc.LOGDEBUG)
        if not self.hp_error:
            if self.errorcontrol is not None:
                window.removeControl(self.errorcontrol)
            if self.errorcontrol2 is not None:
                window.removeControl(self.errorcontrol2)
            if self.title_control is not None:
                xbmc.log("FavoritenView: remove_everything: title_control: "+repr(self.title_control.getId()), level=xbmc.LOGDEBUG)
                window.removeControl(self.title_control)
            if self.szenen_control is not None:
                xbmc.log("FavoritenView: remove_everything: title_control: "+repr(self.szenen_control.getId()), level=xbmc.LOGDEBUG)
                window.removeControl(self.szenen_control)
        if self.scene_group is not None:
            xbmc.log("FavoritenView: remove_everything: title_control: "+repr(self.scene_group.getId()), level=xbmc.LOGDEBUG)
            self.scene_group.setVisible(False)
        if self.geraete_group is not None:
            xbmc.log("FavoritenView: remove_everything: title_control: "+repr(self.geraete_group.getId()), level=xbmc.LOGDEBUG)
            self.geraete_group.setVisible(False)

    def update(self, window, addon, menuControl):
        xbmc.log("FavoritenView: update: hp_error: " + repr(self.hp_error), level=xbmc.LOGDEBUG)
        try:
            if self.hp_error:
                self.remove_everything(window)
                self.visualize(window, addon)
            else:
                new_devices = self.__get_devices()
                list_item_ids = self.list_item_dict.keys()
                xbmc.log("FavoritenView: update:\n new_devices: " + repr(new_devices) +
                         "\nlist_item_ids: " + repr(list_item_ids) +
                         "\nlist_item_dict: " + repr(self.list_item_dict), level=xbmc.LOGDEBUG)
                for new_device in new_devices:
                    new_sync_value = str(new_device.get_sync())
                    device_listitem = self.list_item_dict.get(new_device.get_device_id())
                    xbmc.log("FavoritenView: update: device_listitem: " + repr(device_listitem), level=xbmc.LOGDEBUG)
                    if device_listitem is not None:
                        list_item_ids.remove(new_device.get_device_id())
                        old_sync_value = device_listitem.getProperty(statics.SYNC)
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
                            old_label2 = device_listitem.getProperty(statics.DESCRIPTION)
                            new_label2 = new_device.get_description()
                            if old_label2 != new_label2.encode('utf8'):
                                device_listitem.setProperty(statics.DESCRIPTION, new_label2)
                    else:
                        # add new listitem
                        xbmc.log("FavoritenView: update: device_listitem is None.", level=xbmc.LOGDEBUG)
                        self.__add_listitems([new_device])
                # remove items from list when devices are no longer present
                # workaround implementation as the ControlList.removeItem didn't work
                if len(list_item_ids) > 0:
                    self.list_item_dict = {}
                    self.geraete_list.reset()
                    self.__add_listitems(new_devices)
            self.hp_error = False
        except Exception, e:
            if not self.hp_error:
                xbmc.log("FavoritenView: update: Exception: " + repr(self.type) + "  " + repr(e.message), level=xbmc.LOGERROR)
                self.remove_everything(window)
                self.visualize(window, addon)
                self.hp_error = True
