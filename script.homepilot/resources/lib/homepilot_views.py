#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xbmcgui
import xbmc
import os
import xbmcaddon
__addon__ = xbmcaddon.Addon(id='script.homepilot')
__addon_path__        = __addon__.getAddonInfo('path').decode("utf-8")
_images_device = os.path.join(__addon_path__, 'resources', 'skins', 'Default', 'media', 'devices')
_images = os.path.join(__addon_path__, 'resources', 'skins', 'Default', 'media')

from homepilot_utils import ROLLADEN, SCHALTER, DIMMER, THERMOSTATE, TORE, SZENEN, SENSOREN, FAVORITEN, ALLE

device_types = {}
device_types[SCHALTER] = 1
device_types[ROLLADEN]= 2
device_types[SENSOREN]= 3
device_types[DIMMER] = 4
device_types[THERMOSTATE]= 5
device_types[TORE]= 8


class BaseView:

    def get_title_control(self, text):
        '''
        use this method to make sure view titles are everywhere on the same position
        '''
        label = unicode(text, "utf-8")
        #TODO: Move to xml
        if xbmc.skinHasImage ('settings/slider_back.png'):
            control = xbmcgui.ControlLabel(330, 65, 600, 75, label, font="Font_Reg22")
        else:
            control = xbmcgui.ControlLabel(400, 50, 600, 75, label, font="font16")
        return control

    def get_communication_error_label(self):
        return unicode("<Probleme bei der Kommunikation mit dem HomePilot>", "utf-8")



