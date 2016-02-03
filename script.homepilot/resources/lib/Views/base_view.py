#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xbmc
import os
import xbmcaddon

__addon__ = xbmcaddon.Addon(id='script.homepilot')
__addon_path__ = __addon__.getAddonInfo('path').decode("utf-8")
images_device = os.path.join(__addon_path__, 'resources', 'skins', 'Default', 'media', 'devices')
_images = os.path.join(__addon_path__, 'resources', 'skins', 'Default', 'media')

schalter_img = os.path.join(images_device, 'steckdose_72_0.png')
rollo_img = os.path.join(images_device, 'rollladen2_72_50.png')
dimmer_img = os.path.join(images_device, 'birne1_72_100.png')
thermostat_img = os.path.join(images_device, 'thermostat_72_100.png')
tore_img = os.path.join(images_device, 'garage_72_50.png')
logo_img = os.path.join(_images, 'logo-homepilot-klein.png')
szene_img = os.path.join(_images, 'szene_32.png')
szene_img_deact = os.path.join(_images, 'szene_32_deactivated.png')
scene_manual = os.path.join(_images, 'scene_manual2.png')
scene_non_manual = os.path.join(_images, 'scene_no_manual2.png')


class BaseView:
    def __init__(self):
        xbmc.log("BaseView: __init__", level=xbmc.LOGDEBUG)

    def get_communication_error_label(self):
        return __addon__.getLocalizedString(32381)
