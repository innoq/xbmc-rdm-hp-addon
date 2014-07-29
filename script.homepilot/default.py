#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import time
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
__profile__    = xbmc.translatePath( __addon__.getAddonInfo('profile') ).decode("utf-8")
home = xbmc.translatePath(__addon__.getAddonInfo('path'))

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

action_previous_menu = (9, 10, 92, 216, 247, 257, 275, 61467, 61448)

GERAETETYP_VIEW     = "geraetetyp_view"
FAVORITEN_VIEW      = str(FAVORITEN) + "_view"
FAVORITEN_LOKAL_VIEW = str(FAVORITEN_LOKAL) + "_view"
GRUPPEN_VIEW        = str(GRUPPEN) + "_view"
ALLE_VIEW           = str(ALLE) + "_view"
SENSOREN_VIEW       = str(SENSOREN) + "_view"

ROLLADEN_VIEW       = str(ROLLADEN) + "_view"
SCHALTER_VIEW       = str(SCHALTER) + "_view"
DIMMER_VIEW         = str(DIMMER) + "_view"
THERMOSTATE_VIEW    = str(THERMOSTATE) + "_view"
TORE_VIEW           = str(TORE) + "_view"
SZENEN_MANUELL_VIEW = str(SZENEN_MANUELL) + "_view"
SZENEN_NICHT_MANUELL_VIEW = str(SZENEN_NICHT_MANUELL) + "_view"
SZENEN_ALLE_VIEW    = str(SZENEN_ALLE) + "_view"
SZENENTYP_VIEW      = str(SZENENTYPEN) + "_view"
SZENEN_DETAILS_VIEW = str(SZENEN_DETAILS) + "_views"
EMPTY_VIEW = "empty_view"

BACKSPACE = 61448
ARROW_LEFT = 61570
MOVE_LEFT = 1
ACTION_NAV_BACK = 92
MOUSE_LEFT_CLICK = 100
ENTER = 135
MOVE_RIGHT = 2