class ParametrizedGeraeteView(BaseView):

    def __init__(self, home_pilot_client, type):
        self.client = home_pilot_client
        self.total = 0
        self.controldict = {}
        self.type = type
        self.list_item_dict = {}
        self.hp_error = False
        self.errorcontrol = None

    def get_id (self):
        return self.type + "_view"

    def visualize (self, window):
        xbmc.log("visualize gerateview: " + str(self.type), level=xbmc.LOGNOTICE)
        self.title_control = self.get_title_control(self.type)
        window.addControl(self.title_control)
        if not hasattr(self, "gerate_group_control"):
            self.gerate_group_control = window.getControl(252)
        homepilot_is_reachable = self.client.ping()
        if not homepilot_is_reachable:
            self.hp_error = True
            errorlabel = self.get_communication_error_label()
            self.errorcontrol = xbmcgui.ControlLabel(400, 250, 600, 75, errorlabel)
            window.addControl(self.errorcontrol)
        else:
            self.hp_error = False
            try:
                devices = self.__get_devices()
                self.geraete_list = window.getControl(5)
                if self.type == SENSOREN or self.type == FAVORITEN:
                    self.geraete_list.controlLeft(self.__get_menu_control(window))
                else:
                    #set a fake control to prevent xbmc from setting it back to the main menu
                    control = window.getControl(111)
                    self.geraete_list.controlLeft(control)
                self.geraete_list.reset()
                self.__add_listitems(devices)
                self.gerate_group_control.setPosition(350,100)
                self.gerate_group_control.setVisible(True)
                if self.type != FAVORITEN and self.type != SENSOREN:
                    window.setFocus(self.geraete_list)
                xbmc.log("visualized gerateview: " + str(self.type), level=xbmc.LOGNOTICE)
            except Exception as inst:
                self.hp_error = True
                errorlabel = self.get_communication_error_label()
                self.errorcontrol = xbmcgui.ControlLabel(400, 250, 600, 75, errorlabel)
                window.addControl(self.errorcontrol)
                xbmc.log(str(inst), level=xbmc.LOGWARNING)


    def __get_menu_control(self, window):
        if self.type == FAVORITEN:
            return window.getControl(95)
        elif self.type == SENSOREN:
            return window.getControl(97)
        else:
            return window.getControl(96)

    def __add_listitems (self, devices):
        for device in devices:
            if self.type == SENSOREN:
                item = xbmcgui.ListItem(label = device.get_name())
            else:
                item = xbmcgui.ListItem(label = device.get_name(), label2=device.get_display_value())
            icon_name = device.get_icon()
            item.setIconImage(os.path.join(_images_device, icon_name))
            item.setProperty("description", device.get_description())
            item.setProperty("did", str(device.get_device_id()))
            item.setProperty("sync", str(device.get_sync()))
            self.list_item_dict[device.get_device_id()] = item
            self.geraete_list.addItem(item)

    def __get_devices (self):
        if self.type == FAVORITEN:
            devices = self.client.get_favorite_devices()
        elif self.type == ALLE:
            devices = self.client.get_devices()
        elif self.type == SENSOREN:
            devices = self.client.get_meters()
        else:
            devices = self.client.get_devices_by_device_group(device_types[self.type])
        return devices


    def remove_everything(self, window):
        if self.hp_error and self.errorcontrol is not None:
            window.removeControls([self.errorcontrol, self.title_control])
            self.errorcontrol = None
        else:
            controls_to_remove = [self.title_control]
            window.removeControls(controls_to_remove)
        self.gerate_group_control.setVisible(False)


    def update (self, window, menuControl):
        try:
            new_devices = self.__get_devices()
            if self.hp_error:
                self.remove_everything(window)
                self.visualize(window)
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
            self.visualize(window)
            self.hp_error = True


    def _get_list_item_position (self, item):
        for i in range(0, self.geraete_list.size()):
            if self.geraete_list.getListItem(i) == item:
                return i
        return -1


    def handle_click (self, control):
        if control in self.controldict: #irgendein Button, Slider etc.
            self.controldict[control].handle_click(control)


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

    def visualize (self, window):
        self.geraetelabel_control = self.get_title_control("Gerätetypen")

        self.geraetetypen_list = window.getControl(3)
        self.geraetetypen_list.reset()

        self.rolladen_item = xbmcgui.ListItem(label = ROLLADEN)
        self.rolladen_item.setIconImage(rollo_img)
        self.geraetetypen_list.addItem(self.rolladen_item)

        self.schalter_item = xbmcgui.ListItem(label = SCHALTER)
        self.schalter_item.setIconImage(schalter_img)
        self.geraetetypen_list.addItem(self.schalter_item)

        self.dimmer_item = xbmcgui.ListItem(label = DIMMER)
        self.dimmer_item.setIconImage(dimmer_img)
        self.geraetetypen_list.addItem(self.dimmer_item)

        self.thermostat_item = xbmcgui.ListItem(label = THERMOSTATE)
        self.thermostat_item.setIconImage(thermostat_img)
        self.geraetetypen_list.addItem(self.thermostat_item)

        self.tore_item = xbmcgui.ListItem(label = TORE)
        self.tore_item.setIconImage(tore_img)
        self.geraetetypen_list.addItem(self.tore_item)

        self.alle_item = xbmcgui.ListItem(label = ALLE)
        self.alle_item.setIconImage(logo_img)
        self.geraetetypen_list.addItem(self.alle_item)

        self.geraetetypen_list.setVisible(True)

        label = unicode("Gruppen (nur Anzeige)", "utf-8")
        self.gruppen_control = xbmcgui.ControlLabel(400, 380, 600, 75, label, font="font16")
        window.addControls([self.geraetelabel_control, self.gruppen_control])

        gruppen_list = window.getControl( 4 )
        gruppen_list.reset()
        self.gruppen_group_control = window.getControl(251)
        try:
            groups = self.client.get_groups()
            if len(groups) > 0:
                for group in groups:
                    gruppen_list.addItem (group.get_name())

                self.gruppen_group_control.setPosition(350,420)
                self.gruppen_group_control.setVisible(True)
                self.errorcontrol = None
            else:
                errorlabel = unicode("<Keine Gruppen vorhanden>", "utf-8")
                self.errorcontrol = xbmcgui.ControlLabel(450, 450, 600, 75, errorlabel)
                window.addControl(self.errorcontrol)
        except Exception, e:
            xbmc.log(str(e), level=xbmc.LOGWARNING)
            errorlabel = self.get_communication_error_label()
            self.errorcontrol = xbmcgui.ControlLabel(450, 450, 600, 75, errorlabel)
            window.addControl(self.errorcontrol)




    def handle_click (self, position):
        xbmc.log("position clicked: " + str(position), level=xbmc.LOGNOTICE)
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


class SzenenView(BaseView):

    def __init__(self):
        errorlabel = unicode("<noch nicht implementiert>", "utf-8")
        self.errorcontrol = xbmcgui.ControlLabel(400, 250, 600, 75, errorlabel)

    def get_id (self):
        return SZENEN + "_view"

    def remove_everything(self, window):
        window.removeControls([self.errorcontrol, self.title_control])


    def visualize (self, window):
        window.addControl(self.errorcontrol)
        self.title_control = self.get_title_control("Szenetypen")
        window.addControl(self.title_control)
        return [self.errorcontrol.getId(), self.title_control]

    def handle_click (self, control):
        pass


class EmptyView(BaseView):

    def __init__(self):
        pass

    def get_id (self):
        return "empty_view"

    def remove_everything(self, window):
        window.removeControls([self.einstellungen_control, self.label])

    def visualize (self, window):
        self.einstellungen_control = self.get_title_control("Einstellungen")
        self.label = xbmcgui.ControlLabel(460,250, 590, 40, "Durch drücken von <Enter> gelangen Sie zum Einstellungsdialog", alignment=0x00000002)
        window.addControls([self.einstellungen_control, self.label])
        return [self.einstellungen_control, self.label]

    def handle_click (self, control):
        pass
