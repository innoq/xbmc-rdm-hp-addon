#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xbmcgui
import xbmc
import os
import xbmcaddon
__addon__ = xbmcaddon.Addon(id='script.homepilot')
__addon_path__ = __addon__.getAddonInfo('path').decode("utf-8")
_images_device = os.path.join(__addon_path__, 'resources', 'skins', 'Default', 'media', 'devices')
_images = os.path.join(__addon_path__, 'resources', 'skins', 'Default', 'media')

from homepilot_utils import ROLLADEN, SCHALTER, DIMMER, THERMOSTATE, TORE, SZENEN_MANUELL, SZENEN_NICHT_MANUELL, \
    SZENEN_ALLE, SZENENTYPEN, SENSOREN, FAVORITEN, FAVORITEN_LOKAL, ALLE, GRUPPEN, SZENEN_DETAILS
import homepilot_utils
import local_favorites

device_types = {}
device_types[SCHALTER] = 1
device_types[ROLLADEN] = 2
device_types[SENSOREN] = 3
device_types[DIMMER] = 4
device_types[THERMOSTATE] = 5
device_types[TORE] = 8


MESSAGE_SETTINGS_DIALOG = __addon__.getLocalizedString(32384)


class BaseView:

    def get_title_control(self, text_or_id, addon):
        '''
        use this method to make sure view titles are everywhere on the same position
        '''
        xbmc.log("label: " + str(text_or_id), level=xbmc.LOGNOTICE)
        if isinstance(text_or_id, int):
            label = addon.getLocalizedString(text_or_id)
        else:
            label = text_or_id
        if xbmc.skinHasImage('settings/slider_back.png'):
            control = xbmcgui.ControlLabel(330, 65, 600, 75, label, font="Font_Reg22")
        else:
            control = xbmcgui.ControlLabel(400, 50, 600, 75, label, font="font16")
        return control


    def get_communication_error_label():
        return __addon__.getLocalizedString(32381)


