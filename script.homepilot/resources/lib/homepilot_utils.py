#!/usr/bin/env python
# -*- coding: utf-8 -*-

FAVORITEN = "Favoriten"
SENSOREN = "Sensoren"
SZENEN = "Szenen"

ROLLADEN = "Rollläden"
SCHALTER = "Schalter"
DIMMER = "Dimmer"
THERMOSTATE = "Thermostate"
TORE = "Tore"
ALLE = "Alle Geräte"

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
