#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xbmc

import xbmcgui
import base_view
from .. import homepilot_utils
from .. import statics


class EmptyView(base_view.BaseView):
    def __init__(self):
        base_view.BaseView.__init__(self)
        self.einstellungen_control = None
        self.label = None

    def get_id(self):
        return statics.empty_view_id

    def remove_everything(self, window):
        xbmc.log("EmptyView: remove_everything: ", level=xbmc.LOGDEBUG)
        window.removeControls([self.einstellungen_control, self.label])

    def visualize(self, window, addon):
        xbmc.log("EmptyView: visualize: ", level=xbmc.LOGDEBUG)
        MESSAGE_SETTINGS_DIALOG = base_view.__addon__.getLocalizedString(32384)
        self.einstellungen_control = homepilot_utils.get_title_control(32008, addon)
        self.label = xbmcgui.ControlLabel(460, 250, 590, 40, MESSAGE_SETTINGS_DIALOG, alignment=0x00000002)
        window.addControls([self.einstellungen_control, self.label])
        return [self.einstellungen_control, self.label]

    def handle_click(self, control):
        xbmc.log("EmptyView: handle_click: ", level=xbmc.LOGDEBUG)
        pass
