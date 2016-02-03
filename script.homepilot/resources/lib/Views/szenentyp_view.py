#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xbmcgui
import xbmc
import base_view
from .. import statics
from .. import homepilot_utils


class SzenentypView(base_view.BaseView):
    def __init__(self):
        base_view.BaseView.__init__(self)
        self.scenes_list = None
        self.manuell_item = None
        self.nicht_manuell_item = None
        self.title_control = None
        self.alle_item = None

    def get_id(self):
        return str(statics.SZENENTYPEN) + "_view"

    def remove_everything(self, window):
        xbmc.log("SzenentypView: remove_everything: window: " + str(window), level=xbmc.LOGDEBUG)
        if self.scenes_list is not None:
            self.scenes_list.setVisible(False)
        try:
            window.removeControls([self.title_control])
        except RuntimeError, e:
            xbmc.log("SzenentypView: Control does not exist in window " + str(e.message), level=xbmc.LOGERROR)

    def visualize(self, window, addon):
        self.title_control = homepilot_utils.get_title_control(32016, addon)
        window.addControl(self.title_control)
        self.scenes_list = window.getControl(257)
        self.scenes_list.reset()

        self.manuell_item = xbmcgui.ListItem(addon.getLocalizedString(32017))
        self.manuell_item.setIconImage(base_view.scene_manual)
        self.manuell_item.setProperty("pid", "0")
        self.scenes_list.addItem(self.manuell_item)

        self.nicht_manuell_item = xbmcgui.ListItem(addon.getLocalizedString(32018))
        self.nicht_manuell_item.setIconImage(base_view.scene_non_manual)
        self.nicht_manuell_item.setProperty("pid", "1")
        self.scenes_list.addItem(self.nicht_manuell_item)

        self.alle_item = xbmcgui.ListItem(addon.getLocalizedString(32020))
        self.alle_item.setProperty("pid", "2")
        self.scenes_list.addItem(self.alle_item)

        self.scenes_list.setVisible(True)

        return [self.title_control]

    def handle_click(self, item):
        position = item.getProperty("pid")
        xbmc.log("SzenentypView: handle_click: position: " + str(position), level=xbmc.LOGDEBUG)
        if position == "0":
            return statics.SZENEN_MANUELL
        elif position == "1":
            return statics.SZENEN_NICHT_MANUELL
        elif position == "2":
            return statics.SZENEN_ALLE
        return None

    def focus_list_item(self, view_id):
        xbmc.log("SzenentypView: focus_list_item: view_id: " + str(view_id), level=xbmc.LOGDEBUG)
        if view_id == str(statics.SZENEN_MANUELL) + "_view":
            self.scenes_list.selectItem(0)
        elif view_id == str(statics.SZENEN_NICHT_MANUELL) + "_view":
            self.scenes_list.selectItem(1)
        elif view_id == str(statics.SZENEN_ALLE) + "_view":
            self.scenes_list.selectItem(2)