class ParametrizedGeraeteView(BaseView):

    def __init__(self, home_pilot_client, device_type, group=None):
        self.client = home_pilot_client
        self.total = 0
        self.controldict = {}
        self.type = device_type
        self.list_item_dict = {}
        self.hp_error = False
        self.errorcontrol = None
        self.group = group

    def get_id(self):
        return str(self.type) + "_view"

    def get_group(self):
        return self.group

    def visualize(self, window, addon, title=None):
        xbmc.log("visualize gerateview: " + str(self.type), level=xbmc.LOGNOTICE)
        if title is None:
            self.title_control = self.get_title_control(self.type, addon)
        else:
            self.title_control = self.get_title_control(title, addon)
        window.addControl(self.title_control)
        if not hasattr(self, "gerate_group_control"):
            self.gerate_group_control = window.getControl(252)
            window.setProperty('GeraeteScrollHeight', '480')
        homepilot_is_reachable = self.client.ping()
        if not homepilot_is_reachable:
            self.hp_error = True
            errorlabel = self.get_communication_error_label()
            self.errorcontrol = xbmcgui.ControlLabel(400, 250, 600, 75, errorlabel)
            window.addControl(self.errorcontrol)
        else:
            self.hp_error = False
            self.__visualize_devices(window, addon)


    def __visualize_devices(self, window, addon):
        try:
            devices = self.__get_devices()
            if len(devices) > 0:
                self.geraete_list = window.getControl(5)
                if self.type == SENSOREN or self.type == FAVORITEN or self.type == FAVORITEN_LOKAL:
                    self.geraete_list.controlLeft(self.__get_menu_control(window))
                else:
                    #set a fake control to prevent xbmc from setting it back to the main menu
                    control = window.getControl(111)
                    self.geraete_list.controlLeft(control)
                self.geraete_list.reset()
                self.__add_listitems(devices)
                self.gerate_group_control.setPosition(350,100)
                self.gerate_group_control.setVisible(True)
                if self.type != FAVORITEN and self.type != FAVORITEN_LOKAL and self.type != SENSOREN:
                    window.setFocus(self.geraete_list)
            else:
                pass
                errorlabel = ""
                #self.hp_error = True
                #if self.type == SENSOREN:
                #    errorlabel = unicode("<keine Sensoren vorhanden>", "utf-8")
                #elif self.type == FAVORITEN_LOKAL or self.type == FAVORITEN:
                #    errorlabel = unicode("<keine Favoriten vorhanden>", "utf-8")
                #else:
                #    errorlabel = unicode("<keine Geräte vorhanden>", "utf-8")
                #self.errorcontrol = xbmcgui.ControlLabel(400, 250, 600, 75, errorlabel)
                #window.addControl(self.errorcontrol)
        except Exception as inst:
            self.hp_error = True
            errorlabel = self.get_communication_error_label()
            self.errorcontrol = xbmcgui.ControlLabel(400, 250, 600, 75, errorlabel)
            window.addControl(self.errorcontrol)
            xbmc.log(str(inst), level=xbmc.LOGWARNING)

    def __get_menu_control(self, window):
        if self.type == FAVORITEN or self.type == FAVORITEN_LOKAL:
            return window.getControl(95)
        elif self.type == SENSOREN:
            return window.getControl(97)
        else:
            return window.getControl(96)

    def __add_listitems(self, devices):
        for device in devices:
            if self.type == SENSOREN:
                item = xbmcgui.ListItem(label=device.get_name())
            else:
                item = xbmcgui.ListItem(label=device.get_name(), label2=device.get_display_value())
            icon_name = device.get_icon()
            item.setIconImage(os.path.join(_images_device, icon_name))
            item.setProperty("description", device.get_description())
            item.setProperty("did", str(device.get_device_id()))
            item.setProperty("sync", str(device.get_sync()))
            self.list_item_dict[device.get_device_id()] = item
            self.geraete_list.addItem(item)

    def __get_devices(self):
        if self.type == FAVORITEN:
            devices = self.client.get_favorite_devices()
        elif self.type == FAVORITEN_LOKAL:
            xbmc.log("get local devices ", level=xbmc.LOGNOTICE)
            devices = self.__get_local_favorit_devices()
        elif self.type == ALLE:
            devices = self.client.get_devices()
        elif self.type == SENSOREN:
            devices = self.client.get_meters()
        elif self.type == GRUPPEN:
            devices = self.client.get_devices_by_group(self.group)
        else:
            devices = self.client.get_devices_by_device_group(device_types[self.type])
        return devices

    def __get_local_favorit_devices(self):
        device_ids = local_favorites.get_devices_as_set()
        all_devices = self.client.get_devices()
        favorite_devices = []
        for device in all_devices:
            if device.get_device_id() in device_ids:
                favorite_devices.append(device)
        return favorite_devices

    def remove_everything(self, window):
        if self.hp_error and self.errorcontrol is not None:
            window.removeControls([self.errorcontrol, self.title_control])
            self.errorcontrol = None
        else:
            controls_to_remove = [self.title_control]
            window.removeControls(controls_to_remove)
        self.gerate_group_control.setVisible(False)

    def update(self, window, addon, menuControl):
        try:
            new_devices = self.__get_devices()
            if self.hp_error:
                self.remove_everything(window)
                self.visualize(window, addon)
            else:
                list_item_ids = self.list_item_dict.keys()
                for new_device in new_devices:
                    new_sync_value = str(new_device.get_sync())
                    device_listitem = self.list_item_dict.get(new_device.get_device_id())
                    if device_listitem is not None:
                        list_item_ids.remove(new_device.get_device_id())
                        old_sync_value = device_listitem.getProperty("sync")
                        old_status = device_listitem.getLabel2()
                        new_status = new_device.get_display_value()
                        if new_sync_value != old_sync_value or old_status != new_status:
                            new_icon = new_device.get_icon()
                            if old_status != new_status:
                                device_listitem.setLabel2(new_status)
                                device_listitem.setIconImage(os.path.join(_images_device, new_icon))
                            else:
                                device_listitem.setIconImage(os.path.join(_images_device, new_icon))
                            old_label = device_listitem.getLabel()
                            new_label = new_device.get_name()
                            if old_label != new_label.encode('utf8'):
                                device_listitem.setLabel(new_label)
                            old_label2 = device_listitem.getProperty("description")
                            new_label2 = new_device.get_description()
                            if old_label2 != new_label2.encode('utf8'):
                                device_listitem.setProperty("description", new_label2)

                    else:
                        #add new listitem
                        self.__add_listitems([new_device])
                #remove items from list when devices are no longer present
                #workaround implementation as the ControlList.removeItem didn't work
                if len(list_item_ids) > 0:
                    self.list_item_dict = {}
                    self.geraete_list.reset()
                    self.__add_listitems(new_devices)
            self.hp_error = False
        except Exception, e:
            xbmc.log("Problem beim Updaten des views: " + str(self.type) + "  " + str(e), level=xbmc.LOGWARNING)
            self.remove_everything(window)
            self.visualize(window, addon)
            self.hp_error = True

    def _get_list_item_position(self, item):
        for i in range(0, self.geraete_list.size()):
            if self.geraete_list.getListItem(i) == item:
                return i
        return -1


