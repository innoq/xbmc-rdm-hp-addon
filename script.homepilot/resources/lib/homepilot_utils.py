#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import xbmcgui
import xbmc
import xbmcaddon

FAVORITEN = 32004
SENSOREN = 32007
SZENEN = 32005
SZENENTYPEN = 32016
GRUPPEN = 32015

ROLLADEN = 32010
SCHALTER = 32011
DIMMER = 32012
THERMOSTATE = 32013
TORE = 32014
ALLE = 32002

SZENEN_MANUELL = 32017
SZENEN_NICHT_MANUELL = 32018
SZENEN_ALLE = 32020


icons = {}
icons["iconset1"] = "aquarium_72_"
icons["iconset22"] = "bargraph_horizontal_72_"
icons["iconset2"] = "bargraph_vertikal_72_"
icons["iconset23"] = "bewegungsmelder_72_"
icons["iconset4"] = "deckenlampe_72_"
icons["iconset5"] = "ein_aus_schalter1_72_"
icons["iconset24"] = "fenster_72_"
icons["iconset18"] = "gartensprenkler_72_"
icons["iconset21"] = "birne1_72_"
icons["iconset6"] = "jalousie_72_"
icons["iconset17"] = "kaffeemaschine_72_"
icons["iconset32"] = "lichterkette_72"
icons["iconset7"] = "markise_72_"
icons["iconset16"] = "pumpe_72_"
icons["iconset26"] = "rauchmelder_72_"
icons["iconset8"] = "rollladen1_72_"
icons["iconset15"] = "rollladen2_72_"
icons["iconset9"] = "schiebetuer_72_"
icons["iconset14"] = "schiebeladen_72_"
icons["iconset27"] = "schliesskontakt_72_"
icons["iconset30"] = "garage_72_"
icons["iconset31"] = "sektionaltor_72_"
icons["iconset25"] = "genericsensor_72_"
#icons["iconset19"]      -> Standard
icons["iconset10"] = "steckdose_72_"
icons["iconset13"] = "stehlampe_72_"
icons["iconset20"] = "sunscreen_72_"
icons["iconset28"] = "thermostat_72_"
icons["iconset11"] = "tischlampe_72_"
icons["iconset12"] = "tuer_72_"
icons["iconset33"] = "weihnachtsbaum_72_"
icons["iconset34"] = "dachfenster_72_"
icons["iconset35"] = "handsender_72_"
icons["iconset36"] = "leinwand_72_"
icons["iconset37"] = "radio_72_"
icons["iconset38"] = "smartphone_72_"
icons["iconset39"] = "ventilator_72_"

def get_display_value(position, group):
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
        return str(float(position)/10) + " °C"
    else:
        return str(position)

def get_iconset_inverted(_icon_set_inverted):
    return _icon_set_inverted is not None and _icon_set_inverted != 0


def get_icon(_icon_set, _icon_set_inverted, _position, _deviceGroup):
    if _icon_set in icons:
        base_icon = icons[_icon_set]
        #An-/Aus-Icons
        position = _position
        if _deviceGroup == 5:
            position = (float(position)/10 - 3) * 4
        an_aus = set(
            ["iconset1", "iconset23", "iconset5", "iconset24", "iconset18", "iconset17", "iconset16", "iconset26",
             "iconset27", "iconset25", "iconset10", "iconset12", "iconset32", "iconset33", "iconset34",
             "iconset37", "iconset38", "iconset39"])
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
    if position == 0:
        return base_icon + "0.png"
    else:
        return base_icon + "1.png"


def __get_icon_switch_inverted(position, base_icon):
    if position != 0:
        return base_icon + "1.png"
    else:
        return base_icon + "0.png"


def __get_icon_percent(position, base_icon):
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

