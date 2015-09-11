#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import xbmc
import xbmcgui
import xbmcaddon
import threading

"""
Implementation of an XBMC Script Addon

This addon displays the current state of a Rollo or Switch device
and offers buttons to change ist.
"""


__addon__ = xbmcaddon.Addon(id='script.homepilot')
__cwd__        = xbmc.translatePath( __addon__.getAddonInfo('path') ).decode("utf-8")

# add lib directory to sys.path as this doesn't happen automatically
__resource__   = xbmc.translatePath( os.path.join( __cwd__, 'resources', 'lib' ) ).decode("utf-8")
sys.path.append (__resource__)

import homepilot_client
import homepilot_views
import settings
import time
from homepilot_utils import ROLLADEN, SCHALTER, DIMMER, THERMOSTATE, TORE, SZENEN_MANUELL, SZENEN_NICHT_MANUELL, \
    SZENEN_ALLE, SZENENTYPEN, SZENEN_DETAILS, SENSOREN, ALLE, FAVORITEN, GRUPPEN, FAVORITEN_LOKAL
from device_windows import MeterWindow, PercentageWindow, SwitchWindow, DegreeWindow, ErrorWindow
from scene_window import SzenenDetailWindow

FAVORITEN_VIEW      = str(FAVORITEN) + "_view"
FAVORITEN_LOKAL_VIEW = str(FAVORITEN_LOKAL) + "_view"
GERAETETYP_VIEW     = "geraetetyp_view" # String wird so noch irgendwo anders verwendet Anpassung nicht trivial str(GERAETE) + "_view"
DEVICE_GRUPPEN_VIEW        = str(GRUPPEN) + "_view"
DEVICE_ALLE_VIEW           = str(ALLE) + "_view"
SENSOREN_VIEW       = str(SENSOREN) + "_view"

DEVICE_ROLLADEN_VIEW       = str(ROLLADEN) + "_view"
DEVICE_SCHALTER_VIEW       = str(SCHALTER) + "_view"
DEVICE_DIMMER_VIEW         = str(DIMMER) + "_view"
DEVICE_THERMOSTATE_VIEW    = str(THERMOSTATE) + "_view"
DEVICE_TORE_VIEW           = str(TORE) + "_view"
SZENEN_MANUELL_VIEW = str(SZENEN_MANUELL) + "_view"
SZENEN_NICHT_MANUELL_VIEW = str(SZENEN_NICHT_MANUELL) + "_view"
SZENEN_ALLE_VIEW    = str(SZENEN_ALLE) + "_view"
SZENENTYP_VIEW      = str(SZENENTYPEN) + "_view"
SZENEN_DETAILS_VIEW = str(SZENEN_DETAILS) + "_view"
EMPTY_VIEW = "empty_view"

#Original Links
ACTION_NAV_BACK = 92
ACTION_BACKSPACE = 110
ACTION_MOVE_LEFT = 1
MOUSE_LEFT_CLICK = 100
ENTER = 135
MOVE_RIGHT = 2

#Tastaturnummern buttoncode()
HP_VK_DOWN = 61569
HP_VK_UP = 61568
HP_VK_LEFT = 61570
HP_VK_RIGHT = 61571
HP_VK_ENTER = 61453
#BC_HP_VK_ENTER_NUM = 
HP_VK_BACK = 61448
HP_VK_ESC = 61467

#CEC Befehle (Grundig)
HP_CEC_DOWN = 167
HP_CEC_UP = 166
HP_CEC_LEFT = 169
HP_CEC_RIGHT = 168
HP_CEC_ENTER = 11
HP_CEC_BACK = 216
#HP_CEC_ESC = 

#Action IDs > sollen allgemein richtig sein
AID_DOWN = 4
AID_UP = 3
AID_LEFT = 1
AID_RIGHT = 2
AID_ENTER = 7
AID_BACK = 92
AID_ESC = 10

