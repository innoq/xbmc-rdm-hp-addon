import xbmc
from .. import statics
import automation
import home_pilot_base_object


class Device(home_pilot_base_object.HomePilotBaseObject):
    def __init__(self, device):
        home_pilot_base_object.HomePilotBaseObject.__init__(self, device)
        self.device = device
        self._available = device[statics.AVAIL]
        self._hasErrors = device[statics.HAS_ERRORS] != 0
        self._groups = device[statics.GROUPS]
        self._favoredId = device[statics.FAVORED_ID]
        self._automated = device[statics.AUTOMATED] != 0
        self._properties = device[statics.PROPERTIES]

    def has_errors(self):
        """
        returns if the device has errors
        """
        return self._hasErrors

    def is_available(self):
        """
        returns if the device is available
        """
        return self._available

    def get_favoredId (self):
        return self._favoredId

    def get_icon(self):
        icon = home_pilot_base_object.HomePilotBaseObject.get_icon(self)
        # xbmc.log("device: get_automation: get_icon" + repr(icon) +
        #         "\nis_available:" + repr(self.is_available()) +
        #         "\nhas_errors" + repr(self.has_errors()), level=xbmc.LOGDEBUG)
        if self.is_available() is False or self.has_errors():
            icon = "warnung_72.png"
        return icon

    def is_automated(self):
        return self._automated

    def get_automationen(self):
        xbmc.log("device: get_automation: properties" + str(self._properties), level=xbmc.LOGDEBUG)
        return automation.Automation(self._properties)

    def is_favored(self):
        return self._favoredId != -1
