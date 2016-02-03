import home_pilot_base_object
import xbmc


class Meter(home_pilot_base_object.HomePilotBaseObject):
    def __init__(self, device, data):
        """
        constructor of the class

        Arguments:

        meter -- dictionary with the sensor attributes
        """
        home_pilot_base_object.HomePilotBaseObject.__init__(self, device)
        xbmc.log("Meter: __init__: device: " + str(device), level=xbmc.LOGDEBUG)
        self._data = data

    def get_data(self):
        return self._data
