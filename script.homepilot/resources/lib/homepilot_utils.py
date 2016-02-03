#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import xbmcgui
import xbmc
import xbmcaddon
import statics

__addon__ = xbmcaddon.Addon(id='script.homepilot')
__addon_path__ = __addon__.getAddonInfo('path').decode("utf-8")
_automation_images = os.path.join(__addon_path__, 'resources', 'skins', 'Default', 'media', 'automations')
_images = os.path.join(__addon_path__, 'resources', 'skins', 'Default', 'media')
icons_automation = {"generic": "global_sensor_12_", "wind": "wind_12_", "trigger": "trigger_12_",
                    "closingContact": "schliesskontakt_12_", "dusk": "mond_12_", "dawn": "morgendaemmerung_12_",
                    "time": "uhr_12_", "smoke": "rauchmelder_12_", "sun": "sonne_12_", "temperature": "temperatur_12_",
                    "manual": "global_sensor_12_", "dust": "global_sensor_12_", "favored": "favorite_status_12_",
                    "smartphone": "global_sensor_12_", "motion": "bewegungsmelder_12_",
                    "temperator": "global_sensor_12_", "warning": "warning_12_", "rain": "regen_12_"}


def get_display_value(position, group):
    xbmc.log("homepilot_utils: get_display_value: ", level=xbmc.LOGDEBUG)
    if group == 1:
        if position < 50:
            return "Aus"
        else:
            return "An"
    elif group == 3:
        return ""
    elif group == 4 or group == 8 or group == 2:
        return str(position) + " %"
    elif group == 5:
        return str(float(position) / 10) + " °C"
    else:
        return str(position)


def get_iconset_inverted(_icon_set_inverted):
    xbmc.log("homepilot_utils: get_iconset_inverted: ", level=xbmc.LOGDEBUG)
    return _icon_set_inverted is not None and _icon_set_inverted != 0


def get_icon(_icon_set, _icon_set_inverted, _position, _deviceGroup):
    xbmc.log("homepilot_utils: get_icon: ", level=xbmc.LOGDEBUG)
    if _icon_set in statics.icons:
        base_icon = statics.icons[_icon_set]
        # An-/Aus-Icons
        position = _position
        if _deviceGroup == 5:
            position = (float(position) / 10 - 3) * 4
        an_aus = {"iconset1", "iconset23", "iconset5", "iconset24", "iconset18", "iconset17", "iconset16", "iconset26",
                  "iconset27", "iconset25", "iconset10", "iconset12", "iconset32", "iconset33", "iconset34",
                  "iconset37", "iconset38", "iconset39"}
        if _icon_set in an_aus:
            if get_iconset_inverted(_icon_set_inverted):
                return __get_icon_switch_inverted(position, base_icon)
            else:
                return __get_icon_switch(position, base_icon)

        elif _icon_set == "iconset35":
            return "handsender_72_0.png"
        else:
            if get_iconset_inverted(_icon_set_inverted):
                return __get_icon_percent_inverted(position, base_icon)
            else:
                return __get_icon_percent(position, base_icon)
    else:
        return "logo-homepilot-klein.png"


def __get_icon_switch(position, base_icon):
    xbmc.log("homepilot_utils: __get_icon_switch: ", level=xbmc.LOGDEBUG)
    if position == 0:
        return base_icon + "0.png"
    else:
        return base_icon + "1.png"


def __get_icon_switch_inverted(position, base_icon):
    xbmc.log("homepilot_utils: __get_icon_switch_inverted: ", level=xbmc.LOGDEBUG)
    if position == 0:
        return base_icon + "1.png"
    else:
        return base_icon + "0.png"


def __get_icon_percent(position, base_icon):
    xbmc.log("homepilot_utils: __get_icon_percent: ", level=xbmc.LOGDEBUG)
    if position < 12:
        return base_icon + "0.png"
    elif position < 37:
        return base_icon + "25.png"
    elif position < 62:
        return base_icon + "50.png"
    elif position < 87:
        return base_icon + "75.png"
    else:
        return base_icon + "100.png"


def __get_icon_percent_inverted(position, base_icon):
    xbmc.log("homepilot_utils: __get_icon_percent_inverted: ", level=xbmc.LOGDEBUG)
    if position < 12:
        return base_icon + "100.png"
    elif position < 37:
        return base_icon + "75.png"
    elif position < 62:
        return base_icon + "50.png"
    elif position < 87:
        return base_icon + "25.png"
    else:
        return base_icon + "0.png"


def add_scene_to_automation_list(automation_list, automations, addon):
    xbmc.log("homepilot_utils: add_scene_to_automation_list: automation_list: " + repr(automation_list),
             level=xbmc.LOGDEBUG)
    for prop in automations.get_props():
        _add_scene_item(str(prop), automations.get_props()[prop], automation_list, addon)
    automation_list.setVisible(True)


