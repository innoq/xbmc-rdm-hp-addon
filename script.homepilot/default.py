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
from homepilot_utils import ROLLADEN, SCHALTER, DIMMER, THERMOSTATE, TORE, SZENEN, SENSOREN, ALLE, FAVORITEN
from device_windows import MeterWindow, PercentageWindow, SwitchWindow, DegreeWindow, ErrorWindow

action_previous_menu = (9, 10, 92, 216, 247, 257, 275, 61467, 61448)

GERAETETYP_VIEW = "geraetetyp_view"
FAVORITEN_VIEW = FAVORITEN + "_view"
ALLE_VIEW = ALLE + "_view"
SENSOREN_VIEW = SENSOREN + "_view"

ROLLADEN_VIEW = ROLLADEN + "_view"
SCHALTER_VIEW = SCHALTER + "_view"
DIMMER_VIEW = DIMMER + "_view"
THERMOSTATE_VIEW = THERMOSTATE + "_view"
TORE_VIEW = TORE + "_view"
SZENEN_VIEW = SZENEN + "_view"
EMPTY_VIEW = "empty_view"



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
            if view_id == FAVORITEN_VIEW or view_id == ROLLADEN_VIEW or view_id == SCHALTER_VIEW or view_id == DIMMER_VIEW or view_id ==THERMOSTATE_VIEW or view_id == TORE_VIEW:
                self.currentView.update(self.window, self.menuControl)
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

        self.szenenView = homepilot_views.SzenenView()

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
        geraete_view.visualize (self)
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


    def onAction(self, action):
        """
        handles window exits
        # ACTION_LAST_PAGE = 160
        #ACTION_NAV_PREV = 92
        """
        BACKSPACE = 61448
        ARROW_LEFT = 61570
        view = self.currentView.get_id()
        is_geraeteview = self.__is_geraeteview(view)
        if self.getFocusId() == 3 and (action.getButtonCode() == 61453 or action == 100 or action == 135):#Gerätetyptabelle
            #self._wait_for_visualization = True
            geraetetyp_list = self.getControl(3)
            position = geraetetyp_list.getSelectedPosition()
            next_view = self.currentView.handle_click(position)
            if next_view is not None:
                self.currentView.remove_everything(self)
                geraete_view = homepilot_views.ParametrizedGeraeteView(self.client, next_view)
                menu_control = self.window.getControl(96)
                geraete_view.visualize(self)
                self.currentView = geraete_view
                self.status_updater.set_current_view(geraete_view, menu_control)
        elif self.getFocusId() == 999 and action == 31:
            self.setFocusId(5)
        elif action == 13 or action == 10 or action == 160 or action == 21:
            self.shutdown()
        elif action == 92 and view == FAVORITEN_VIEW:
            self.setFocusId(95)
        elif action == 92 and view == GERAETETYP_VIEW:
            self.setFocusId(96)
        elif action == 92 and view == SENSOREN_VIEW:
            self.setFocusId(97)
        elif is_geraeteview and self.getFocusId() != 999 and (action.getButtonCode() == BACKSPACE or action.getButtonCode() == ARROW_LEFT):
            self.__show_geraetetyp_view()
            self.__set_geraetetyp_list_focus(view)
            self.setFocusId(3)
        if self.getFocusId() == 0:
            if view == FAVORITEN_VIEW or view == SENSOREN_VIEW or is_geraeteview:
                self.setFocusId(5)
                #pass
            elif view == GERAETETYP_VIEW:
                self.setFocusId(3)
            else:
                self.setFocusId(95)



    def onFocus(self, control):
        if not self._wait_for_visualization:
            if control == 98: #menüpunkt Einstellungen
                if self.currentView.get_id() != EMPTY_VIEW:
                    self.currentView.remove_everything (self)
                    empty_view = homepilot_views.EmptyView()
                    menu_control = self.window.getControl(98)
                    empty_view.visualize(self)
                    self.currentView = empty_view
                    self.status_updater.set_current_view(empty_view, menu_control)
            elif control == 95: #Menüpunkt Favoriten
                if self.currentView.get_id() != FAVORITEN_VIEW:
                    self.currentView.remove_everything (self)
                    geraete_view = homepilot_views.ParametrizedGeraeteView(self.client, FAVORITEN)
                    menu_control = self.window.getControl(95)
                    geraete_view.visualize (self)
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
                    geraete_view.visualize (self)
                    self.currentView = geraete_view
                    self.status_updater.set_current_view(geraete_view, menu_control)
            elif control == 94: # Menüpunkt Szenen
                if self.currentView.get_id() != SZENEN_VIEW:
                    self.currentView.remove_everything (self)
                    self.currentView = self.szenenView
                    self.currentView.visualize (self)


    def onClick(self, control):
        xbmc.log("onClick " + str(control), level=xbmc.LOGNOTICE)
        if control == 5:
            view_id = self.currentView.get_id()
            if view_id == SENSOREN + "_view":
                geraete_listcontrol = self.getControl(5)
                list_item = geraete_listcontrol.getSelectedItem()
                did = list_item.getProperty("did")
                device_window = MeterWindow('device_window.xml', home, client=self.client, did=did, parent=self)
                device_window.doModal()
            elif view_id == FAVORITEN + "_view" or view_id == ALLE_VIEW or view_id == ROLLADEN_VIEW \
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


    def __set_geraetetyp_list_focus (self, previeous_view):
        list_control = self.window.getControl(3)
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



    def __show_geraetetyp_view(self):
        self.currentView.remove_everything (self)
        geraetetyp_view = homepilot_views.GeraetetypView(self.client)
        menu_control = self.window.getControl(96)
        menu_control.controlRight(self.window.getControl(3))
        geraetetyp_view.visualize (self)
        self.currentView = geraetetyp_view
        self.status_updater.set_current_view(geraetetyp_view, menu_control)


    def __open_device_window(self, did):
        try:
            device = self.client.get_device_by_id(did)
            dgroup = device.get_devicegroup()
            if dgroup == 2 or dgroup == 4 or dgroup == 8:
                percent_window = PercentageWindow('device_window.xml', home, client=self.client, device=device,parent=self)
                self.status_updater.set_current_window(percent_window)
                percent_window.doModal()
            elif dgroup == 1:
                switch_window = SwitchWindow('device_window.xml', home, client=self.client, device=device, parent=self)
                self.status_updater.set_current_window(switch_window)
                switch_window.doModal()
            elif dgroup == 5:
                percent_window = DegreeWindow('device_window.xml', home, client=self.client, device=device, parent=self)
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

