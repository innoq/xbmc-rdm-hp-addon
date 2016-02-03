import xbmc
import json
import os.path

file_location = str(xbmc.translatePath("special://userdata")) + "addon_data/script.homepilot/local_favorites.json"
DEVICES = "devices"
SCENES = "scenes"


def open_file_to_read():
    xbmc.log("local_favorites: open_file_to_read. ", level=xbmc.LOGDEBUG)
    try:
        if os.path.isfile(file_location):
            with open(file_location, 'r') as f:
                content = f.read()
                if content == '':
                    data = None
                else:
                    data = json.loads(content)
                xbmc.log("local_favorites: open_file_to_write: Content: " + repr(content), level=xbmc.LOGDEBUG)
                return data
    except Exception, e:
        xbmc.log("local_favorites: open_file_to_read: Problem beim Lesen der Datei: " + str(file_location) + "  " + str(
            e.message), level=xbmc.LOGWARNING)
        return None


def open_file_to_write(type, id):
    xbmc.log("local_favorites: open_file_to_write: ", level=xbmc.LOGDEBUG)
    try:
        if os.path.isfile(file_location):
            with open(file_location, 'r') as f:
                content = f.read()
                if content == '':
                    f.close()
                    with open(file_location, 'w') as f:
                        if type == DEVICES:
                            data = {SCENES: [], DEVICES: [id]}
                        else:
                            data = {SCENES: [id], DEVICES: []}
                        json_text = json.dumps(data)
                        f.write(json_text)
                        xbmc.log("local_favorites: open_file_to_write: TYPE: " + str(type)
                                 + "\nID: " + repr(id)
                                 + "\nJSON: " + repr(json_text), level=xbmc.LOGDEBUG)
                else:
                    data = json.loads(content)
                    json_text = __add_id(data, id, type) # "devices"
                    with open(file_location, 'w') as f:
                        f.write(json_text)
                        xbmc.log("local_favorites: open_file_to_write: TYPE: " + str(type)
                                 + "\nID: " + repr(id)
                                 + "\nJSON: " + repr(json_text), level=xbmc.LOGDEBUG)
        else:
            with open(file_location, 'w') as f:
                if id == DEVICES:
                    data = {SCENES: [], DEVICES: [id]}
                else:
                    data = {SCENES: [id], DEVICES: []}
                json_text = json.dumps(data)
                f.write(json_text)
                xbmc.log("local_favorites: open_file_to_write: TYPE: " + str(type)
                                 + "\nID: " + repr(id)
                                 + "\nJSON: " + repr(json_text), level=xbmc.LOGDEBUG)
    except Exception, e:
        xbmc.log("local_favorites: open_file_to_write: Problem beim Verarbeiten der Datei: " + str(file_location) + "  " + str(e.message),
                 level=xbmc.LOGWARNING)


def get_file_content(file_path):
    xbmc.log("local_favorites: get_file_content. ", level=xbmc.LOGDEBUG)
    return open_file_to_read()


def get_devices_as_set():
    xbmc.log("local_favorites: get_devices_as_set: ", level=xbmc.LOGDEBUG)
    data = get_file_content(file_location)
    if data is not None:
        device_ids = data[DEVICES]
        if not device_ids:
            xbmc.log("local_favorites: get_devices_as_set: Keine lokalen Geraete Favoriten gefunden. No devices.",
                     level=xbmc.LOGDEBUG)
            return None
        else:
            xbmc.log("local_favorites: get_devices_as_set: "+repr(len(device_ids))+" lokale Geraete Favoriten gefunden.", level=xbmc.LOGDEBUG)
            return set(device_ids)
    else:
        xbmc.log("local_favorites: get_devices_as_set: Keine lokalen Geraete Favoriten gefunden. No data. ", level=xbmc.LOGDEBUG)
        return None


def add_device(device_id):
    xbmc.log("local_favorites: add_device: ", level=xbmc.LOGDEBUG)
    open_file_to_write(DEVICES, device_id)


def __add_id(data, id, type):
    xbmc.log("local_favorites: __add_id: ", level=xbmc.LOGDEBUG)
    device_ids = set(data[type])
    device_ids.add(id)
    data[type] = list(device_ids)
    return json.dumps(data)


def remove_device(device_id):
    xbmc.log("local_favorites: remove_device: ", level=xbmc.LOGDEBUG)
    try:
        if os.path.isfile(file_location):
            with open(file_location, 'r') as rm_file:
                content = rm_file.read()
            with open(file_location, 'w') as rm_file:
                data = json.loads(content)
                json_text = __remove_id(data, device_id, DEVICES)
                rm_file.write(json_text)
    except Exception, e:
        xbmc.log("remove_device: Problem beim Verarbeiten der Datei: " + str(file_location) + "  " + str(e), level=xbmc.LOGWARNING)


def __remove_id(data, id, type):
    xbmc.log("local_favorites: __remove_id: ", level=xbmc.LOGDEBUG)
    device_ids = set(data[type])
    device_ids.remove(id)
    data[type] = list(device_ids)
    return json.dumps(data)


def get_scenes_as_set():
    xbmc.log("local_favorites: get_scenes_as_set: ", level=xbmc.LOGDEBUG)
    data = get_file_content(file_location)
    if data is not None:
        scene_ids = data[SCENES]
        if not scene_ids:
            xbmc.log("local_favorites: get_scenes_as_set: Keine lokalen Szene Favoriten gefunden. Keine Szenen. ",
                     level=xbmc.LOGDEBUG)
            return None
        else:
            xbmc.log("local_favorites: get_scenes_as_set: "+repr(len(scene_ids))+" lokale Szene Favoriten gefunden.", level=xbmc.LOGDEBUG)
            return set(scene_ids)
    else:
        xbmc.log("local_favorites: get_scenes_as_set: Keine Lokalen Szene Favoriten gefunden. Keine Daten. ", level=xbmc.LOGDEBUG)
        return None


def add_scene(scene_id):
    xbmc.log("local_favorites: add_scene: scene_id: " + repr(scene_id), level=xbmc.LOGDEBUG)
    open_file_to_write(SCENES, scene_id)


def remove_scene(scene_id):
    xbmc.log("local_favorites: remove_scene: scene_id: " + repr(scene_id), level=xbmc.LOGDEBUG)
    try:
        if os.path.isfile(file_location):
            with open(file_location, 'r') as remove_scene:
                content = remove_scene.read()
            with open(file_location, 'w') as remove_scene:
                data = json.loads(content)
                json_text = __remove_id(data, scene_id, SCENES)
                remove_scene.write(json_text)
    except Exception, e:
        xbmc.log("remove_scene: Problem beim Verarbeiten der Datei: " + str(file_location) + "  " + str(e), level=xbmc.LOGWARNING)