schalter_img = os.path.join(_images_device, 'steckdose_72_0.png')
rollo_img = os.path.join(_images_device, 'rollladen2_72_50.png')
dimmer_img = os.path.join(_images_device, 'birne1_72_100.png')
thermostat_img = os.path.join(_images_device, 'thermostat_72_100.png')
tore_img = os.path.join(_images_device, 'garage_72_50.png')
logo_img = os.path.join(_images, 'logo-homepilot-klein.png')


class GeraetetypView(BaseView):

    def __init__(self, home_pilot_client):
        self.client = home_pilot_client

    def get_id(self):
        return "geraetetyp_view"

    def remove_everything(self, window):
        window.removeControls([self.geraetelabel_control, self.gruppen_control])
        self.geraetetypen_list.setVisible(False)
        self.gruppen_group_control.setVisible(False)
        if self.errorcontrol is not None:
            window.removeControl(self.errorcontrol)

    def visualize(self, window, addon):
        xbmc.log("visualize geraetetypview: ", level=xbmc.LOGNOTICE)
        self.geraetelabel_control = self.get_title_control(32009, addon)

        self.geraetetypen_list = window.getControl(257)
        self.geraetetypen_list.reset()

        self.rolladen_item = xbmcgui.ListItem(label=addon.getLocalizedString(ROLLADEN))
        self.rolladen_item.setIconImage(rollo_img)
        self.geraetetypen_list.addItem(self.rolladen_item)

        self.schalter_item = xbmcgui.ListItem(label=addon.getLocalizedString(SCHALTER))
        self.schalter_item.setIconImage(schalter_img)
        self.geraetetypen_list.addItem(self.schalter_item)

        self.dimmer_item = xbmcgui.ListItem(label=addon.getLocalizedString(DIMMER))
        self.dimmer_item.setIconImage(dimmer_img)
        self.geraetetypen_list.addItem(self.dimmer_item)

        self.thermostat_item = xbmcgui.ListItem(label=addon.getLocalizedString(THERMOSTATE))
        self.thermostat_item.setIconImage(thermostat_img)
        self.geraetetypen_list.addItem(self.thermostat_item)

        self.tore_item = xbmcgui.ListItem(label=addon.getLocalizedString(TORE))
        self.tore_item.setIconImage(tore_img)
        self.geraetetypen_list.addItem(self.tore_item)

        self.alle_item = xbmcgui.ListItem(label=addon.getLocalizedString(ALLE))
        self.alle_item.setIconImage(logo_img)
        self.geraetetypen_list.addItem(self.alle_item)

        self.geraetetypen_list.setVisible(True)

        label = addon.getLocalizedString(32015)
        self.gruppen_control = xbmcgui.ControlLabel(400, 380, 600, 75, label, font="font16")
        window.addControls([self.geraetelabel_control, self.gruppen_control])

        gruppen_list = window.getControl(4)
        gruppen_list.reset()
        self.gruppen_group_control = window.getControl(251)
        try:
            groups = self.client.get_groups()
            if len(groups) > 0:
                for group in groups:
                    group_item = xbmcgui.ListItem(label=group.get_name())
                    group_item.setProperty("gid", str(group.get_group_id()))
                    gruppen_list.addItem (group_item)

                self.gruppen_group_control.setPosition(350,420)
                self.gruppen_group_control.setVisible(True)
                self.errorcontrol = None
            else:
                errorlabel = addon.getLocalizedString(32380)
                self.errorcontrol = xbmcgui.ControlLabel(450, 450, 600, 75, errorlabel)
                window.addControl(self.errorcontrol)
        except Exception, e:
            xbmc.log(str(e), level=xbmc.LOGWARNING)
            errorlabel = self.get_communication_error_label()
            self.errorcontrol = xbmcgui.ControlLabel(450, 450, 600, 75, errorlabel)
            window.addControl(self.errorcontrol)

    def handle_click(self, position):
        if position == 5:
            return ALLE
        elif position == 0:
            return ROLLADEN
        elif position == 1:
            return SCHALTER
        elif position == 2:
            return DIMMER
        elif position == 3:
            return THERMOSTATE
        elif position == 4:
            return TORE
        pass