__addon__ = xbmcaddon.Addon(id='script.homepilot')
__addon_path__        = __addon__.getAddonInfo('path').decode("utf-8")
_automation_images = os.path.join(__addon_path__, 'resources', 'skins', 'Default', 'media', 'automations')
icons_automation = {}
icons_automation["generic"] = "global_sensor_12_"
icons_automation["wind"] = "wind_12_"
icons_automation["trigger"] = "trigger_12_"
icons_automation["closingContact"] = "schliesskontakt_12_"
icons_automation["dusk"] = "mond_12_"
icons_automation["dawn"] = "morgendaemmerung_12_"
icons_automation["time"] = "uhr_12_"
icons_automation["smoke"] = "rauchmelder_12_"
icons_automation["sun"] = "sonne_12_"
icons_automation["temperature"] = "temperatur_12_"
# TODO
icons_automation["manual"] = "global_sensor_12_"
# TODO
icons_automation["dust"] = "global_sensor_12_"
icons_automation["favored"] = "favorite_status_12_"
# TODO
icons_automation["smartphone"] = "global_sensor_12_"
icons_automation["motion"] = "bewegungsmelder_12_"
# TODO
icons_automation["temperator"] = "global_sensor_12_"
icons_automation["warning"] = "warning_12_"
icons_automation["rain"] = "regen_12_"

def add_items_to_automation_list(automation_list, automations):
        dusk = automations.get_dusk()
        _add_list_item("dusk", dusk, automation_list)

        dawn = automations.get_dawn()
        _add_list_item("dawn", dawn, automation_list)

        time = automations.get_time()
        _add_list_item("time", time, automation_list)

        generic = automations.get_generic()
        _add_list_item("generic", generic, automation_list)

        wind = automations.get_wind()
        _add_list_item("wind", wind, automation_list)

        trigger = automations.get_trigger()
        _add_list_item("trigger", trigger, automation_list)

        closingContact = automations.get_closing_contact()
        _add_list_item("closingContact", closingContact, automation_list)

        dust = automations.get_dust()
        _add_list_item("dust", dust, automation_list)

        smoke = automations.get_smoke()
        _add_list_item("smoke", smoke, automation_list)

        sun = automations.get_sun()
        _add_list_item("sun", sun, automation_list)

        temperature = automations.get_temperature()
        _add_list_item("temperature", temperature, automation_list)

        manual = automations.get_manual()
        _add_list_item("manual", manual, automation_list)

        favored = automations.get_favored()
        _add_list_item("favored", favored, automation_list)

        smartphone = automations.get_smartphone()
        _add_list_item("smartphone", smartphone, automation_list)

        motion = automations.get_motion()
        _add_list_item("motion", motion, automation_list)

        temperator = automations.get_temperator()
        _add_list_item("temperator", temperator, automation_list)

        warning = automations.get_warning()
        _add_list_item("warning", warning, automation_list)

        rain = automations.get_rain()
        _add_list_item("rain", rain, automation_list)

        automation_list.setVisible(True)
        xbmc.log("visualize automations " + str(automation_list.size()), level=xbmc.LOGNOTICE)


def _add_list_item(automation_type, value, automation_list):
    if value == 1 or value == 2 or value == 0 or value == 3:
        label = _get_label_device(automation_type, value)
        item = xbmcgui.ListItem(label=label)
        image = os.path.join(_automation_images, icons_automation[automation_type] + str(value) + ".png")
        item.setIconImage(image)
        automation_list.addItem(item)
    else:
        return None

def _get_label_device(type, value):
    if value != 1 and value != 2:
        return "<Dummy-Text>"
    if type == "dusk":
        return "Die Abenddämmerungsautomatik " + _get_automation_text_device(value) + ", wenn es dunkel wird."
    elif type == "dawn":
        return "Die Morgendämmerungsautomatik " + _get_automation_text_device(value) + ", wenn es hell wird."
    elif type == "time":
        return "Die Zeitautomatik " + _get_automation_text_device(value) + " auf Zeitbefehle."
    else:
        return "<Dummy-Text>"

def _get_label_scene(type, value):
    if value != 1 and value != 2:
        return "<Dummy-Text>"
    if type == "dusk":
        return "Die Abenddämmerungsautomatik " + _get_automation_text_scene(value) + ", wenn es dunkel wird."
    elif type == "dawn":
        return "Die Morgendämmerungsautomatik " + _get_automation_text_scene(value) + ", wenn es hell wird."
    elif type == "time":
        return "Die Szene ist " + _get_automation_text_scene(value) + " auf eingestellte Zeit-Automationen."
    else:
        return "<Dummy-Text>"

def _get_automation_text_device(status):
    if status == 1:
        return "des Gerätes ist deaktiviert. Es reagiert nicht"
    elif status == 2:
        return "des Gerätes ist aktiviert. Es reagiert"

def _get_automation_text_scene(status):
    if status == 1:
        return "deaktiviert und reagiert nicht"
    elif status == 2:
        return "aktiviert und reagiert"