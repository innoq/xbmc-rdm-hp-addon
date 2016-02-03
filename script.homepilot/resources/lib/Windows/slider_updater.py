#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import threading
from .. import statics
import xbmc


class SliderUpdater(threading.Thread):
    def __init__(self, client, device, type):
        threading.Thread.__init__(self)
        self.position = -1
        self.update_time = 0
        self.client = client
        self.device = device
        self.status = statics.NOTHING
        self.type = type
        self.is_running = None

    def update_slider(self, new_value):
        xbmc.log("SliderUpdater: update_slider: ", level=xbmc.LOGDEBUG)
        if self.position != new_value:
            # xbmc.log(str(self.position), xbmc.LOGNOTICE)
            # xbmc.log(str(new_value), xbmc.LOGNOTICE)
            self.update_time = time.time()
            self.position = new_value
            self.status = statics.UPDATE

    def set_is_running(self, is_running):
        xbmc.log("SliderUpdater: set_is_running: ", level=xbmc.LOGDEBUG)
        self.is_running = is_running

    def get_status(self):
        xbmc.log("SliderUpdater: get_status: ", level=xbmc.LOGDEBUG)
        return self.status

    def run(self):
        xbmc.log("SliderUpdater: run: ", level=xbmc.LOGDEBUG)
        self.is_running = True
        count = 0
        while self.is_running:
            if self.update_time > 0 and time.time() - self.update_time > 0.4:
                if self.status == statics.UPDATE:
                    if self.type == statics.PERCENT_TYPE and count < 3:
                        success = self.client.move_to_position(self.device.get_device_id(), self.position)
                        if success:
                            self.status = statics.UPDATE_SENT
                            count = 0
                        else:
                            count += 1
                    elif count < 3:
                        success = self.client.move_to_degree(self.device.get_device_id(), self.position)
                        if success:
                            self.status = statics.UPDATE_SENT
                            count = 0
                        else:
                            count += 1
            time.sleep(0.3)