szene_img = os.path.join(_images, 'szene_32.png')
szene_img_deact = os.path.join(_images, 'szene_32_deactivated.png')
scene_manual = os.path.join(_images, 'scene_manual2.png')
scene_non_manual = os.path.join(_images, 'scene_no_manual2.png')


class SzenentypView(BaseView):

    def __init__(self):
        pass

    def get_id(self):
        return str(SZENENTYPEN) + "_view"

    def remove_everything(self, window):
        self.geraetetypen_list.setVisible(False)
        window.removeControls([self.title_control])


    def visualize(self, window, addon):
        self.title_control = self.get_title_control(32016, addon)
        window.addControl(self.title_control)
        self.geraetetypen_list = window.getControl(257)
        self.geraetetypen_list.reset()

        self.manuell_item = xbmcgui.ListItem(addon.getLocalizedString(32017))
        self.manuell_item.setIconImage(scene_manual)
        self.geraetetypen_list.addItem(self.manuell_item)

        self.nicht_manuell_item = xbmcgui.ListItem(addon.getLocalizedString(32018))
        self.nicht_manuell_item.setIconImage(scene_non_manual)
        self.geraetetypen_list.addItem(self.nicht_manuell_item)

        self.alle_item = xbmcgui.ListItem(addon.getLocalizedString(32020))
        self.geraetetypen_list.addItem(self.alle_item)

        self.geraetetypen_list.setVisible(True)

        return [self.title_control]

    def handle_click (self, position):
        if position == 0:
            return SZENEN_MANUELL
        elif position == 1:
            return SZENEN_NICHT_MANUELL
        elif position == 2:
            return SZENEN_ALLE
        return ""


class SzenenListView(BaseView):

    def __init__(self, client, type):
        self.type = type
        self.client = client

    def get_id(self):
        return str(self.type) + "_view"

    def remove_everything(self, window):
        window.removeControls([self.title_control])
        scenes_group = window.getControl(260)
        scenes_group.setVisible(False)
        if self.errorcontrol is not None:
            window.removeControl(self.errorcontrol)

    def visualize(self, window, addon):
        self.title_control = self.get_title_control(self.type, addon)
        window.addControl(self.title_control)
        scenes_list = window.getControl(258)
        scenes_list.reset()

        scenes = self.__get_scenes()
        if len(scenes) > 0:
            scenes_group = window.getControl(260)
            scenes_group.setPosition(350, 100)
            scenes_group.setVisible(True)
            for scene in scenes:
                scene_item = xbmcgui.ListItem(label = scene.get_name())
                scene_item.setIconImage(szene_img)
                scene_item.setProperty("sid", str(scene.get_id()))

                scenes_list.addItem(scene_item)
            self.errorcontrol = None
        else:
            errorlabel = addon.getLocalizedString(32380)
            self.errorcontrol = xbmcgui.ControlLabel(450, 150, 600, 75, errorlabel)
            window.addControl(self.errorcontrol)
        scenes_list.setVisible(True)
        return [self.title_control]

    def handle_click (self, control):
        pass

    def __get_scenes(self):
        if self.type == SZENEN_ALLE:
            return self.client.get_scenes()
        elif self.type == SZENEN_MANUELL:
            return self.client.get_manual_scenes()
        elif self.type == SZENEN_NICHT_MANUELL:
            return self.client.get_non_manual_scenes()


