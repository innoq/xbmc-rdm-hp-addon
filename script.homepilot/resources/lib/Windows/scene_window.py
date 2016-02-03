#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from .. import statics
from .. import homepilot_utils
from .. import local_favorites
import xbmc
import xbmcaddon
import xbmcgui

__addon__ = xbmcaddon.Addon(id='script.homepilot')
__addon_path__ = __addon__.getAddonInfo('path').decode("utf-8")
_images_device = os.path.join(__addon_path__, 'resources', 'skins', 'Default', 'media', 'devices')
_images = os.path.join(__addon_path__, 'resources', 'skins', 'Default', 'media')

szene_img = os.path.join(_images, 'szene_32.png')
szene_img_deact = os.path.join(_images, 'szene_32_deactivated.png')


class SzenenDetailWindow(xbmcgui.WindowXMLDialog):
    def __init__(self, *args, **kwargs):
        xbmcgui.WindowXMLDialog.__init__(self)
        self.x = 250
        self.y = 40
        self.client = kwargs[statics.CLIENT]
        scene_id = kwargs[statics.SCENE_ID]
        self.scene = self.client.get_scene_by_id(scene_id)
        self.previous_list_position = kwargs[statics.PREVIOUS_LIST_POSITION]
        self.addon = kwargs[statics.ADDON]
        self.parent_window = kwargs[statics.PARENT]
        self.use_local_favorites = kwargs[statics.USE_LOCAL_FAVORITES]
        self.title_control = None
        self.radiobutton_control = None
        self.execcontrol = None
        self.gerate_group_control = None
        self.imagecontrol = None
        self._is_closed = True

    def get_previous_list_position(self):
        return self.previous_list_position

    def onInit(self):
        xbmc.log("SzenenDetailWindow: onInit: ", level=xbmc.LOGDEBUG)
        self.title_control = xbmcgui.ControlLabel(400, 55, 600, 75, self.scene.get_name(), font="font16",
                                                  textColor="white")
        self.radiobutton_control = self.getControl(134)
        self.addControl(self.title_control)
        self.__set_state()

        self.gerate_group_control = self.getControl(146)
        self.gerate_group_control.setPosition(350, 300)
        self.gerate_group_control.setVisible(True)
        self.gerate_group_control.setHeight(100)

        self.execcontrol = xbmcgui.ControlButton(600, 110, 120, 50, self.addon.getLocalizedString(32370))
        self.addControl(self.execcontrol)
        if not self.scene.is_executable():
            self.execcontrol.setVisible(False)

        self.__generate_geraetelist()
        self.__generate_automationlist()
        self.__handle_navigation(self.scene.is_executable())

    def __generate_geraetelist(self):
        xbmc.log("SzenenDetailWindow: __generate_geraetelist: ", level=xbmc.LOGDEBUG)
        self.geraete_list = self.getControl(148)
        actions = self.scene.get_actions_as_list()
        self.geraete_list.reset()
        # show scrollbar only when there are more than two devices
        if len(actions) <= 2:
            xbmc.log("SzenenDetailWindow: __generate_geraetelist: No scrollbar, less than two devices.", level=xbmc.LOGDEBUG)
            xbmc.executebuiltin("SetProperty(show_bar,0,Home)")
        else:
            xbmc.log("SzenenDetailWindow: __generate_geraetelist: Scrollbar, more than two devices.", level=xbmc.LOGDEBUG)
            xbmc.executebuiltin("SetProperty(show_bar,1,Home)")

        self.__add_geraetelistitems(actions, __addon__)

    def __generate_automationlist(self):
        xbmc.log("SzenenDetailWindow: __generate_automationlist: ", level=xbmc.LOGDEBUG)
        self.automation_group_control = self.getControl(138)
        self.automation_group_control.setHeight(100)
        self.automation_list = self.getControl(142)
        self.automation_list.reset()
        automations = self.scene.get_automationen()
        homepilot_utils.add_scene_to_automation_list(self.automation_list, automations, __addon__)

    def __set_state(self):
        xbmc.log("SzenenDetailWindow: __set_state: ", level=xbmc.LOGDEBUG)
        aktiv_button = self.getControl(160)
        is_active = self.scene.is_active()
        aktiv_button.setSelected(is_active)

        if hasattr(self, "imagecontrol") and self.imagecontrol is not None:
            self.removeControl(self.imagecontrol)

        if is_active:
            self.imagecontrol = xbmcgui.ControlImage(400, 100, 64, 64, szene_img)
        else:
            self.imagecontrol = xbmcgui.ControlImage(400, 100, 64, 64, szene_img_deact)

        fav_button = self.getControl(136)
        favored_scenes = local_favorites.get_scenes_as_set()

        if self.use_local_favorites and favored_scenes is not None:
            xbmc.log("SzenenDetailWindow: __set_state: use_local_favorites: " + repr(self.use_local_favorites), level=xbmc.LOGDEBUG)
            if self.scene.get_id() in favored_scenes or self.scene.is_favored():
                fav_button.setSelected(True)
            else:
                fav_button.setSelected(False)
        else:
            fav_button.setSelected(self.scene.is_favored())

        if self.execcontrol is not None:
            if self.scene.is_executable() and hasattr(self, 'execcontrol'):
                self.execcontrol.setVisible(True)
            elif hasattr(self, 'execcontrol'):
                self.execcontrol.setVisible(False)
        else:
            xbmc.log("SzenenDetailWindow: __set_state: execcontrol: " + repr(self.execcontrol.__class__), level=xbmc.LOGDEBUG)
        self.addControl(self.imagecontrol)

    def __handle_navigation(self, exec_button_visible):
        xbmc.log("SzenenDetailWindow: __handle_navigation: ", level=xbmc.LOGDEBUG)
        aktiv_button = self.getControl(160)
        fav_button = self.getControl(136)
        if exec_button_visible:
            self.setFocus(self.execcontrol)
            self.execcontrol.controlDown(self.radiobutton_control)
            aktiv_button.controlUp(self.execcontrol)
        else:
            self.setFocus(aktiv_button)

        if self.geraete_list.size() > 0:
            fav_button.controlDown(self.geraete_list)
            self.automation_list.controlUp(self.geraete_list)
        else:
            fav_button.controlDown(self.automation_list)
            self.automation_list.controlUp(fav_button)

    def __add_geraetelistitems(self, actions, addon):
        xbmc.log("SzenenDetailWindow: __add_geraetelistitems: action: " + repr(actions), level=xbmc.LOGDEBUG)
        for action in actions:
            xbmc.log("SzenenDetailWindow: __add_geraetelistitems: action Name: " + repr(action.get_name()), level=xbmc.LOGDEBUG)
            item = xbmcgui.ListItem(label=str(action.get_name()))
            icon_name = action.get_icon()
            item.setLabel2(self.get_cmd_txt(action.get_cmdId(), action.get_param(), action.get_device_group(), addon))
            item.setIconImage(os.path.join(_images_device, icon_name))
            item.setProperty("description", action.get_description())
            self.geraete_list.addItem(item)

    def get_cmd_txt(self, cmd_id, param, device_group, addon):
        xbmc.log("SzenenDetailWindow: get_cmd_txt: ", level=xbmc.LOGDEBUG)
        EIN = 10
        AUS = 11
        AUF = 1
        AB = 2
        STOPP = 3
        SENSOR = 666
        FAHRE_IN_POS = 9
        if cmd_id == SENSOR:
            return addon.getLocalizedString(32379)
        elif device_group == 1:
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
            elif cmd_id == FAHRE_IN_POS:
                if param is not None:
                    return homepilot_utils.get_display_value(param, device_group)
                else:
                    return "-"
        elif device_group == 5:
            if cmd_id == EIN:
                return addon.getLocalizedString(32375)
            elif cmd_id == AUS:
                return addon.getLocalizedString(32376)
            elif cmd_id == FAHRE_IN_POS:
                if param is not None:
                    return homepilot_utils.get_display_value(param, device_group)
                else:
                    return "-"
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
            elif cmd_id == FAHRE_IN_POS:
                if param is not None:
                    return homepilot_utils.get_display_value(param, device_group)
                else:
                    return "-"
        elif device_group == 8:
            if cmd_id == AUF:
                return addon.getLocalizedString(32371)
            elif cmd_id == STOPP:
                return addon.getLocalizedString(32372)
            elif cmd_id == AB:
                return addon.getLocalizedString(32373)
            elif cmd_id == FAHRE_IN_POS:
                if param is not None:
                    return homepilot_utils.get_display_value(param, device_group)
                else:
                    return "-"
        return ""

    def onClick(self, controlId):
        xbmc.log("SzenenDetailWindow: onClick: ", level=xbmc.LOGDEBUG)
        if controlId == 160:
            self.__on_click_active_button()
        elif controlId == 136:
            self.__on_click_fav_button()
        elif controlId == self.execcontrol.getId():
            self.client.execute_scene(self.scene.get_id())

    def __on_click_active_button(self):
        xbmc.log("SzenenDetailWindow: __on_click_active_button", level=xbmc.LOGDEBUG)
        aktiv_button = self.getControl(160)
        button_is_akiv = aktiv_button.isSelected()
        xbmc.log("SzenenDetailWindow: __on_click_active_button scene.is_active():" +  repr(self.scene.is_active()) +
                 "\nbutton_is_akiv: " +  repr(button_is_akiv), level=xbmc.LOGDEBUG)
        if self.scene.is_active() and not button_is_akiv:
            self.client.set_scene_inactive(self.scene.get_id())
            self.scene.set_inactive()
            self.removeControl(self.imagecontrol)
            self.imagecontrol = xbmcgui.ControlImage(400, 100, 64, 64, szene_img_deact)
            self.addControl(self.imagecontrol)
        elif not self.scene.is_active() and button_is_akiv:
            self.client.set_scene_active(self.scene.get_id())
            self.scene.set_activ()
            self.removeControl(self.imagecontrol)
            self.imagecontrol = xbmcgui.ControlImage(400, 100, 64, 64, szene_img)
            self.addControl(self.imagecontrol)

    def __on_click_fav_button(self):
        xbmc.log("SzenenDetailWindow: __on_click_fav_button", level=xbmc.LOGDEBUG)
        fav_button = self.getControl(136)
        button_is_faved = (fav_button.isSelected() == 1)
        if self.use_local_favorites:
            favored_scenes = local_favorites.get_scenes_as_set()
            xbmc.log("SzenenDetailWindow: __on_click_fav_button: favored_scenes: " + repr(favored_scenes)
                     + " self.scene.get_id(): " + repr(self.scene.get_id())
                     + " scene is_favored: " + repr(self.scene.is_favored()), level=xbmc.LOGDEBUG)
            if favored_scenes is not None:
                if button_is_faved and self.scene.get_id() not in favored_scenes:
                    local_favorites.add_scene(self.scene.get_id())
                    self.scene.set_favored()
                elif not button_is_faved and self.scene.get_id() in favored_scenes:
                    local_favorites.remove_scene(self.scene.get_id())
                    self.scene.set_unfavored()
            else:
                #Wenn die Favoriten None sind, sind sie leer. Also befüllen wie sie.
                local_favorites.add_scene(self.scene.get_id())
                self.scene.set_favored()
        else:
            if self.scene.is_favored() and not button_is_faved:
                self.client.unfavorize_scene(self.scene.get_id())
                self.scene.set_unfavored()
            elif not self.scene.is_favored() and button_is_faved:
                self.client.favorize_scene(self.scene.get_id())
                self.scene.set_favored()
        xbmc.log("SzenenDetailWindow: __on_click_fav_button: is_favored: " + repr(self.scene.is_favored()), level=xbmc.LOGDEBUG)

    def onAction(self, action):
        xbmc.log("SzenenDetailWindow: onAction: action: " +  repr(action), level=xbmc.LOGDEBUG)
        if action == statics.AID_BACK or action == statics.ACTION_LAST_PAGE or action == statics.ACTION_STEP_BACK:
            self.close()
            self._is_closed = True
        if action == statics.ACTION_PREVIOUS_MENU:
            self.parent_window.shutdown()
            self.close()
            self._is_closed = True

    def is_closed(self):
        return self._is_closed

    def update(self):
        xbmc.log("SzenenDetailWindow: update: is_favored: " + repr(self.scene.is_favored())
                 + "\nexeccontrol: " + repr(self.execcontrol)
                 + "\nradiobutton_control: " + repr(self.radiobutton_control)
                 + "\nuse_local_favorites: " + repr(self.use_local_favorites), level=xbmc.LOGDEBUG)
        if self.getFocusId() == 0 and self.scene.is_executable() and hasattr(self, 'execcontrol') and self.execcontrol is not None:
            self.setFocus(self.execcontrol)
        elif self.getFocusId() == 0 and hasattr(self, 'radiobutton_control') and self.radiobutton_control is not None:
            self.setFocus(self.radiobutton_control)
        try:
            new_scene = self.client.get_scene_by_id(self.scene.get_id())
            if new_scene.get_sync() != self.scene.get_sync():
                self.scene = new_scene
                self.__set_state()
                self.__generate_geraetelist()
                self.__generate_automationlist()
                self.__handle_navigation(self.scene.is_executable())
        except Exception, e:
            xbmc.log(str(e), level=xbmc.LOGWARNING)
