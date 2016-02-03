import xbmc
from .. import statics
from .. import homepilot_utils


class Action:
    def __init__(self, action):
        xbmc.log("Action: __init__: action: " + str(action), level=xbmc.LOGDEBUG)
        self._did = action[statics.DID]
        self._type = action[statics.TYPE]
        self._name = action[statics.NAME]
        self._description = action[statics.DESCRIPTION]
        self._iconset = action[statics.ICONSET]
        self._iconsetInverted = action[statics.ICONSET_INVERTED]
        self._cmdId = action[statics.CMID]
        if statics.PARAM in action:
            self._param = action[statics.PARAM]
        else:
            self._param = None

    def get_did(self):
        return self._did

    def get_name(self):
        return self._name

    def get_description(self):
        return self._description

    def get_icon(self):
        xbmc.log("Action: get_icon: _cmdId" + repr(self._cmdId), level=xbmc.LOGDEBUG)
        if self._cmdId == 666:
            return homepilot_utils.get_action_sensor_icon()
        elif self._param is not None:
            return homepilot_utils.get_icon(self._iconset, self._iconsetInverted, self._param, type)
        elif self._cmdId == 10 or self._cmdId == 2:
            return homepilot_utils.get_icon(self._iconset, self._iconsetInverted, 100, type)
        else:
            return homepilot_utils.get_icon(self._iconset, self._iconsetInverted, 0, type)

    def get_cmdId(self):
        return self._cmdId

    def get_device_group(self):
        return self._type

    def get_param(self):
        return self._param