class SzenenDetailView(BaseView):

    def __init__(self, client, scene_id, previous_list_position):
        self.client = client
        scene_id = scene_id
        self.scene = client.get_scene_by_id(scene_id)
        self.previous_list_position = previous_list_position

    def get_id(self):
        return str(SZENEN_DETAILS) + "_view"

    def get_previous_list_position(self):
        return self.previous_list_position

    def visualize(self, window, addon):
        self.title_control = self.get_title_control(self.scene.get_name().encode("utf-8"), addon)
        self.execcontrol = None
        self.radiobutton_control = window.getControl(134)
        self.radiobutton_control.setVisible(True)
        self.radiobutton_control.setPosition(400, 180)
        self.__set_state(window, self.scene)
        if self.scene.is_executable():
            self.execcontrol = xbmcgui.ControlButton(600, 110, 120, 50, addon.getLocalizedString(32370))
        if self.execcontrol is None:
            window.addControls([self.title_control, self.imagecontrol])
        else:
            window.addControls([self.title_control, self.imagecontrol, self.execcontrol])

        self.gerate_group_control = window.getControl(146)
        self.gerate_group_control.setPosition(350, 300)
        self.gerate_group_control.setVisible(True)
        self.gerate_group_control.setHeight(100)
        self.geraete_list = window.getControl(148)

        self.geraete_list.reset()
        self.__add_geraetelistitems(self.scene.get_actions(), __addon__)

        self.automation_group_control = window.getControl(138)
        self.automation_group_control.setPosition(350, 460)
        self.automation_group_control.setHeight(100)
        self.automation_group_control.setVisible(True)
        self.automation_list = window.getControl(142)
        self.automation_list.reset()
        automations = self.scene.get_automationen()
        homepilot_utils.add_scene_to_automation_list(self.automation_list, automations, __addon__)

        self.__handle_navigation(window)


    def __set_state(self, window, scene):
        aktiv_button = window.getControl(160)
        is_active = scene.is_active()
        aktiv_button.setSelected(is_active)
        if is_active:
            self.imagecontrol = xbmcgui.ControlImage(400, 100, 64, 64, szene_img)
        else:
            self.imagecontrol = xbmcgui.ControlImage(400, 100, 64, 64, szene_img_deact)

        fav_button = window.getControl(136)
        fav_button.setSelected(scene.is_favored())

    def __handle_navigation(self, window):
        aktiv_button = window.getControl(160)
        if self.execcontrol is not None:
            window.setFocus(self.execcontrol)
            self.execcontrol.controlDown(self.radiobutton_control)
            aktiv_button.controlUp(self.execcontrol)
        else:
            window.setFocus(aktiv_button)


    def __add_geraetelistitems(self, actions, addon):
        for action in actions:
            item = xbmcgui.ListItem(label=action.get_name())
            icon_name = action.get_icon()
            item.setLabel2(self.get_cmd_txt(action.get_cmdId(), action.get_device_group(), addon))
            item.setIconImage(os.path.join(_images_device, icon_name))
            item.setProperty("description", action.get_description())
            self.geraete_list.addItem(item)

    def get_cmd_txt (self, cmd_id, device_group, addon):
        EIN = 10
        AUS = 11
        AUF = 1
        AB = 2
        STOPP = 3
        if device_group == 1:
            if cmd_id == EIN:
                return addon.getLocalizedString(32375)
            elif cmd_id == AUS:
                return addon.getLocalizedString(32376)
        elif device_group == 2:
            if cmd_id == AUF:
                return addon.getLocalizedString(32371)
            elif cmd_id == STOPP:
                return addon.getLocalizedString(32372)
            elif cmd_id == AB:
                return addon.getLocalizedString(32373)
            #Fahre in Pos (%)
        elif device_group == 5:
            if cmd_id == EIN:
                return addon.getLocalizedString(32375)
            elif cmd_id == AUS:
                return addon.getLocalizedString(32376)
            #Fahre in Pos (°C * 10))
        elif device_group == 4:
            if cmd_id == EIN:
                return addon.getLocalizedString(32375)
            elif cmd_id == AUS:
                return addon.getLocalizedString(32376)
            elif cmd_id == AUF:
                return addon.getLocalizedString(32371)
            elif cmd_id == STOPP:
                return addon.getLocalizedString(32372)
            elif cmd_id == AB:
                return addon.getLocalizedString(32373)
            elif cmd_id == 23:
                return addon.getLocalizedString(32371)
            elif cmd_id == 24:
                return addon.getLocalizedString(32373)
            #Fahre in Pos (%)
        elif device_group == 8:
            if cmd_id == AUF:
                return addon.getLocalizedString(32371)
            elif cmd_id == STOPP:
                return addon.getLocalizedString(32372)
            elif cmd_id == AB:
                return addon.getLocalizedString(32373)
            #Fahre in Pos (%))
        return ""


    def remove_everything(self, window):
        if self.execcontrol is None:
            window.removeControls([self.title_control, self.imagecontrol])
        else:
            window.removeControls([self.title_control, self.imagecontrol, self.execcontrol])
        self.gerate_group_control.setVisible(False)
        self.automation_group_control.setVisible(False)
        self.radiobutton_control.setVisible(False)


    def handle_click(self, controlId, window, use_local_favorites):
        if controlId == 160:
            aktiv_button = window.getControl(160)
            button_is_akiv = aktiv_button.isSelected()
            if self.scene.is_active() and not button_is_akiv:
                self.client.set_scene_inactive(self.scene.get_id())
                window.removeControl(self.imagecontrol)
                self.imagecontrol = xbmcgui.ControlImage(400, 100, 64, 64, szene_img_deact)
                window.addControl(self.imagecontrol)
            elif not self.scene.is_active() and button_is_akiv:
                self.client.set_scene_active(self.scene.get_id())
                window.removeControl(self.imagecontrol)
                self.imagecontrol = xbmcgui.ControlImage(400, 100, 64, 64, szene_img)
                window.addControl(self.imagecontrol)
        elif controlId == 136:
            fav_button = window.getControl(136)
            button_is_faved = fav_button.isSelected()
            if self.scene.is_favored() and not button_is_faved:
                if use_local_favorites:
                    local_favorites.add_scene(self.scene.get_id())
                else:
                    self.client.favorize_scene(self.scene.get_id())
            elif not self.scene.is_favored() and button_is_faved:
                if use_local_favorites:
                    local_favorites.remove_scene(self.scene.get_id())
                else:
                    self.client.unfavorize_scene(self.scene.get_id())
        elif controlId == self.execcontrol.getId():
            self.client.execute_scene(self.scene.get_id())


class EmptyView(BaseView):

    def __init__(self):
        pass

    def get_id(self):
        return "empty_view"

    def remove_everything(self, window):
        window.removeControls([self.einstellungen_control, self.label])

    def visualize(self, window, addon):
        self.einstellungen_control = self.get_title_control(32008, addon)
        self.label = xbmcgui.ControlLabel(460,250, 590, 40, MESSAGE_SETTINGS_DIALOG, alignment=0x00000002)
        window.addControls([self.einstellungen_control, self.label])
        return [self.einstellungen_control, self.label]

    def handle_click(self, control):
        pass
