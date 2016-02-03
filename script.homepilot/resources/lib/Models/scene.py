import xbmc
from .. import statics
import automation
import action


class Scene:
    def __init__(self, scene):
        self._sid = scene[statics.SID]
        self._name = scene[statics.NAME]
        self._description = scene[statics.DESCRIPTION]
        self._is_executable = scene[statics.IS_EXECUTABLE]
        self._sync = scene[statics.SYNC]
        self._groups = scene[statics.GROUPS]
        if 'actions' in scene:
            self._actions = scene[statics.ACTIONS]
        self._properties = scene[statics.PROPERTIES]
        self._is_active = scene[statics.IS_ACTIVE]
        self._favored = scene[statics.FAVORED_ID]

    def get_id(self):
        return self._sid

    def get_name(self):
        return self._name

    def get_actions_as_list(self):
        xbmc.log("Scene: get_actions_as_list: ", level=xbmc.LOGDEBUG)
        return map(lambda x: action.Action(x), self._actions)

    def get_automationen(self):
        return automation.Automation(self._properties)

    def is_executable(self):
        return self._is_executable == 1

    def is_active(self):
        return self._is_active == 1

    def is_favored(self):
        return self._favored > 0

    def get_sync(self):
        return self._sync

    def get_description(self):
        return self._description

    def set_favored(self):
        xbmc.log("Scene: set_favored: ", level=xbmc.LOGDEBUG)
        self._favored = 1

    def set_unfavored(self):
        xbmc.log("Scene: set_unfavored: ", level=xbmc.LOGDEBUG)
        self._favored = 0

    def set_activ(self):
        xbmc.log("Scene: set_activ: ", level=xbmc.LOGDEBUG)
        self._is_active = 1

    def set_inactive(self):
        xbmc.log("Scene: set_inactive: ", level=xbmc.LOGDEBUG)
        self._is_active = 0