class StatusUpdater (threading.Thread):

    def __init__(self, currentView, menuControl, window):
        self.window = window
        threading.Thread.__init__(self)
        self.set_current_view(currentView, menuControl)
        self.is_running = True
        self.current_window = None

    def set_current_view (self, currentView, menuControl):
        self.currentView = currentView
        self.menuControl = menuControl

    def set_current_window(self, currentWindow):
        self.current_window = currentWindow

    def set_is_running (self, is_running):
        self.is_running = is_running

    def run(self):
        self.is_running = 'True'
        while self.is_running:
            if self.current_window is not None:
                #this is a pretty sloppy implementation, as the window is updated even when it isn't display anymore
                #I've choosen this way as I didn't find a method for getting the current state of a xbmcgui.WindowXMLDialog
                #and the possible alternatives(e.g. passing references of this class around) looked more error prone
                self.current_window.update()
            view_id = self.currentView.get_id()
            if view_id == FAVORITEN_VIEW or view_id == FAVORITEN_LOKAL_VIEW or view_id == ROLLADEN_VIEW or view_id == SCHALTER_VIEW or view_id == DIMMER_VIEW or view_id ==THERMOSTATE_VIEW or view_id == TORE_VIEW:
                self.currentView.update(self.window, __addon__, self.menuControl)
            time.sleep(1.5)


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

        useLocalFavorites = self.settings_dialog_manager.use_local_favorites(__addon__)
        if useLocalFavorites == "true":
            self.favoritenView = homepilot_views.ParametrizedGeraeteView(self.client, FAVORITEN_LOKAL)
        else:
            self.favoritenView = homepilot_views.ParametrizedGeraeteView(self.client, FAVORITEN)
        self._wait_for_visualization = False

    def onInit(self):
        """
        initializes the window
        """
        self.window = xbmcgui.Window(xbmcgui.getCurrentWindowDialogId())
        self.window.setProperty('windowLabel', 'Rademacher HomePilot')
        geraete_view = self.favoritenView
        menu_control = self.window.getControl(95)
        useLocalFavorites = self.settings_dialog_manager.use_local_favorites(__addon__)
        title = self.__get_favorite_view_title(useLocalFavorites)
        geraete_view.visualize (self, __addon__, title)
        self.setFocus(menu_control)
        self.currentView = geraete_view
        self.status_updater = StatusUpdater (self.currentView, menu_control, self)
        self.status_updater.start()

    def shutdown(self):
        """
        closes the window
        """
        self.status_updater.is_running = False
        self.close()

    def __is_geraeteview (self, view):
        return view == ALLE_VIEW or view == ROLLADEN_VIEW or view == SCHALTER_VIEW or view == DIMMER_VIEW or \
                         view == THERMOSTATE_VIEW or view == TORE_VIEW

    def __get_favorite_view_title(self, useLocalFavorites):
        label = __addon__.getLocalizedString(32004)
        if useLocalFavorites == "true":
            label += " (lokale Favoriten)"
        else:
            label += " (HomePilot)"
        xbmc.log("label " + str(label), level=xbmc.LOGNOTICE)
        return label

    def onAction(self, action):
        """
        handles window exits
        # ACTION_LAST_PAGE = 160
        """
        xbmc.log("onAction " + str(action.getButtonCode()), level=xbmc.LOGNOTICE)
        xbmc.log("Fokus " + str(self.getFocusId()), level=xbmc.LOGNOTICE)
        view = self.currentView.get_id()
        xbmc.log("View " + str(view), level=xbmc.LOGNOTICE)
        is_geraeteview = self.__is_geraeteview(view)
        if action == 13 or action == 10 or action == 160 or action == 21:
            self.shutdown()
        elif view == GERAETETYP_VIEW:
            self.__on_Action_Geraetetypview(action)
        elif view == SZENENTYP_VIEW:
            if action.getButtonCode() == BACKSPACE or action.getButtonCode() == ARROW_LEFT:
                self.setFocusId(94)
            elif self.getFocusId() == 257 and (action.getButtonCode() == 61453 or action == MOUSE_LEFT_CLICK or action == ENTER):#Gerätetyptabelle
                type_list = self.getControl(257)
                position = type_list.getSelectedPosition()
                next_view = self.currentView.handle_click(position)
                self.currentView.remove_everything(self)
                szenen_view = homepilot_views.SzenenView(self.client, next_view)
                menu_control = self.window.getControl(94)
                szenen_view.visualize(self, __addon__)
                self.currentView = szenen_view
                self.status_updater.set_current_view(szenen_view, menu_control)
                self.setFocusId(258)
            elif action == MOVE_RIGHT:
                self.setFocusId(257)
        elif self.getFocusId() == 999 and action == 31:
            self.setFocusId(5)
        elif action == ACTION_NAV_BACK and (view == FAVORITEN_VIEW or view == FAVORITEN_LOKAL_VIEW):
            self.setFocusId(95)
        elif action == ACTION_NAV_BACK and view == SENSOREN_VIEW:
            self.setFocusId(97)
        elif action == MOVE_RIGHT and view == SENSOREN_VIEW:
            self.setFocusId(5)
        elif action.getButtonCode() == BACKSPACE or action.getButtonCode() == ARROW_LEFT:
            self.__handle_back_action_on_nested_sites(view, is_geraeteview)
        if self.getFocusId() == 0 and action.getButtonCode() != 0:
            if view == FAVORITEN_VIEW or view == FAVORITEN_LOKAL_VIEW or view == SENSOREN_VIEW or is_geraeteview:
                self.setFocusId(5)
            elif view == GERAETETYP_VIEW:
                self.setFocusId(257)
            else:
                self.setFocusId(95)


    def __on_Action_Geraetetypview (self, action):

        if self.getFocusId() == 257 and (action.getButtonCode() == 61453 or action == MOUSE_LEFT_CLICK or action == ENTER):#Gerätetyptabelle
            xbmc.log("select list item " + __addon__.getLocalizedString(32005), level=xbmc.LOGNOTICE)
            gruppen_list = self.getControl(257)
            position = gruppen_list.getSelectedPosition()
            next_view = self.currentView.handle_click(position)
            if next_view is not None:
                self.currentView.remove_everything(self)
                geraete_view = homepilot_views.ParametrizedGeraeteView(self.client, next_view)
                menu_control = self.window.getControl(96)
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
            menu_control = self.window.getControl(96)
            geraete_view.visualize(self, gruppen_name, __addon__)
            self.currentView = geraete_view
            self.status_updater.set_current_view(geraete_view, menu_control)
        elif action == ACTION_NAV_BACK or action == MOVE_LEFT:
            self.setFocusId(96)


    def __handle_back_action_on_nested_sites (self, view, is_geraeteview):
        if is_geraeteview and self.getFocusId() != 999:
            self.__show_geraetetyp_view()
            self.__set_geraetetyp_list_focus(view)
            self.setFocusId(257)
        elif view == GRUPPEN_VIEW and self.getFocusId() != 999:
            group_id = self.currentView.get_group()
            self.__show_geraetetyp_view()
            self.__set_gruppen_list_focus(group_id)


    def onFocus(self, control):
        xbmc.log("onFocus " + str(control), level=xbmc.LOGNOTICE)
        if not self._wait_for_visualization:
            if control == 98: #menüpunkt Einstellungen
                if self.currentView.get_id() != EMPTY_VIEW:
                    self.currentView.remove_everything (self)
                    empty_view = homepilot_views.EmptyView()
                    menu_control = self.window.getControl(98)
                    empty_view.visualize(self, __addon__)
                    self.currentView = empty_view
                    self.status_updater.set_current_view(empty_view, menu_control)
            elif control == 95: #Menüpunkt Favoriten
                if self.currentView.get_id() != FAVORITEN_VIEW and self.currentView.get_id != FAVORITEN_LOKAL_VIEW:
                    xbmc.log("visualize Favoritenview ")
                    self.currentView.remove_everything (self)
                    useLocalFavorites = self.settings_dialog_manager.use_local_favorites(__addon__)
                    title = self.__get_favorite_view_title(useLocalFavorites)
                    if useLocalFavorites == "true":
                        geraete_view = homepilot_views.ParametrizedGeraeteView(self.client, FAVORITEN_LOKAL)
                    else:
                        geraete_view = homepilot_views.ParametrizedGeraeteView(self.client, FAVORITEN)
                    menu_control = self.window.getControl(95)
                    geraete_view.visualize (self, __addon__, title)
                    self.currentView = geraete_view
                    self.status_updater.set_current_view(geraete_view, menu_control)
            elif control == 96: #Menüpunkt Geräte
                if self.currentView.get_id() != GERAETETYP_VIEW:
                    previous_view = self.currentView.get_id()
                    self.__show_geraetetyp_view()
            elif control == 97: # Menüpunkt sensoren
                if self.currentView.get_id() != SENSOREN_VIEW:
                    self.currentView.remove_everything (self)
                    geraete_view = homepilot_views.ParametrizedGeraeteView(self.client, SENSOREN)
                    menu_control = self.window.getControl(97)
                    geraete_view.visualize (self, __addon__)
                    self.currentView = geraete_view
                    self.status_updater.set_current_view(geraete_view, menu_control)
            elif control == 94: # Menüpunkt Szenentypen
                if self.currentView.get_id() != SZENENTYP_VIEW:
                    menu_control = self.window.getControl(97)
                    self.currentView.remove_everything (self)
                    self.currentView = homepilot_views.SzenentypView()
                    menu_control.controlRight(self.window.getControl(257))
                    self.currentView.visualize (self, __addon__)


    def onClick(self, control):
        xbmc.log("onClick " + str(control), level=xbmc.LOGNOTICE)
        view_id = self.currentView.get_id()
        if view_id == SZENEN_DETAILS_VIEW:
            self.currentView.handle_click(control, self)
        elif control == 5:
            if view_id == SENSOREN_VIEW:
                geraete_listcontrol = self.getControl(5)
                list_item = geraete_listcontrol.getSelectedItem()
                did = list_item.getProperty("did")
                device_window = MeterWindow('device_window.xml', home, client=self.client, did=did, parent=self)
                device_window.doModal()
            elif view_id == FAVORITEN_VIEW or view_id == FAVORITEN_LOKAL_VIEW or view_id == ALLE_VIEW or view_id == ROLLADEN_VIEW \
                or view_id == SCHALTER_VIEW or view_id == DIMMER_VIEW or view_id == THERMOSTATE_VIEW or view_id == TORE_VIEW:
                geraete_listcontrol = self.getControl(5)
                list_item = geraete_listcontrol.getSelectedItem()
                did = list_item.getProperty("did")
                self.__open_device_window(did)
        elif control == 98: #menüpunkt Einstellungen
                self._wait_for_visualization = True
                self.settings_dialog_manager.update_ip_address(__addon__)
                ip_address = self.settings_dialog_manager.get_ip_address(__addon__)
                self._wait_for_visualization = False
                self.client.set_ip_address (ip_address)
        elif control == 258:# show szenen detail view
            scene_list_control = self.getControl(258)
            list_item = scene_list_control.getSelectedItem()
            sceneId = list_item.getProperty("sid")
            xbmc.log("sid " + str(sceneId), level=xbmc.LOGNOTICE)
            self.currentView.remove_everything(self)
            self.currentView = homepilot_views.SzenenDetailView(self.client, sceneId)
            self.currentView.visualize(self, __addon__)


    def __set_geraetetyp_list_focus (self, previeous_view):
        list_control = self.window.getControl(257)
        if previeous_view == ALLE_VIEW:
            list_control.selectItem(5)
        elif previeous_view == ROLLADEN_VIEW:
            list_control.selectItem(0)
        elif previeous_view == SCHALTER_VIEW:
            list_control.selectItem(1)
        elif previeous_view == DIMMER_VIEW:
            list_control.selectItem(2)
        elif previeous_view == THERMOSTATE_VIEW:
            list_control.selectItem(3)
        elif previeous_view == TORE_VIEW:
            list_control.selectItem(4)


    def __set_gruppen_list_focus (self, gruppen_id):
        xbmc.log("Set gruppenlist focus " + str(gruppen_id), level=xbmc.LOGWARNING)
        list_control = self.window.getControl(4)
        xbmc.log("gruppenlist size  " + str(list_control.size()), level=xbmc.LOGWARNING)

        i = 0
        while True:
            try:
                item = list_control.getListItem(i)
                gid = item.getProperty("gid")
                xbmc.log("gruppenlist  " + str(gid), level=xbmc.LOGWARNING)
                if gid == str(gruppen_id):
                    list_control.selectItem(i)
                    return
            except RuntimeError:
                self.setFocusId(4)
                return

    def __show_geraetetyp_view(self):
        self.currentView.remove_everything (self)
        geraetetyp_view = homepilot_views.GeraetetypView(self.client)
        menu_control = self.window.getControl(96)
        menu_control.controlRight(self.window.getControl(257))
        geraetetyp_view.visualize (self, __addon__)
        self.currentView = geraetetyp_view
        self.status_updater.set_current_view(geraetetyp_view, menu_control)


    def __open_device_window(self, did):
        useLocalFavorites = self.settings_dialog_manager.use_local_favorites(__addon__)
        local_favs = False
        if useLocalFavorites == "true":
            local_favs = True
        try:
            device = self.client.get_device_by_id(did)
            dgroup = device.get_devicegroup()
            if dgroup == 2 or dgroup == 4 or dgroup == 8:

                percent_window = PercentageWindow('device_window.xml', home, client=self.client, device=device, parent=self, local_favs= local_favs)
                self.status_updater.set_current_window(percent_window)
                percent_window.doModal()
            elif dgroup == 1:
                switch_window = SwitchWindow('device_window.xml', home, client=self.client, device=device, parent=self, local_favs= local_favs)
                self.status_updater.set_current_window(switch_window)
                switch_window.doModal()
            elif dgroup == 5:
                percent_window = DegreeWindow('device_window.xml', home, client=self.client, device=device, parent=self, local_favs= local_favs)
                self.status_updater.set_current_window(percent_window)
                percent_window.doModal()
        except Exception, e:
            xbmc.log("Fehler beim Öffnen einer Detailsicht: " + str(e), level=xbmc.LOGWARNING)
            error_window = ErrorWindow('device_window.xml', home, parent=self)
            error_window.doModal()


if __name__ == "__main__":
    args = sys.argv
    window = GuiController('homepilot.xml', home)
    window.doModal()

