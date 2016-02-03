#!/usr/bin/env python
# -*- coding: utf-8 -*-

import base_window
from .. import statics
import xbmc


class ErrorWindow(base_window.BaseWindow):
    def __init__(self, xmlFilename, scriptPath, *args, **kwargs):
        super(ErrorWindow, self).__init__(xmlFilename, scriptPath)
        self.parent_window = kwargs[statics.PARENT]

    def onInit(self):
        self.add_error_control()

    def onAction(self, action):
        xbmc.log("ErrorWindow: onAction: ", level=xbmc.LOGDEBUG)
        base_window.BaseWindow.onAction(self, action)

    def is_closed(self):
        return base_window.BaseWindow.is_closed()
