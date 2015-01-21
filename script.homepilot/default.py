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

# tail -f /home/root/.xbmc/temp/xbmc.log | grep PMM---
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
            #xbmc.log("---default.py-- run", level=xbmc.LOGNOTICE)
            if self.current_window is not None:
                #this is a pretty sloppy implementation, as the window is updated even when it isn't display anymore
                #I've choosen this way as I didn't find a method for getting the current state of a xbmcgui.WindowXMLDialog
                #and the possible alternatives(e.g. passing references of this class around) looked more error prone
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
        
    # Helper Funktion für Debugging
    def getViewstring(self, view):
        if view == FAVORITEN_VIEW:
            return "Favoriten View"
        elif view == FAVORITEN_LOKAL_VIEW:
            return "Favoriten Lokal View"
        elif view == GERAETETYP_VIEW:
            return "Geraetetyp View"
        elif view == SZENENTYP_VIEW:
           return "Szenentyp View"
        elif view == SZENEN_MANUELL_VIEW:
            return "Szenen Manu View"
        elif view == SZENEN_NICHT_MANUELL_VIEW:
            return "Szenen nicht Manu View"
        elif view == SZENEN_ALLE_VIEW:
            return "Szenen alle View"
        elif view == SENSOREN_VIEW:
            return "Sensoren View"
        elif view == EMPTY_VIEW:
            return "Einstellungen View"
        else:
            return "unbekannt:" + str(view)
            
    # Helper Funktion für Debugging    
    def getFocusIdstring(self, id):
        if id == FOCUS_LIST_FAV:
            return "FavMenü"
        elif id == FOCUS_LIST_DEVICES:
            return "GeraeteMenu"
        elif id == FOCUS_LIST_DEVICE_TYP:
            return "Geraetetypen"
        elif id == FOCUS_LIST_DEVICE_GROUP:
            return "GeraeteGruppen"
        elif id == FOCUS_LIST_SCENES:
            return "SzenenMenü"
        elif id == FOCUS_LIST_SENSOR:
            return "SensorMenue"
        elif id == FOCUS_LIST_CONFIG:
            return "ConfigMenue"
        elif id == FOCUS_LIST_SENSORLIST:
            return "Sensorliste"
        elif id == FOCUS_LIST_FAVLIST_AKTOREN:
            return "FavAktorenliste"
        elif id == FOCUS_LIST_FAVLIST_SZENEN:
            return "FavSzenenliste"
        elif id == FOCUS_LIST_SCENE_LIST:
            return "SzenenTypliste"
        elif id == FOCUS_SCROLL_FAVLIST_DEV:
            return "Scrollbar FavList Aktoren"
        elif id == FOCUS_SCROLL_FAVLIST_SCN:
            return "Scrollbar FavList Szenen"
        elif id == FOCUS_SCROLL_DEVGROUP:
            return "Scrollbar Geraetetyp Aktoren"
        elif id == FOCUS_SCROLL_DEVLIST:
            return "Scrollbar Aktoren,Sensoren"
        elif id == FOCUS_SCROLL_SCENELIST:
            return "Scrollbar Szenen"
        #elif id == FOCUS_SCROLL_DEVTYP:
        #    return "SzenenTypliste"
        else:
            return "unbekannt:" + str(id)
    
    # Helper Funktion für Debugging
    def getButtonCodestring(self, button):
        if button == HP_VK_DOWN:
            return "VK Down"
        elif button == HP_VK_UP:
            return "VK Up"
        elif button == HP_VK_LEFT:
            return "VK Left"
        elif button == HP_VK_RIGHT:
            return "VK Right"
        elif button == HP_VK_ENTER:
            return "VK Enter"
        elif button == HP_VK_BACK:
            return "VK Back"
        elif button == HP_VK_ESC:
            return "VK ESC"
        elif button == HP_CEC_DOWN:
            return "CEC Down"
        elif button == HP_CEC_UP:
            return "CEC Up"
        elif button == HP_CEC_LEFT:
            return "CEC Left"
        elif button == HP_CEC_RIGHT:
            return "CEC Right"
        elif button == HP_CEC_ENTER:
            return "CEC Ok"
        elif button == HP_CEC_BACK:
            return "CEC Exit"
        else:
            return "unbekannt:" + str(button)
            
    # Helper Funktion für Debugging
    def getActionIDstring(self, actionid):            
        if actionid == AID_DOWN:
            return "Down"
        elif actionid == AID_UP:
            return "Up"
        elif actionid == AID_LEFT:
            return "Left"
        elif actionid == AID_RIGHT:
            return "Right"
        elif actionid == AID_ENTER:
            return "Enter"
        elif actionid == AID_BACK:
            return "Back"
        elif actionid == AID_ESC:
            return "ESC"
        else:
            return "unbekannt:" + str(actionid)
    
            
    # Helper Funktion um Quellcode besser lesen zu können
    def switchDevicetypeBack(self, view, focusid):
        self.__show_geraetetyp_view()
        self.__set_geraetetyp_list_focus(view)
        self.setFocusId(focusid)
            
    # Helper Funktion um Quellcode besser lesen zu können
    def isKeyBackbutton(self, button):
        return button == HP_VK_BACK or button == HP_VK_LEFT or button == HP_CEC_BACK or button == HP_CEC_LEFT
        
    def isActionBack(self, actionid):
        return actionid == AID_LEFT or actionid == AID_BACK
        
    # Helper Funktion um Quellcode besser lesen zu können
    def isKeyEnterbutton(self, button):
        return button == HP_CEC_ENTER or button == MOUSE_LEFT_CLICK or button == HP_VK_ENTER

    def isActionEnter(self, actionid):
        return actionid == AID_ENTER
        
    # Eventhandling
    def onAction(self, action):
        view = self.currentView.get_id()
        focusid = self.getFocusId()
        
        # Debug Log Start Event Handling
        xbmc.log("PMM---default.py-- START View: " + self.getViewstring(view) + " - Action: " + self.getActionIDstring(action.getId()) + " - FocusId: " +  self.getFocusIdstring(focusid) + " - Szene: " + str(self._isScene), level=xbmc.LOGNOTICE)
            
        #Shutdown ermöglichen, wenn in oberer Schicht
        if focusid == FOCUS_LIST_FAV or focusid == FOCUS_LIST_DEVICES or focusid == FOCUS_LIST_SCENES or focusid == FOCUS_LIST_SENSOR or focusid == FOCUS_LIST_CONFIG:
            if action.getId() == AID_BACK:
                xbmc.log("PMM---default.py-- shutdown via FocusID", level=xbmc.LOGNOTICE)
                self.shutdown()
        # Mit ESC wird Addon komplett geschlossen
        if action.getId() == AID_ESC:
            xbmc.log("PMM---default.py-- shutdown via ESC", level=xbmc.LOGNOTICE)
            self.shutdown()
    
        #Menüsteuerung
        #Favoriten
        if view == FAVORITEN_VIEW or view == FAVORITEN_LOKAL_VIEW:
            if self.isActionBack(action.getId()):
                self.switchDevicetypeBack(view, FOCUS_LIST_FAV)
        elif view == GERAETETYP_VIEW:
            if not self.isActionBack(action.getId()):
                if focusid == FOCUS_LIST_DEVICES:
                    self._isScene = False
                elif focusid == FOCUS_LIST_SCENES:
                    self._isScene = True
            if self.isActionBack(action.getId()):
                if self._isScene == False:
                    self.setFocusId(FOCUS_LIST_DEVICES)
                else:
                    self.setFocusId(FOCUS_LIST_SCENES)
            elif self.isActionEnter(action.getId()):
                if self._isScene == False:
                    self.__on_action_geraetetypview(action)
                else:
                    xbmc.log("PMM--- Enter hilfe Quellcode schauen", level=xbmc.LOGNOTICE)
        elif view == DEVICE_ROLLADEN_VIEW:
            if self.isActionBack(action.getId()):
                self.switchDevicetypeBack(view, FOCUS_LIST_DEVICE_TYP)
        elif view == DEVICE_SCHALTER_VIEW:
            if self.isActionBack(action.getId()):
                self.switchDevicetypeBack(view, FOCUS_LIST_DEVICE_TYP)
        elif view == DEVICE_DIMMER_VIEW:
            if self.isActionBack(action.getId()):
                self.switchDevicetypeBack(view, FOCUS_LIST_DEVICE_TYP)
        elif view == DEVICE_THERMOSTATE_VIEW:
            if self.isActionBack(action.getId()):
                self.switchDevicetypeBack(view, FOCUS_LIST_DEVICE_TYP)
        elif view == DEVICE_TORE_VIEW:
            if self.isActionBack(action.getId()):
                self.switchDevicetypeBack(view, FOCUS_LIST_DEVICE_TYP)
        elif view == DEVICE_ALLE_VIEW:
            if self.isActionBack(action.getId()):
               self.switchDevicetypeBack(view, FOCUS_LIST_DEVICE_TYP)
        elif view == DEVICE_GRUPPEN_VIEW:
            if self.isActionBack(action.getId()):
                group_id = self.currentView.get_group()
                self.__show_geraetetyp_view()
                self.__set_gruppen_list_focus(group_id)
        #Szenen
        elif view == SZENENTYP_VIEW:
            self._isScene = True
            if self.isActionBack(action.getId()):
                self.setFocusId(FOCUS_LIST_SCENES)
            elif self.getFocusId() == FOCUS_LIST_DEVICE_TYP and self.isActionEnter(action.getId()):#Gerätetyptabelle
                type_list = self.getControl(FOCUS_LIST_DEVICE_TYP)
                item = type_list.getSelectedItem()
                next_view = self.currentView.handle_click(item)
                self.currentView.remove_everything(self)
                szenen_view = homepilot_views.SzenenListView(self.client, next_view)
                menu_control = self.getControl(FOCUS_LIST_SCENES)
                szenen_view.visualize(self, __addon__)
                self.currentView = szenen_view
                self.status_updater.set_current_view(szenen_view, menu_control)
        elif view == SZENEN_MANUELL_VIEW:
            if self.isActionBack(action.getId()):
                self.setFocusId(FOCUS_LIST_SCENES)
            elif self.isActionEnter(action.getId()):
                self.setFocusId(FOCUS_LIST_SENSORLIST)
        elif view == SZENEN_NICHT_MANUELL_VIEW:
            if self.isActionBack(action.getId()):
                self.setFocusId(FOCUS_LIST_SCENES)
            elif self.isActionEnter(action.getId()):
                self.setFocusId(FOCUS_LIST_SENSORLIST)
        elif view == SZENEN_ALLE_VIEW:
            if self.isActionBack(action.getId()):
                self.setFocusId(FOCUS_LIST_SCENES)
            elif self.isActionEnter(action.getId()):
                self.setFocusId(FOCUS_LIST_SENSORLIST)
        #Sensoren
        elif view == SENSOREN_VIEW:
            if self.isActionBack(action.getId()):
                self.setFocusId(FOCUS_LIST_SENSOR)
        #Einstellungen
        #elif view == EMPTY_VIEW:
 
        #XBMC has lost focus, set a new one
        if self.getFocusId() == 0 and action.getButtonCode() != 0:
            xbmc.log("PMM---default.py-- focus lost", level=xbmc.LOGNOTICE)
            if view == SENSOREN_VIEW:
                self.setFocusId(5)
            elif view == FAVORITEN_VIEW or view == FAVORITEN_LOKAL_VIEW:
                self.setFocusId(255)
            elif view == GERAETETYP_VIEW:
                self.setFocusId(257)
            else:
                self.setFocusId(95)
        
        # Debug Log END Event Handling
        xbmc.log("PMM---default.py-- ENDE View: " + self.getViewstring(view) + " - Action: " + self.getActionIDstring(action.getId()) + " - FocusId: " +  self.getFocusIdstring(focusid) + " - Szene: " + str(self._isScene), level=xbmc.LOGNOTICE)
        #xbmc.log("PMM---default.py-- ENDE View: " + self.getViewstring(view) + " - Action: " + self.getActionIDstring(action.getId()) + " - Key: " + self.getButtonCodestring(action.getButtonCode()) + " - FocusId: " +  self.getFocusIdstring(focusid) + " - Szene: " + str(self._isScene), level=xbmc.LOGNOTICE)

    def __on_action_geraetetypview (self, action):
        if self.getFocusId() == FOCUS_LIST_DEVICE_TYP:
            # Einmal tiefer ins Menü
            if self.isActionEnter(action.getId()):#Gerätetyptabelle
                gruppen_list = self.getControl(FOCUS_LIST_DEVICE_TYP)
                position = gruppen_list.getSelectedItem()
                next_view = self.currentView.handle_click(position)
                if next_view is not None:
                    self.currentView.remove_everything(self)
                    geraete_view = homepilot_views.ParametrizedGeraeteView(self.client, next_view)
                    menu_control = self.getControl(FOCUS_LIST_DEVICES)
                    geraete_view.visualize(self, __addon__)
                    self.currentView = geraete_view
                    self.status_updater.set_current_view(geraete_view, menu_control)
        elif self.getFocusId() == FOCUS_LIST_DEVICE_GROUP:
            # Einmal tiefer ins Menü
            if self.isActionEnter(action.getId()):#Gruppentabelle
                gruppen_list = self.getControl(FOCUS_LIST_DEVICE_GROUP)
                position = gruppen_list.getSelectedPosition()
                list_item = gruppen_list.getListItem(position)
                gruppen_id = list_item.getProperty("gid")
                gruppen_name = list_item.getLabel()
                self.currentView.remove_everything(self)
                geraete_view = homepilot_views.ParametrizedGeraeteView(self.client, GRUPPEN, gruppen_id)
                menu_control = self.getControl(FOCUS_LIST_DEVICES)
                geraete_view.visualize(self, __addon__, gruppen_name)
                self.currentView = geraete_view
                self.status_updater.set_current_view(geraete_view, menu_control)
    
    def __on_action_scenetypview (self, action):
        if self.getFocusId() == FOCUS_LIST_DEVICE_TYP:
            # Einmal tiefer ins Menü
            if self.isActionEnter(action.getId()):#Gerätetyptabelle
                gruppen_list = self.getControl(FOCUS_LIST_DEVICE_TYP)
                position = gruppen_list.getSelectedItem()
                next_view = self.currentView.handle_click(position)
                if next_view is not None:
                    self.currentView.remove_everything(self)
                    geraete_view = homepilot_views.ParametrizedGeraeteView(self.client, next_view)
                    menu_control = self.getControl(FOCUS_LIST_DEVICES)
                    geraete_view.visualize(self, __addon__)
                    self.currentView = geraete_view
                    self.status_updater.set_current_view(geraete_view, menu_control)

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
                meter_window.doModal()
                self.status_updater.set_current_window(meter_window)
            elif view_id == DEVICE_ALLE_VIEW or view_id == DEVICE_ROLLADEN_VIEW or view_id == DEVICE_SCHALTER_VIEW or view_id == DEVICE_DIMMER_VIEW \
                or view_id == DEVICE_THERMOSTATE_VIEW or view_id == DEVICE_TORE_VIEW:
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
        list_control = self.getControl(4)
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