def get_action_sensor_icon():
    xbmc.log("homepilot_utils: get_action_sensor_icon: ", level=xbmc.LOGDEBUG)
    return os.path.join(_images, "action_sensor.png")


def _add_scene_item(automation_type, value, automation_list, addon):
    xbmc.log("homepilot_utils: _add_scene_item: ", level=xbmc.LOGDEBUG)
    if value == 1 or value == 2 or value == 0 or value == 4:
        label = _get_label_scene(automation_type, value, addon)
        item = xbmcgui.ListItem(label=label)
        image = os.path.join(_automation_images, icons_automation[automation_type] + str(value) + ".png")
        item.setIconImage(image)
        automation_list.addItem(item)
    else:
        return None


def _get_label_scene(type, val, addon):
    xbmc.log("homepilot_utils: _get_label_scene: ", level=xbmc.LOGDEBUG)
    if val != 1 and val != 2 and val != 4 and val != 0:
        return "-"
    value = str(val)
    labels = {statics.DUSK: int(str(3222) + value),
              statics.DAWN: int(str(3221) + value),
              statics.TIME: int(str(3220) + value),
              statics.DUST: int(str(3223) + value),
              statics.SUN: int(str(3224) + value),
              statics.FAVORED: int(str(3225) + value),
              statics.WIND: int(str(3227) + value),
              statics.MANUAL: int(str(3226) + value),
              statics.RAIN: int(str(3228) + value),
              statics.TRIGGER: int(str(3229) + value),
              statics.GENERIC: int(str(3230) + value),
              statics.TEMPERATOR: int(str(3231) + value),
              statics.TEMPERATUR: int(str(3232) + value),
              statics.MOTION: int(str(3233) + value),
              statics.SMOKE: int(str(3234) + value),
              statics.CLOSINGCONTACT: int(str(3235) + value),
              statics.WARNING: int(str(3236) + value)}
    if type in labels:
        return addon.getLocalizedString(labels[type])
    else:
        xbmc.log("homepilot_utils: _get_label_scene: Label nicht gefunden!", level=xbmc.LOGERROR)
        return "-"


def add_device_to_automation_list(automation_list, automations, addon):
    xbmc.log("homepilot_utils: add_device_to_automation_list: ", level=xbmc.LOGDEBUG)
    for prop in automations.get_props():
        _add_device_item(str(prop), automations.get_props()[prop], automation_list, addon)
    automation_list.setVisible(True)


def _add_device_item(automation_type, value, automation_list, addon):
    xbmc.log("homepilot_utils: _add_device_item: ", level=xbmc.LOGDEBUG)
    if value == 1 or value == 2 or value == 0 or value == 4:
        label = _get_label_device(automation_type, value, addon)
        item = xbmcgui.ListItem(label=label)
        image = os.path.join(_automation_images, icons_automation[automation_type] + str(value) + ".png")
        item.setIconImage(image)
        automation_list.addItem(item)
    else:
        return None


def _get_label_device(type, val, addon):
    xbmc.log("homepilot_utils: _get_label_device: ", level=xbmc.LOGDEBUG)
    if val != 1 and val != 2 and val != 4 and val != 0:
        return "-"
    value = str(val)
    labels = {statics.DUSK: int(str(3205) + value),
              statics.DAWN: int(str(3204) + value),
              statics.TIME: int(str(3203) + value),
              statics.DUST: int(str(3206) + value),
              statics.SUN: int(str(3207) + value),
              statics.FAVORED: int(str(3208) + value),
              statics.WIND: int(str(3210) + value),
              statics.MANUAL: int(str(3209) + value),
              statics.RAIN: int(str(3211) + value),
              statics.TRIGGER: int(str(3212) + value),
              statics.GENERIC: int(str(3213) + value),
              statics.TEMPERATOR: int(str(3214) + value),
              statics.TEMPERATUR: int(str(3215) + value),
              statics.MOTION: int(str(3216) + value),
              statics.SMOKE: int(str(3217) + value),
              statics.CLOSINGCONTACT: int(str(3218) + value),
              statics.WARNING: int(str(3219) + value)}
    if type in labels:
        return addon.getLocalizedString(labels[type])
    else:
        xbmc.log("homepilot_utils: _get_label_device: Label nicht gefunden!", level=xbmc.LOGERROR)
        return "-"


def get_title_control(text_or_id, addon):
    '''
    use this method to make sure view titles are everywhere on the same position
    '''
    xbmc.log("homepilot_utils: get_title_control: text_or_id:" + repr(text_or_id), level=xbmc.LOGDEBUG)
    if isinstance(text_or_id, int):
        label = addon.getLocalizedString(text_or_id)
    else:
        label = text_or_id
    if xbmc.skinHasImage('settings/slider_back.png'):
        control = xbmcgui.ControlLabel(330, 65, 600, 75, label, font="Font_Reg22")
    else:
        control = xbmcgui.ControlLabel(400, 50, 600, 75, label, font="font16")
    return control
