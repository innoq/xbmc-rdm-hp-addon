import xbmc
from .. import statics


class Group:
    def __init__(self, group):
        self.group = group
        self._name = group[statics.NAME]
        self._description = group[statics.DESCRIPTION]
        self._gid = group[statics.GID]
        xbmc.log("Group: __init__: group: name: " + repr(self._name) +
                 "\ngid: " + repr(self._gid), level=xbmc.LOGDEBUG)

    def get_group_id(self):
        return self._gid

    def get_name(self):
        return self._name

    def get_description(self):
        return self._description
