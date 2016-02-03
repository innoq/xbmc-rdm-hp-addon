#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import threading
import time

import xbmc
import xbmcaddon
import xbmcgui
from resources.lib import homepilot_client
from resources.lib import settings
from resources.lib import statics
from resources.lib.Views.empty_view import EmptyView
from resources.lib.Views.favoriten_view import FavoritenView
from resources.lib.Views.geraetetyp_view import GeraetetypView
from resources.lib.Views.parametrized_geraete_view import ParametrizedGeraeteView
from resources.lib.Views.szenen_list_view import SzenenListView
from resources.lib.Views.szenentyp_view import SzenentypView
from resources.lib.Windows.degree_window import DegreeWindow
from resources.lib.Windows.error_window import ErrorWindow
from resources.lib.Windows.meter_window import MeterWindow
from resources.lib.Windows.percentage_window import PercentageWindow
from resources.lib.Windows.switch_window import SwitchWindow
from resources.lib.Windows import scene_window as szene

"""
Implementation of an XBMC Script Addon

This addon displays the current state of a Rollo or Switch device
and offers buttons to change ist.
"""

__addon__ = xbmcaddon.Addon(id='script.homepilot')
__cwd__ = xbmc.translatePath(__addon__.getAddonInfo('path').decode("utf-8"))

# add lib directory to sys.path as this doesn't happen automatically
__resource__ = xbmc.translatePath(os.path.join(__cwd__, 'resources', 'lib').decode("utf-8"))
sys.path.append(__resource__)


# tail -f /home/root/.xbmc/temp/xbmc.log | grep PMM---
# ps aux | grep xbmc.bin

class StatusUpdater(threading.Thread):
    def __init__(self, initialView, menuControl, title, x):
        xbmc.log("PMM--- StatusUpdater: __init__", level=xbmc.LOGDEBUG)
        self.window = window
        threading.Thread.__init__(self)
        self.currentView = initialView
        self.menuControl = menuControl
        self.is_running = True
        self.current_window = None
        self.title = title

    def set_current_view(self, currentView, menuControl):
        xbmc.log("PMM--- StatusUpdater: set_currentView: currentView:" + str(currentView) + " menuControl: " + str(
            menuControl), level=xbmc.LOGDEBUG)
        self.currentView = currentView
        self.menuControl = menuControl

    def set_current_window(self, currentWindow):
        xbmc.log("PMM--- StatusUpdater: set_current_window: currentWindow: " + str(currentWindow), level=xbmc.LOGDEBUG)
        self.current_window = currentWindow

    def run(self):
        """
        run läuft alle 1,5 Sekunden und ruft die Updatemethode des aktuellen Windows und der aktuellen View auf.
        """
        self.is_running = True
        self.currentView.visualize(self.window, __addon__, self.title)
        views = [statics.FAVORITEN_VIEW, statics.FAVORITEN_LOKAL_VIEW,
                 statics.DEVICE_ROLLADEN_VIEW, statics.DEVICE_DIMMER_VIEW,
                 statics.DEVICE_SCHALTER_VIEW, statics.DEVICE_THERMOSTATE_VIEW,
                 statics.DEVICE_TORE_VIEW, statics.SENSOREN_VIEW, statics.DEVICE_ALLE_VIEW]
        while self.is_running:
            time.sleep(1.5)
            xbmc.log("PMM--- StatusUpdater: run: is_running", level=xbmc.LOGDEBUG)
            if self.currentView is not None and self.current_window is not None:
                xbmc.log("PMM--- StatusUpdater: run: \n" +
                         "Window: " + repr(self.current_window) + "\n" +
                         "View: " + repr(self.currentView),
                         level=xbmc.LOGDEBUG)
                self.current_window.update()
                v_id = self.currentView.get_id()
                if v_id in views:
                    self.currentView.update(self.window, __addon__, self.menuControl)
            elif self.currentView is not None:
                v_id = self.currentView.get_id()
                xbmc.log("PMM--- StatusUpdater: run: No Window but a view. \nView: " + repr(self.currentView) +
                         "\nv_id: " + repr(v_id), level=xbmc.LOGDEBUG)
                if v_id in views:
                    self.currentView.update(self.window, __addon__, self.menuControl)
            else:
                xbmc.log("PMM--- StatusUpdater: run: No window or view.", level=xbmc.LOGDEBUG)


