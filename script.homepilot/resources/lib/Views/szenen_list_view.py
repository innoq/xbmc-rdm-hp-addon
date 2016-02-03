#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xbmc

import xbmcgui
from .. import statics
from .. import homepilot_utils
import base_view


class SzenenListView(base_view.BaseView):
    def __init__(self, client, stype):
        base_view.BaseView.__init__(self)
        self.stype = stype
        self.client = client
        self.title_control = None
        self.errorcontrol = None

    def get_id(self):
        return str(self.stype) + "_view"

    def remove_everything(self, window):
        xbmc.log("SzenenListView: remove_everything: window: " + str(window), level=xbmc.LOGDEBUG)
        window.removeControls([self.title_control])
        scenes_group = window.getControl(260)
        if scenes_group is not None:
            scenes_group.setVisible(False)
        if self.errorcontrol is not None:
            window.removeControl(self.errorcontrol)

    def visualize(self, window, addon):
        xbmc.log("SzenenListView: visualize: window: " + str(window), level=xbmc.LOGDEBUG)
        self.title_control = homepilot_utils.get_title_control(self.stype, addon)
        window.addControl(self.title_control)
        scenes_list = window.getControl(258)
        scenes_list.reset()

        scenes = self.__get_scenes()
        if scenes is not None and len(scenes) > 0:
            scenes_group = window.getControl(260)
            scenes_group.setPosition(350, 100)
            scenes_group.setVisible(True)
            for scene in scenes:
                scene_item = xbmcgui.ListItem(label=scene.get_name())
                if scene.is_active():
                    scene_item.setIconImage(base_view.szene_img)
                else:
                    scene_item.setIconImage(base_view.szene_img_deact)
                scene_item.setProperty("sid", str(scene.get_id()))
                scene_item.setProperty("description", scene.get_description())
                scenes_list.addItem(scene_item)
            self.errorcontrol = None
            window.setFocusId(258)
        else:
            errorlabel = addon.getLocalizedString(32380)
            self.errorcontrol = xbmcgui.ControlLabel(450, 150, 600, 75, errorlabel)
            window.addControl(self.errorcontrol)
            # window.setFocusId(94)
        scenes_list.setVisible(True)
        return [self.title_control]

    def handle_click(self, control):
        pass

    def __get_scenes(self):
        xbmc.log("SzenenListView: __get_scenes: ", level=xbmc.LOGDEBUG)
        if self.stype == statics.SZENEN_ALLE:
            return self.client.get_scenes()
        elif self.stype == statics.SZENEN_MANUELL:
            return self.client.get_manual_scenes()
        elif self.stype == statics.SZENEN_NICHT_MANUELL:
            return self.client.get_non_manual_scenes()

    def update(self, window, addon, menuControl):
        xbmc.log("SzenenListView: update", level=xbmc.LOGDEBUG)
        try:
            self.remove_everything(window)
            self.visualize(window, addon)

        except Exception, e:
            xbmc.log("SzenenListView: update: Exception" + str(e.message), level=xbmc.LOGERROR)
