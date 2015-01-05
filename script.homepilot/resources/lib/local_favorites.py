
import xbmcvfs
import xbmc
import json
import os.path

file_location = xbmc.translatePath('special://userdata') + 'addon_data/script.homepilot/local_favorites.json'


def get_file_content(file_path):
    try:
        if os.path.isfile(file_location):
            with open(file_location, 'r') as f:
                content = f.read()
                data = json.loads(content)
                return data
    except Exception, e:
        xbmc.log("Problem beim Lesen der Datei: " + str(file_location) + "  " + str(e), level=xbmc.LOGWARNING)

    return None


def get_devices_as_set():
    data = get_file_content(file_location)
    if data is not None:
        device_ids = data["devices"]
        return set(device_ids)
    else:
        return set()


def add_device(device_id):
    try:
        if os.path.isfile(file_location):
            content = "{}"
            with open(file_location, 'r') as file:
                content = file.read()
            data = json.loads(content)
            json_text = __add_id(data, device_id, "devices")
            with open(file_location, 'w') as file:
                file.write(json_text)
        else:
            with open(file_location, 'w') as f:
                data = {}
                data["scenes"] = []
                data["devices"] = [device_id]
                json_text = json.dumps(data)
                f.write(json_text)
        return True
    except Exception, e:
        xbmc.log("Problem beim Verarbeiten der Datei: " + str(file_location) + "  " + str(e), level=xbmc.LOGWARNING)
    return False


def __add_id(data, id, type):
    device_ids = set(data[type])
    device_ids.add(id)
    data[type] = list(device_ids)
    return json.dumps(data)


def remove_device(device_id):
    try:
        if os.path.isfile(file_location):
            content = "{}"
            with open(file_location, 'r') as file:
                content = file.read()
            with open(file_location, 'w') as file:
                data = json.loads(content)
                json_text = __remove_id(data, device_id, "devices")
                file.write(json_text)
    except Exception, e:
        xbmc.log("Problem beim Verarbeiten der Datei: " + str(file_location) + "  " + str(e), level=xbmc.LOGWARNING)


def __remove_id(data, id, type):
    device_ids = set(data[type])
    device_ids.remove(id)
    data[type] = list(device_ids)
    return json.dumps(data)


def get_scenes_as_set():
    data = get_file_content(file_location)
    if data is not None:
        scene_ids = data["scenes"]
        return set(scene_ids)
    else:
        return set()


def add_scene(scene_id):
    try:
        if os.path.isfile(file_location):
            content = "{}"
            with open(file_location, 'r') as file:
                content = file.read()
            with open(file_location, 'w') as file:
                data = json.loads(content)
                json_text = __add_id(data, scene_id, "scenes")
                file.write(json_text)
        else:
            f =xbmcvfs.File(file_location, 'w')
            data = {}
            data["scenes"] = [scene_id]
            data["devices"] = []
            json_text = json.dumps(data)
            f.write(json_text)
            f.close()
        return True
    except Exception, e:
        xbmc.log("Problem beim Verarbeiten der Datei: " + str(file_location) + "  " + str(e), level=xbmc.LOGWARNING)

    return False


def remove_scene(scene_id):
    try:
        if os.path.isfile(file_location):
            content = "{}"
            with open(file_location, 'r') as file:
                content = file.read()
            with open(file_location, 'w') as file:
                data = json.loads(content)
                json_text = __remove_id(data, scene_id, "scenes")
                file.write(json_text)
    except Exception, e:
        xbmc.log("Problem beim Verarbeiten der Datei: " + str(file_location) + "  " + str(e), level=xbmc.LOGWARNING)