#FocusIds
FOCUS_LIST_FAV = 95
FOCUS_LIST_DEVICES = 96
FOCUS_LIST_DEVICE_TYP = 257
FOCUS_LIST_DEVICE_GROUP = 4
FOCUS_LIST_SCENES = 94
FOCUS_LIST_SENSOR = 97
FOCUS_LIST_CONFIG = 98
FOCUS_LIST_SENSORLIST = 5
FOCUS_LIST_FAVLIST_AKTOREN = 255
FOCUS_LIST_FAVLIST_SZENEN = 264
FOCUS_LIST_SCENE_LIST = 258
FOCUS_SCROLL_FAVLIST_DEV = 993
FOCUS_SCROLL_FAVLIST_SCN = 226
#FOCUS_SCROLL_DEVTYP = 
FOCUS_SCROLL_DEVGROUP = 998
FOCUS_SCROLL_DEVLIST = 999
FOCUS_SCROLL_SCENELIST = 259

# tail -f /home/root/.xbmc/temp/xbmc.log
# ps aux | grep xbmc.bin

class StatusUpdater (threading.Thread):

    def __init__(self, initialView, menuControl, title, window):
        self.window = window
        threading.Thread.__init__(self)
        self.set_current_view(initialView, menuControl)
        self.is_running = True
        self.current_window = None
        self.title = title

    def set_current_view (self, currentView, menuControl):
        self.currentView = currentView
        self.menuControl = menuControl

    def set_current_window(self, currentWindow):
        self.current_window = currentWindow

    def set_is_running (self, is_running):
        self.is_running = is_running

    def run(self):
        self.is_running = 'True'
        self.currentView.visualize (self.window, __addon__, self.title)
        while self.is_running:
            time.sleep(1.5)
            if self.current_window is not None and not self.current_window.is_closed():
                self.current_window.update()
            v_id = self.currentView.get_id()
            if v_id == FAVORITEN_VIEW or v_id == FAVORITEN_LOKAL_VIEW or v_id == DEVICE_ROLLADEN_VIEW or v_id == DEVICE_SCHALTER_VIEW \
                    or v_id == DEVICE_DIMMER_VIEW or v_id == DEVICE_THERMOSTATE_VIEW or v_id == DEVICE_TORE_VIEW or v_id == SENSOREN_VIEW:
                self.currentView.update(self.window, __addon__, self.menuControl)




