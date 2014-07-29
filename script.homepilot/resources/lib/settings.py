


class SettingsDialogManager (object):

    def get_ip_address (self, addon):
        ip_address = addon.getSetting("homepilot_ip")
        ip_set = addon.getSetting("homepilot_ip_set")
        if not ip_address or not ip_set: 
            addon.openSettings()
            ip_address = addon.getSetting("homepilot_ip")
            addon.setSetting("homepilot_ip_set", "true")
        return ip_address

    def update_ip_address(self, addon):
        addon.openSettings()
        addon.setSetting("homepilot_ip_set", "true")
