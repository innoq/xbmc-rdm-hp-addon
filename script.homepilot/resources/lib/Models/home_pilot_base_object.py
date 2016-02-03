import xbmc
from .. import statics
from .. import homepilot_utils


class HomePilotBaseObject:
    """
    class which represents a single device
    """

    def __init__(self, device):
        """
        constructor of the class
        Arguments:
        device -- dictionary with the device attributes
        """
        self.device = device
        self.name = device[statics.NAME]
        self.descriprion = device[statics.DESCRIPTION]
        self.did = device[statics.DID]
        self.position = device[statics.POSITION]
        self.deviceGroup = device[statics.DEVICE_GROUP]
        self.status = device[statics.POSITION]
        self.sync = device[statics.SYNC]
        self.icon_set = device[statics.ICONSETKEY]
        self.icon_set_inverted = device.get(statics.ICON_SET_INVERTED)

    def get_name(self):
        """
        returns the device name
        """
        return self.name

    def get_device_id(self):
        """
        return the device id
        """
        return self.did

    def get_position(self):
        """
        gets the current position of the device on a scale from 0 to 100
        """
        return self.position

    def get_devicegroup(self):
        """
        returns the devicegroup the device belongs to
        Schalter:1,	Sensoren:3, Rollos:2, Thermostate:5, Dimmer:4, Tore:8
        """
        return self.deviceGroup

    def get_status(self):
        """
        returns the current status
        """
        return self.status

    def get_description(self):
        return self.descriprion

    def get_sync(self):
        return self.sync

    def get_iconset_inverted(self):
        return homepilot_utils.get_iconset_inverted(self.icon_set_inverted)

    def get_icon(self):
        icon = homepilot_utils.get_icon(self.icon_set, self.icon_set_inverted, self.position, self.deviceGroup)
        xbmc.log("HomePilotBaseObject: get_icon: icon: " + repr(icon), level=xbmc.LOGDEBUG)
        return icon

    def get_display_value(self):
        position = self.get_position()
        group = self.get_devicegroup()
        return homepilot_utils.get_display_value(position, group)