class GuiController(xbmcgui.WindowXMLDialog):
    """
    representing a window with the HomePilot controls
    """

    def __init__( self, *args, **kwargs ):
        """
        constructor of the class
        """
        xbmcgui.WindowXMLDialog.__init__( self )
        self.settings_dialog_manager = settings.SettingsDialogManager()
        ip_address = self.settings_dialog_manager.get_ip_address(__addon__)
        self.client = homepilot_client.HomepilotClient(ip_address)

        self._wait_for_visualization = False
        self._isScene = False

    def onInit(self):
        """
        initializes the window
        """
        self.window = xbmcgui.Window(xbmcgui.getCurrentWindowDialogId())
        self.setProperty('windowLabel', __addon__.getLocalizedString(32383))
        menu_control = self.getControl(95)
        uselocalfavorites = self.settings_dialog_manager.use_local_favorites(__addon__)
        if uselocalfavorites == "true":
            favoritenView = homepilot_views.FavoritenView(self.client, FAVORITEN_LOKAL, menu_control)
        else:
            favoritenView = homepilot_views.FavoritenView(self.client, FAVORITEN, menu_control)
        title = self.__get_favorite_view_title(uselocalfavorites)

        self.setFocus(menu_control)
        self.currentView = favoritenView
        self.status_updater = StatusUpdater (favoritenView, menu_control, title, self)
        self.status_updater.start()


    def shutdown(self):
        """
        closes the window
        """
        self.status_updater.is_running = False
        self.close()

    def __get_favorite_view_title(self, useLocalFavorites):
        label = __addon__.getLocalizedString(32004)
        if useLocalFavorites == "true":
            label += " (" + __addon__.getLocalizedString(32385) + ")"
        else:
            label += " (" + __addon__.getLocalizedString(32382) + ")"
        return label

    def __is_geraeteview (self, view):
        return view == DEVICE_ALLE_VIEW or view == DEVICE_ROLLADEN_VIEW or view == DEVICE_SCHALTER_VIEW or view == DEVICE_DIMMER_VIEW or \
                         view == DEVICE_THERMOSTATE_VIEW or view == DEVICE_TORE_VIEW
        
    # Eventhandling
    def onAction(self, action):
        view = self.currentView.get_id()
        is_geraeteview = self.__is_geraeteview(view)
        if action == 10 or action == 160 or action == 21:
            self.shutdown()
        elif view == GERAETETYP_VIEW:
            self.__on_action_geraetetypview(action)
        elif view == SZENENTYP_VIEW:
            if action == ACTION_BACKSPACE or action == ACTION_MOVE_LEFT:
                self.setFocusId(94)
            elif self.getFocusId() == 257 and (action.getButtonCode() == 61453 or action == MOUSE_LEFT_CLICK or action == ENTER):#Gerätetyptabelle
                type_list = self.getControl(257)
                item = type_list.getSelectedItem()
                next_view = self.currentView.handle_click(item)
                self.currentView.remove_everything(self)
                szenen_view = homepilot_views.SzenenListView(self.client, next_view)
                menu_control = self.getControl(94)
                szenen_view.visualize(self, __addon__)
                self.currentView = szenen_view
                self.status_updater.set_current_view(szenen_view, menu_control)
            elif action == MOVE_RIGHT:
                self.setFocusId(257)
        elif self.getFocusId() == 999 and action == 31:
            self.setFocusId(5)
        elif action == ACTION_NAV_BACK and (view == FAVORITEN_VIEW or view == FAVORITEN_LOKAL_VIEW):
            self.setFocusId(95)
        elif action == ACTION_NAV_BACK and view == SENSOREN_VIEW:
            self.setFocusId(97)
        elif action == MOVE_RIGHT and view == SENSOREN_VIEW and self.getFocusId() != 999:
            self.setFocusId(5)
        elif action == ACTION_BACKSPACE or action == ACTION_MOVE_LEFT or action == ACTION_NAV_BACK:
            self.__handle_back_action_on_nested_sites(view, is_geraeteview)
        # XBMC has lost focus, set a new one
        if self.getFocusId() == 0 and action.getButtonCode() != 0:
            if view == SENSOREN_VIEW or is_geraeteview:
                self.setFocusId(5)
            elif view == FAVORITEN_VIEW or view == FAVORITEN_LOKAL_VIEW:
                self.setFocusId(255)
            elif view == GERAETETYP_VIEW:
                self.setFocusId(257)
            else:
                self.setFocusId(95)


    def __on_action_geraetetypview (self, action):
        if self.getFocusId() == 257 and (action.getButtonCode() == 61453 or action == MOUSE_LEFT_CLICK or action == ENTER):#Gerätetyptabelle
            gruppen_list = self.getControl(257)
            position = gruppen_list.getSelectedItem()
            next_view = self.currentView.handle_click(position)
            if next_view is not None:
                self.currentView.remove_everything(self)
                geraete_view = homepilot_views.ParametrizedGeraeteView(self.client, next_view)
                menu_control = self.getControl(96)
                geraete_view.visualize(self, __addon__)
                self.currentView = geraete_view
                self.status_updater.set_current_view(geraete_view, menu_control)
        elif self.getFocusId() == 4 and (action.getButtonCode() == 61453 or action == MOUSE_LEFT_CLICK or action == ENTER):#Gruppentabelle
            gruppen_list = self.getControl(4)
            position = gruppen_list.getSelectedPosition()
            list_item = gruppen_list.getListItem(position)
            gruppen_id = list_item.getProperty("gid")
            gruppen_name = list_item.getLabel()
            self.currentView.remove_everything(self)
            geraete_view = homepilot_views.ParametrizedGeraeteView(self.client, GRUPPEN, gruppen_id)
            menu_control = self.getControl(96)
            geraete_view.visualize(self, __addon__, gruppen_name)
            self.currentView = geraete_view
            self.status_updater.set_current_view(geraete_view, menu_control)
        elif action == ACTION_NAV_BACK:
            self.setFocusId(96)


    def __handle_back_action_on_nested_sites (self, view, is_geraeteview):
        if is_geraeteview and self.getFocusId() != 999:
            self.__show_geraetetyp_view()
            self.__set_geraetetyp_list_focus(view)
            self.setFocusId(257)
        elif view == DEVICE_GRUPPEN_VIEW and self.getFocusId() != 999:
            group_id = self.currentView.get_group()
            self.__show_geraetetyp_view()
            self.__set_gruppen_list_focus(group_id)
        elif view == SZENEN_NICHT_MANUELL_VIEW or view == SZENEN_MANUELL_VIEW or view == SZENEN_ALLE_VIEW:
            self.__show_szenentyp_view()
            # set the focus in the szenetyp list
            self.currentView.focus_list_item(view, self)

    def onFocus(self, control):
        if not self._wait_for_visualization:
            if control == FOCUS_LIST_CONFIG: #menüpunkt Einstellungen
                if self.currentView.get_id() != EMPTY_VIEW:
                    self.currentView.remove_everything (self)
                    empty_view = homepilot_views.EmptyView()
                    menu_control = self.getControl(FOCUS_LIST_CONFIG)
                    empty_view.visualize(self, __addon__)
                    self.currentView = empty_view
                    self.status_updater.set_current_view(empty_view, menu_control)
            elif control == FOCUS_LIST_FAV: #Menüpunkt Favoriten
                if self.currentView.get_id() != FAVORITEN_VIEW and self.currentView.get_id != FAVORITEN_LOKAL_VIEW:
                    self.__show_favoriten_view()
            elif control == FOCUS_LIST_DEVICES: #Menüpunkt Geräte
                if self.currentView.get_id() != GERAETETYP_VIEW:
                    previous_view = self.currentView.get_id()
                    self.__show_geraetetyp_view()
            elif control == FOCUS_LIST_SENSOR: # Menüpunkt sensoren
                if self.currentView.get_id() != SENSOREN_VIEW:
                    self.currentView.remove_everything (self)
                    geraete_view = homepilot_views.ParametrizedGeraeteView(self.client, SENSOREN)
                    menu_control = self.getControl(FOCUS_LIST_SENSOR)
                    geraete_view.visualize (self, __addon__)
                    self.currentView = geraete_view
                    self.status_updater.set_current_view(geraete_view, menu_control)
            elif control == FOCUS_LIST_SCENES: # Menüpunkt Szenentypen
                if self.currentView.get_id() != SZENENTYP_VIEW:
                    self.__show_szenentyp_view()

    def onClick(self, control):
        view_id = self.currentView.get_id()
        if control == FOCUS_LIST_SENSORLIST:
            if view_id == SENSOREN_VIEW:
                geraete_listcontrol = self.getControl(FOCUS_LIST_SENSORLIST)
                list_item = geraete_listcontrol.getSelectedItem()
                did = list_item.getProperty("did")
                meter_window = MeterWindow('device_window.xml', __cwd__, client=self.client, did=did, parent=self)
                self.status_updater.set_current_window(meter_window)
                meter_window.doModal()
            elif view_id == DEVICE_ALLE_VIEW or view_id == DEVICE_ROLLADEN_VIEW or view_id == DEVICE_SCHALTER_VIEW or view_id == DEVICE_DIMMER_VIEW \
                or view_id == DEVICE_THERMOSTATE_VIEW or view_id == DEVICE_TORE_VIEW or view_id == DEVICE_GRUPPEN_VIEW:
                geraete_listcontrol = self.getControl(FOCUS_LIST_SENSORLIST)
                list_item = geraete_listcontrol.getSelectedItem()
                did = list_item.getProperty("did")
                self.__open_device_window(did)
        elif view_id == FAVORITEN_VIEW or view_id == FAVORITEN_LOKAL_VIEW:
            if control == 255:
                geraete_listcontrol = self.getControl(255)
                list_item = geraete_listcontrol.getSelectedItem()
                did = list_item.getProperty("did")
                self.__open_device_window(did)
            elif control == 264:
                scene_list_control = self.getControl(264)
                list_item = scene_list_control.getSelectedItem()
                position = scene_list_control.getSelectedPosition
                sid = list_item.getProperty("sid")
                useLocalFavorites = self.settings_dialog_manager.use_local_favorites(__addon__)
                self.__open_scene_window(sid, position, useLocalFavorites)
        elif control == FOCUS_LIST_CONFIG: #Menüpunkt Einstellungen
            self._wait_for_visualization = True
            self.settings_dialog_manager.update_ip_address(__addon__)
            ip_address = self.settings_dialog_manager.get_ip_address(__addon__)
            self._wait_for_visualization = False
            self.client.set_ip_address(ip_address)
        elif control == 258:# show szenen detail view
            scene_list_control = self.getControl(258)
            list_item = scene_list_control.getSelectedItem()
            position = scene_list_control.getSelectedPosition()
            sceneId = list_item.getProperty("sid")
            useLocalFavorites = self.settings_dialog_manager.use_local_favorites(__addon__)
            self.__open_scene_window(sceneId, position, useLocalFavorites)


    def __set_geraetetyp_list_focus (self, previeous_view):
        list_control = self.getControl(257)
        try:
            for i in range(0, 6):
                list_item = list_control.getListItem(i)
                type = list_item.getProperty("type")
                if previeous_view == type + "_view":
                    list_control.selectItem(i)
                    return
        #unfortunately there seem to be no way to get the number of list items in a control
        #if a non-existent index is accessed a value error is thrown
        except ValueError,e:
            pass


    def _set_szenenlistfocus(self, position):
        list_control = self.getControl(258)
        self.setFocus(list_control)
        list_control.selectItem(position)


    def __set_gruppen_list_focus (self, gruppen_id):
        list_control = self.window.getControl(4)
        i = 0
        while True:
            try:
                item = list_control.getListItem(i)
                gid = item.getProperty("gid")
                if gid == str(gruppen_id):
                    list_control.selectItem(i)
                    self.setFocusId(4)
                    return
            except RuntimeError:
                self.setFocusId(4)
                return

    def __show_favoriten_view(self):
        self.currentView.remove_everything (self)
        useLocalFavorites = self.settings_dialog_manager.use_local_favorites(__addon__)
        title = self.__get_favorite_view_title(useLocalFavorites)
        menu_control = self.getControl(FOCUS_LIST_FAV)
        if useLocalFavorites == "true":
            geraete_view = homepilot_views.FavoritenView(self.client, FAVORITEN_LOKAL, menu_control)
        else:
            geraete_view = homepilot_views.FavoritenView(self.client, FAVORITEN, menu_control)
        geraete_view.visualize (self, __addon__, title)
        self.currentView = geraete_view
        self.status_updater.set_current_view(geraete_view, menu_control)


    def __show_geraetetyp_view(self):
        self.currentView.remove_everything (self)
        geraetetyp_view = homepilot_views.GeraetetypView(self.client)
        menu_control = self.getControl(96)
        menu_control.controlRight(self.getControl(257))
        geraetetyp_view.visualize (self, __addon__)
        self.currentView = geraetetyp_view
        self.status_updater.set_current_view(geraetetyp_view, menu_control)


    def __show_szenentyp_view(self):
        menu_control = self.getControl(94)
        self.currentView.remove_everything (self)
        status_view = homepilot_views.SzenentypView()
        self.currentView = status_view
        self.status_updater.set_current_view(status_view, menu_control)
        menu_control.controlRight(self.getControl(257))
        self.currentView.visualize (self, __addon__)


    def __open_device_window(self, did):
        useLocalFavorites = self.settings_dialog_manager.use_local_favorites(__addon__)
        local_favs = False
        if useLocalFavorites == "true":
            local_favs = True
        try:
            device = self.client.get_device_by_id(did)
            dgroup = device.get_devicegroup()
            if dgroup == 2 or dgroup == 4 or dgroup == 8:
                percent_window = PercentageWindow('device_window.xml', __cwd__, client=self.client, device=device, parent=self, local_favs= local_favs)
                self.status_updater.set_current_window(percent_window)
                percent_window.doModal()
            elif dgroup == 1:
                switch_window = SwitchWindow('device_window.xml', __cwd__, client=self.client, device=device, parent=self, local_favs= local_favs)
                self.status_updater.set_current_window(switch_window)
                switch_window.doModal()
            elif dgroup == 5:
                percent_window = DegreeWindow('device_window.xml', __cwd__, client=self.client, device=device, parent=self, local_favs= local_favs)
                self.status_updater.set_current_window(percent_window)
                percent_window.doModal()
        except Exception, e:
            xbmc.log("Fehler beim Öffnen einer Detailsicht: " + str(e), level=xbmc.LOGWARNING)
            error_window = ErrorWindow('device_window.xml', __cwd__, parent=self)
            error_window.doModal()

    def __open_scene_window(self, sceneId, position, useLocalFavorites):
            scene_window = SzenenDetailWindow('scene_window.xml', __cwd__, client=self.client, scene_id=sceneId,
            previous_list_position=position, addon=__addon__, parent=self,
            use_local_favorites=useLocalFavorites)
            self.status_updater.set_current_window(scene_window)
            scene_window.doModal()


if __name__ == "__main__":
    window = GuiController('homepilot.xml', __cwd__)
    window.doModal()