class GuiController(xbmcgui.WindowXMLDialog):
    """
    representing a window with the HomePilot controls
    """

    def __init__(self, *args, **kwargs):
        """
        constructor of the class
        """
        xbmc.log("PMM--- GuiController: __init__", level=xbmc.LOGDEBUG)
        xbmcgui.WindowXMLDialog.__init__(self, *args, **kwargs)
        self.settings_dialog_manager = settings.SettingsDialogManager()
        ip_address = self.settings_dialog_manager.get_ip_address(__addon__)
        self.client = homepilot_client.HomepilotClient(ip_address)
        self._wait_for_visualization = False
        uselocalfavorites = self.settings_dialog_manager.use_local_favorites(__addon__)
        if uselocalfavorites == "true":
            self.uselocalfavorites_bool = True
        else:
            self.uselocalfavorites_bool = False
        xbmc.log("PMM--- GuiController: __init__: uselocalfavorites_bool: " + repr(self.uselocalfavorites_bool),
                 level=xbmc.LOGDEBUG)
        self.currentView = None
        self.status_updater = None

    def onInit(self):
        """
        initializes the window
        """
        self.setProperty('windowLabel', __addon__.getLocalizedString(32383))
        menu_control = self.getControl(statics.FOCUS_LIST_FAV)
        xbmc.log("PMM--- GuiController: onInit: localfavorites: " + repr(self.uselocalfavorites_bool),
                 level=xbmc.LOGDEBUG)
        if self.uselocalfavorites_bool:
            favoriten_view = FavoritenView(self.client, self.uselocalfavorites_bool, menu_control)
        else:
            favoriten_view = FavoritenView(self.client, self.uselocalfavorites_bool, menu_control)
        title = self.__get_favorite_view_title(self.uselocalfavorites_bool)

        self.setFocus(menu_control)
        self.currentView = favoriten_view
        self.status_updater = StatusUpdater(favoriten_view, menu_control, title, self)
        self.status_updater.start()

    def shutdown(self):
        """
        closes the window
        """
        self.status_updater.is_running = False
        self.close()

    def __get_favorite_view_title(self, useLocalFavorites):
        """
        Abhängig von der gewählten Favoritenart, wird ein Titel gewählt.
        :param useLocalFavorites:
        :return:
        """
        xbmc.log("PMM--- GuiController: __get_favorite_view_title: useLocalFavorites: " + repr(useLocalFavorites),
                 level=xbmc.LOGDEBUG)
        label = __addon__.getLocalizedString(32004)
        if useLocalFavorites:
            fav_id = 32385
        else:
            fav_id = 32382
        label += " (" + __addon__.getLocalizedString(fav_id) + ")"
        xbmc.log("PMM--- GuiController: __get_favorite_view_title: id: " + repr(fav_id) + " label: " + repr(label),
                 level=xbmc.LOGDEBUG)
        return label

    # Helper Funktion um Quellcode besser lesen zu können
    def switchDevicetypeBack(self, view, focusid):
        """
        Funktion um die Gerätetypenliste anzuzeigen, nachdem man von der Geräteliste zurück geht.
        :param view:
        :param focusid:
        :return:
        """
        self.__show_geraetetyp_view()
        self.__set_geraetetyp_list_focus(view)
        self.setFocusId(focusid)

    # Helper Funktion um Quellcode besser lesen zu können
    def isKeyBackbutton(self, button):
        xbmc.log("PMM--- GuiController: isKeyBackbutton button: " + repr(button), level=xbmc.LOGDEBUG)
        return button == statics.HP_VK_BACK or button == statics.HP_VK_LEFT or button == statics.HP_CEC_BACK or button == statics.HP_CEC_LEFT

    def isActionBack(self, actionid):
        # Left Button pressed
        xbmc.log("PMM--- GuiController: isActionBack actionid: " + repr(actionid), level=xbmc.LOGDEBUG)
        return actionid == statics.AID_LEFT or actionid == statics.AID_BACK or actionid == statics.ACTION_NAV_BACK

    # Helper Funktion um Quellcode besser lesen zu können
    def isKeyEnterbutton(self, button):
        xbmc.log("PMM--- GuiController: isKeyEnterbutton button: " + repr(button), level=xbmc.LOGDEBUG)
        return button == statics.HP_CEC_ENTER or button == statics.MOUSE_LEFT_CLICK or button == statics.HP_VK_ENTER

    def isActionEnter(self, actionid):
        xbmc.log("PMM--- GuiController: isActionEnter actionid: " + repr(actionid), level=xbmc.LOGDEBUG)
        return actionid == statics.AID_ENTER

    # Eventhandling
    def onAction(self, action):
        """
        Wird aufgerufen wenn eine Action (Taste) ausgeführt wird.
        :param action:
        :return:
        """
        view = self.currentView.get_id()
        focusid = self.getFocusId()
        deviceset = statics.DEVICESET
        scene_set = statics.SCENE_SET
        action_id = action.getId()
        # Shutdown ermöglichen, wenn in oberer Schicht
        self.on_action_shutdown(focusid, action_id)

        xbmc.log("PMM--- GuiController: onAction: \nview: " + str(view) +
                 "\naction:" + repr(action.getId()) +
                 "\nfocusid: " + repr(focusid), level=xbmc.LOGDEBUG)

        # Menüsteuerung, abhängig von der aktuellen View wird eine Methode geöffnet, die den aktuellen Focus,
        # also die Auswahl, und die gedrückte Taste, Action, bekommt.
        if view == statics.FAVORITEN_VIEW or view == statics.FAVORITEN_LOKAL_VIEW:  # Favoriten
            self.on_action_favoriten(action_id, focusid)
        elif view == statics.GERAETETYP_VIEW:  # Geräte
            self.on_action_geraetetyp_view(action_id, focusid)
        elif view in deviceset:  # Ein Device ist offen
            self.on_action_deviceset(action_id, focusid, view)
        elif view == statics.DEVICE_GRUPPEN_VIEW: #Gerätegruppen
            self.on_action_device_gruppen_view(action_id, focusid)
        elif view in scene_set:  # Szene offen
            self.on_action_szene_set(action_id, focusid)
        elif view == statics.SZENENTYP_VIEW:
            self.on_action_szenentypview(action_id, focusid)
        elif view == statics.SENSOREN_VIEW:  # Sensoren
            self.on_action_sensoren_view(action_id, focusid)

        # XBMC has lost focus, set a new one
        if self.getFocusId() == 0 and action.getButtonCode() != 0:
            self.on_action_focuslost(view)

    def on_action_favoriten(self, action_id, focusid):
        xbmc.log("PMM--- GuiController: on_action_favoriten", level=xbmc.LOGDEBUG)
        if self.isActionBack(action_id):
            if focusid == statics.FOCUS_LIST_FAV: # Zurück ins Menü
                self.setFocusId(statics.FOCUS_LIST_FAV)

    def on_action_geraetetyp_view(self, action_id, focusid):
        xbmc.log("PMM--- GuiController: on_action_geraetetyp_view", level=xbmc.LOGDEBUG)
        if self.isActionBack(action_id):
            if focusid == statics.FOCUS_LIST_DEVICE_TYP:
                self.setFocusId(statics.FOCUS_LIST_DEVICES)
        elif self.isActionEnter(action_id):
            if focusid == statics.FOCUS_LIST_DEVICE_TYP:
                self.focus_list_device_typ()
            elif focusid == statics.FOCUS_LIST_DEVICE_GROUP:
                self.focus_list_device_group()

    def on_action_deviceset(self, action_id, focusid, view):
        xbmc.log("PMM--- GuiController: on_action_deviceset", level=xbmc.LOGDEBUG)
        if self.isActionBack(action_id):
            if focusid == statics.FOCUS_SCROLL_DEVLIST:
                con = self.getControl(statics.FOCUS_LIST_SENSORLIST)
                self.setFocus(con)
            elif focusid != statics.FOCUS_SCROLL_SCENELIST:
                self.switchDevicetypeBack(view, statics.FOCUS_LIST_DEVICE_TYP)

    def on_action_device_gruppen_view(self, action_id, focusid):
        xbmc.log("PMM--- GuiController: on_action_device_gruppen_view", level=xbmc.LOGDEBUG)
        if self.isActionBack(action_id):
            group_id = self.currentView.get_id()
            self.__set_gruppen_list_focus(group_id)

    def on_action_szene_set(self, action_id, focusid):
        xbmc.log("PMM--- GuiController: on_action_szene_set", level=xbmc.LOGDEBUG)
        if self.isActionBack(action_id):
            if focusid == statics.FOCUS_LIST_SCENE_LIST:
                scene_id = self.currentView.stype
                self.__set_scenen_list_focus(scene_id)
            if focusid == statics.FOCUS_SCROLL_SCENELIST:
                controll = self.getControl(statics.FOCUS_LIST_SCENE_LIST)
                self.setFocus(controll)
        elif self.isActionEnter(action_id):
            self.setFocusId(statics.FOCUS_LIST_SCENES)

    def on_action_sensoren_view(self, action_id, focusid):
        xbmc.log("PMM--- GuiController: on_action_sensoren_view", level=xbmc.LOGDEBUG)
        if self.isActionBack(action_id):
            if focusid == statics.FOCUS_LIST_SENSOR:
                self.setFocusId(statics.FOCUS_LIST_SENSOR)
            elif focusid == statics.FOCUS_SCROLL_DEVLIST:
                con = self.getControl(statics.FOCUS_LIST_SENSORLIST)
                self.setFocus(con)

    def on_action_shutdown(self, focusid, action):
        """
        Ermöglicht den Shutdow, , egal was gerade für eine View oder Fenster präsent sind.
        """
        if focusid in statics.SHUTDOWN_SET:
            if action == statics.AID_BACK or action == statics.ACTION_NAV_BACK:
                xbmc.log("PMM---default.py-- shutdown via FocusID", level=xbmc.LOGNOTICE)
                self.shutdown()
        # Mit ESC wird Addon komplett geschlossen
        if action == statics.AID_ESC:
            xbmc.log("PMM---default.py-- shutdown via ESC", level=xbmc.LOGNOTICE)
            self.shutdown()

    def focus_list_device_typ(self):
        xbmc.log("PMM--- focus_list_device_typ", level=xbmc.LOGDEBUG)
        # Einmal tiefer ins Menü
        gruppen_list = self.getControl(statics.FOCUS_LIST_DEVICE_TYP)
        position = gruppen_list.getSelectedItem()
        next_view = self.currentView.handle_click(position)
        if next_view is not None:
            self.currentView.remove_everything(self)
            geraete_view = ParametrizedGeraeteView(self.client, next_view)
            menu_control = self.getControl(statics.FOCUS_LIST_DEVICES)
            geraete_view.visualize(self, __addon__)
            self.currentView = geraete_view
            self.status_updater.set_current_view(geraete_view, menu_control)

    def focus_list_device_group(self):
        xbmc.log("PMM--- focus_list_device_group", level=xbmc.LOGDEBUG)
        gruppen_list = self.getControl(statics.FOCUS_LIST_DEVICE_GROUP)
        position = gruppen_list.getSelectedPosition()
        list_item = gruppen_list.getListItem(position)
        gruppen_id = list_item.getProperty("gid")
        gruppen_name = list_item.getLabel()
        self.currentView.remove_everything(self)
        geraete_view = ParametrizedGeraeteView(self.client, statics.GRUPPEN, gruppen_id)
        menu_control = self.getControl(statics.FOCUS_LIST_DEVICES)
        geraete_view.visualize(self, __addon__, gruppen_name)
        self.currentView = geraete_view
        self.status_updater.set_current_view(geraete_view, menu_control)

    def on_action_szenentypview(self, action_id, focus_id):
        xbmc.log("PMM--- GuiController: on_action_szenentypview", level=xbmc.LOGDEBUG)
        if self.isActionBack(action_id):
            self.setFocusId(statics.FOCUS_LIST_SCENES)
        elif self.isActionEnter(action_id):
            type_list = self.getControl(statics.FOCUS_LIST_DEVICE_TYP)
            item = type_list.getSelectedItem()
            next_view = self.currentView.handle_click(item)
            self.currentView.remove_everything(self)
            szenen_view = SzenenListView(self.client, next_view)
            menu_control = self.getControl(statics.FOCUS_LIST_SCENES)
            szenen_view.visualize(self, __addon__)
            self.currentView = szenen_view
            self.status_updater.set_current_view(szenen_view, menu_control)

    def on_action_focuslost(self, view):
        if view == statics.SENSOREN_VIEW:
            xbmc.log("PMM--- GuiController: onAction: LostFocus to 5", level=xbmc.LOGDEBUG)
            self.setFocusId(5)
        elif view == statics.FAVORITEN_VIEW or view == statics.FAVORITEN_LOKAL_VIEW:
            xbmc.log("PMM--- GuiController: onAction: LostFocus to 255", level=xbmc.LOGDEBUG)
            self.setFocusId(255)
        elif view == statics.GERAETETYP_VIEW:
            xbmc.log("PMM--- GuiController: onAction: LostFocus to 257", level=xbmc.LOGDEBUG)
            self.setFocusId(257)
        else:
            xbmc.log("PMM--- GuiController: onAction: LostFocus to 95", level=xbmc.LOGDEBUG)
            self.setFocusId(95)

    def onFocus(self, control):
        """
        Bekommt eine ID (controll) und öffnet die passende View. Das passiert aus dem Hauptmenü.
        :param control:
        :return:
        """
        xbmc.log("PMM--- GuiController: onFocus: control: " + str(control) + " Last View ID: " + str(
            self.currentView.get_id()),
                 level=xbmc.LOGDEBUG)
        if not self._wait_for_visualization and control is not None:
            if control == statics.FOCUS_LIST_CONFIG:  # menüpunkt Einstellungen
                xbmc.log("PMM--- GuiController: onFocus: control: Einstellungen", level=xbmc.LOGDEBUG)
                if self.currentView.get_id != statics.EMPTY_VIEW:
                    self.__show_config_view()
            elif control == statics.FOCUS_LIST_FAV:  # Menüpunkt Favoriten
                xbmc.log("PMM--- GuiController: onFocus: control: Favoriten", level=xbmc.LOGDEBUG)
                if self.currentView.get_id() != statics.FAVORITEN_VIEW and self.currentView.get_id != statics.FAVORITEN_LOKAL_VIEW:
                    self.__show_favoriten_view()
            elif control == statics.FOCUS_LIST_DEVICES:  # Menüpunkt Geräte
                xbmc.log("PMM--- GuiController: onFocus: control: Geräte", level=xbmc.LOGDEBUG)
                if self.currentView.get_id() != statics.GERAETETYP_VIEW:
                    self.__show_geraetetyp_view()
            elif control == statics.FOCUS_LIST_SCENES:  # Menüpunkt Szenentypen
                xbmc.log("PMM--- GuiController: onFocus: control: Szenentypen", level=xbmc.LOGDEBUG)
                if self.currentView.get_id() != statics.SZENENTYP_VIEW:
                    self.__show_szenentyp_view()
            elif control == statics.FOCUS_LIST_SENSOR:  # Menüpunkt sensoren
                xbmc.log("PMM--- GuiController: onFocus: control: Sensoren", level=xbmc.LOGDEBUG)
                if self.currentView.get_id() != statics.SENSOREN_VIEW:
                    geraete_view = ParametrizedGeraeteView(self.client, statics.SENSOREN)
                    self.currentView.remove_everything(self)
                    menu_control = self.getControl(statics.FOCUS_LIST_SENSOR)
                    geraete_view.visualize(self, __addon__)
                    self.currentView = geraete_view
                    self.status_updater.set_current_view(geraete_view, menu_control)
            else:
                xbmc.log("PMM--- GuiController: onFocus: Keine neue View. ", level=xbmc.LOGDEBUG)

    def onClick(self, control):
        """
        Öffnet ein Window für ein Gerät oder eine Szene.
        :param control:
        :return:
        """
        view_id = self.currentView.get_id()
        xbmc.log("PMM--- GuiController: onClick: " + str(control) +
                 "\nview_id: " + repr(view_id), level=xbmc.LOGDEBUG)

        if control == statics.FOCUS_LIST_SENSORLIST:
            xbmc.log("PMM--- GuiController: onClick: FOCUS_LIST_SENSORLIST", level=xbmc.LOGDEBUG)
            geraete_listcontrol = self.getControl(statics.FOCUS_LIST_SENSORLIST)
            list_item = geraete_listcontrol.getSelectedItem()
            did = list_item.getProperty(statics.DID)
            if view_id == statics.SENSOREN_VIEW:
                meter_window = MeterWindow('device_window.xml', __cwd__, client=self.client, did=did, parent=self)
                self.status_updater.set_current_window(meter_window)
                meter_window.doModal()
            elif view_id == statics.DEVICE_ALLE_VIEW or view_id == statics.DEVICE_ROLLADEN_VIEW or \
                            view_id == statics.DEVICE_SCHALTER_VIEW or view_id == statics.DEVICE_DIMMER_VIEW \
                    or view_id == statics.DEVICE_THERMOSTATE_VIEW or view_id == statics.DEVICE_TORE_VIEW \
                    or view_id == statics.DEVICE_GRUPPEN_VIEW:
                self.__open_device_window(did)
        elif view_id == statics.FAVORITEN_VIEW or view_id == statics.FAVORITEN_LOKAL_VIEW:
            xbmc.log("PMM--- GuiController: onClick: FAVORITEN_VIEW", level=xbmc.LOGDEBUG)
            if control == statics.FOCUS_LIST_FAVLIST_AKTOREN:
                geraete_listcontrol = self.getControl(statics.FOCUS_LIST_FAVLIST_AKTOREN)
                list_item = geraete_listcontrol.getSelectedItem()
                did = list_item.getProperty(statics.DID)
                self.__open_device_window(did)
            elif control == statics.FOCUS_LIST_FAVLIST_SZENEN:
                scene_list_control = self.getControl(statics.FOCUS_LIST_FAVLIST_SZENEN)
                list_item = scene_list_control.getSelectedItem()
                position = scene_list_control.getSelectedPosition
                sid = list_item.getProperty(statics.SID)
                self.__open_scene_window(sid, position, self.uselocalfavorites_bool)
        elif control == statics.FOCUS_LIST_CONFIG:  # Menüpunkt Einstellungen
            xbmc.log("PMM--- GuiController: onClick: FOCUS_LIST_CONFIG", level=xbmc.LOGDEBUG)
            self._wait_for_visualization = True
            self.settings_dialog_manager.update_ip_address(__addon__)
            ip_address = self.settings_dialog_manager.get_ip_address(__addon__)
            if self.settings_dialog_manager.use_local_favorites(__addon__) == "true":
                self.uselocalfavorites_bool = True
            else:
                self.uselocalfavorites_bool = False
            self._wait_for_visualization = False
            self.client.set_ip_address(ip_address)
        elif control == statics.FOCUS_LIST_SCENE_LIST:  # show szenen detail view
            xbmc.log("PMM--- GuiController: onClick: FOCUS_LIST_SCENE_LIST", level=xbmc.LOGDEBUG)
            scene_list_control = self.getControl(statics.FOCUS_LIST_SCENE_LIST)
            list_item = scene_list_control.getSelectedItem()
            position = scene_list_control.getSelectedPosition()
            sceneId = list_item.getProperty("sid")
            self.__open_scene_window(sceneId, position, self.uselocalfavorites_bool)

    def __set_scenen_list_focus(self, scene_id):
        xbmc.log("PMM--- GuiController: __set_scenen_list_focus: scene_id: " + repr(scene_id), level=xbmc.LOGDEBUG)
        try:
            self.__show_szenentyp_view()
            list_control = self.getControl(257)
            self.setFocus(list_control)
            if scene_id == statics.SZENEN_MANUELL:
                list_control.selectItem(0)
            elif scene_id == statics.SZENEN_NICHT_MANUELL:
                list_control.selectItem(1)
            elif scene_id == statics.SZENEN_ALLE:
                list_control.selectItem(2)
        except ValueError:
            xbmc.log("PMM--- GuiController: __set_scenen_list_focus: ValueError!", level=xbmc.LOGERROR)

    def __set_geraetetyp_list_focus(self, previeous_view):
        xbmc.log("PMM--- GuiController: __set_geraetetyp_list_focus: previeous_view: " + str(previeous_view),
                 level=xbmc.LOGDEBUG)
        list_control = self.getControl(257)
        xbmc.log("PMM--- GuiController: __set_geraetetyp_list_focus: list_control: \n" + str(list_control),
                 level=xbmc.LOGDEBUG)
        try:
            for i in range(0, int(list_control.size())):
                list_item = list_control.getListItem(i)
                type = list_item.getProperty(statics.TYPE)
                if previeous_view == type + "_view":
                    list_control.selectItem(i)
                    return
        except ValueError:
            xbmc.log("PMM--- GuiController: __set_geraetetyp_list_focus: ValueError!", level=xbmc.LOGERROR)

    def __set_gruppen_list_focus(self, gruppen_id):
        xbmc.log("PMM--- GuiController: __set_gruppen_list_focus: gruppen_id:" + str(gruppen_id), level=xbmc.LOGDEBUG)
        list_control = self.getControl(statics.FOCUS_LIST_DEVICE_GROUP)
        i = 0
        run = True
        while run:
            try:
                item = list_control.getListItem(i)
                gid = item.getProperty("gid")
                xbmc.log("PMM--- GuiController: __set_gruppen_list_focus: i:" + repr(i) +
                         "\nGID  " + str(gid) +
                         "\nitem" + repr(item), level=xbmc.LOGDEBUG)
                if gid == str(gruppen_id):
                    list_control.selectItem(i)
                    run = False
                i += 1
            except RuntimeError:
                xbmc.log("PMM--- GuiController: __set_geraetetyp_list_focus: RuntimeError.", level=xbmc.LOGERROR)
                self.setFocusId(statics.FOCUS_LIST_DEVICE_GROUP)
                run = False

    def __show_favoriten_view(self):
        xbmc.log("PMM--- GuiController: __show_favoriten_view: useLocalFav: " + str(
            self.uselocalfavorites_bool) + " currenView: " + repr(self.currentView), level=xbmc.LOGDEBUG)
        self.currentView.remove_everything(self)
        title = self.__get_favorite_view_title(self.uselocalfavorites_bool)
        menu_control = self.getControl(statics.FOCUS_LIST_FAV)
        favoriten_view = FavoritenView(self.client, self.uselocalfavorites_bool, menu_control)
        favoriten_view.visualize(self, __addon__, title)
        self.currentView = favoriten_view
        self.status_updater.set_current_view(favoriten_view, menu_control)

    def __show_geraetetyp_view(self):
        xbmc.log("PMM--- GuiController: __show_geraetetyp_view: ", level=xbmc.LOGDEBUG)
        geraetetyp_view = GeraetetypView(self.client)
        self.currentView.remove_everything(self)
        menu_control = self.getControl(statics.FOCUS_LIST_DEVICES)
        menu_control.controlRight(self.getControl(statics.FOCUS_LIST_DEVICE_TYP))
        geraetetyp_view.visualize(self, __addon__)
        self.currentView = geraetetyp_view
        self.status_updater.set_current_view(geraetetyp_view, menu_control)

    def __show_szenentyp_view(self):
        xbmc.log("PMM--- GuiController: __show_szenentyp_view: ", level=xbmc.LOGDEBUG)
        status_view = SzenentypView()
        menu_control = self.getControl(statics.FOCUS_LIST_SCENES)
        self.currentView.remove_everything(self)
        self.currentView = status_view
        self.status_updater.set_current_view(status_view, menu_control)
        menu_control.controlRight(self.getControl(statics.FOCUS_LIST_DEVICE_TYP))
        self.currentView.visualize(self, __addon__)

    def __show_config_view(self):
        xbmc.log("PMM--- GuiController: __show_config_view: ", level=xbmc.LOGDEBUG)
        self.currentView.remove_everything(self)
        empty_view = EmptyView()
        menu_control = self.getControl(statics.FOCUS_LIST_CONFIG)
        empty_view.visualize(self, __addon__)
        self.currentView = empty_view
        self.status_updater.set_current_view(empty_view, menu_control)

    def __open_device_window(self, did):
        xbmc.log("PMM--- GuiController: __open_device_window: use_local_favs: " + str(
            self.uselocalfavorites_bool) + " did: " + str(did), level=xbmc.LOGDEBUG)
        try:
            device = self.client.get_device_by_id(did)
            dgroup = device.get_devicegroup()
            if dgroup == 2 or dgroup == 4 or dgroup == 8:
                percent_window = PercentageWindow('device_window.xml', __cwd__, client=self.client, device=device,
                                                  parent=self, local_favs=self.uselocalfavorites_bool)
                self.status_updater.set_current_window(percent_window)
                percent_window.doModal()
            elif dgroup == 1:
                percent_window = SwitchWindow('device_window.xml', __cwd__, client=self.client, device=device,
                                              parent=self, local_favs=self.uselocalfavorites_bool)
                self.status_updater.set_current_window(percent_window)
                percent_window.doModal()
            elif dgroup == 5:
                percent_window = DegreeWindow('device_window.xml', __cwd__, client=self.client, device=device,
                                              parent=self, local_favs=self.uselocalfavorites_bool)
                self.status_updater.set_current_window(percent_window)
                percent_window.doModal()
        except Exception, e:
            xbmc.log("PMM--- GuiController: __open_device_window: Fehler beim Öffnen einer Detailsicht: " + str(e.args),
                     level=xbmc.LOGWARNING)
            error_window = ErrorWindow()
            error_window.doModal()

    def __open_scene_window(self, sceneId, position, useLocalFavorites):
        xbmc.log("PMM--- GuiController: __open_scene_window ", level=xbmc.LOGDEBUG)
        scene_window = szene.SzenenDetailWindow('scene_window.xml', __cwd__, client=self.client, scene_id=sceneId,
                                                previous_list_position=position, addon=__addon__, parent=self,
                                                use_local_favorites=useLocalFavorites)
        self.status_updater.set_current_window(scene_window)
        scene_window.doModal()


if __name__ == "__main__":
    xbmc.log("PMM--- default: START ", level=xbmc.LOGDEBUG)
    window = GuiController('homepilot.xml', __cwd__)
    window.doModal()
