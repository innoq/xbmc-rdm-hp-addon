import xbmc
from .. import statics


class Automation:
    def __init__(self, properties):
        xbmc.log("Automation: __init__: properties: " + str(properties), level=xbmc.LOGDEBUG)
        self.properties = properties

    def get_dawn(self):
        return self.properties[statics.DAWN]

    def get_dusk(self):
        return self.properties[statics.DUSK]

    def get_time(self):
        return self.properties[statics.TIME]

    def get_wind(self):
        return self.properties[statics.WIND]

    def get_temperature(self):
        return self.properties[statics.TEMPERATUR]

    def get_generic(self):
        return self.properties[statics.GENERIC]

    def get_trigger(self):
        return self.properties[statics.TRIGGER]

    def get_closing_contact(self):
        return self.properties[statics.CLOSINGCONTACT]

    def get_smoke(self):
        return self.properties[statics.SMOKE]

    def get_sun(self):
        return self.properties[statics.SUN]

    def get_manual(self):
        return self.properties[statics.MANUAL]

    def get_dust(self):
        return self.properties[statics.DUST]

    def get_favored(self):
        return self.properties[statics.FAVORED]

    def get_smartphone(self):
        return self.properties[statics.SMARTPHONE]

    def get_motion(self):
        return self.properties[statics.MOTION]

    def get_temperator(self):
        return self.properties[statics.TEMPERATOR]

    def get_warning(self):
        return self.properties[statics.WARNING]

    def get_rain(self):
        return self.properties[statics.RAIN]

    def get_props(self):
        return self.properties
