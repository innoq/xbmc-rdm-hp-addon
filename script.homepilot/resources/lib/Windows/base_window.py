#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

import xbmc
import xbmcaddon
import xbmcgui
from .. import statics

__addon__ = xbmcaddon.Addon(id='script.homepilot')
__addon_path__ = __addon__.getAddonInfo('path').decode("utf-8")
_control_images = os.path.join(__addon_path__, 'resources', 'skins', 'Default', 'media')
images = os.path.join(__addon_path__, 'resources', 'skins', 'Default', 'media', 'devices')

sliderbarImg = os.path.join(_control_images, 'slider.png')
sliderNibImg = os.path.join(_control_images, 'osd_slider_nib.png')
sliderNibImgNF = os.path.join(_control_images, 'osd_slider_nibNF.png')


class BaseWindow(xbmcgui.WindowXMLDialog):
    def __init__(self, xmlFilename, scriptPath, defaultSkin='Default', defaultRes='720p'):
        super(BaseWindow, self).__init__(xmlFilename, scriptPath, defaultSkin='Default', defaultRes='720p')
        self.parent_window = None
        self.errorcontrol = None
        self._is_closed = True

    def is_closed(self):
        xbmc.log("BaseWindow: is_closed: is_closed: "+repr(self._is_closed), level=xbmc.LOGDEBUG)
        return self._is_closed

    def onAction(self, action):
        xbmc.log("BaseWindow: onAction: action: "+repr(action), level=xbmc.LOGDEBUG)
        if action == statics.ACTION_NAV_BACK or action == statics.ACTION_LAST_PAGE or action == statics.ACTION_STEP_BACK:
            self.close()
            self._is_closed = True
        if action == statics.ACTION_PREVIOUS_MENU:
            self.parent_window.shutdown()
            self.close()

    def add_error_control(self):
        label = __addon__.getLocalizedString(32381)
        self.errorcontrol = xbmcgui.ControlLabel(280, 250, 350, 75, label, alignment=0x00000002)
        self.addControl(self.errorcontrol)
