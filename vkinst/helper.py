import os
import time
from pathlib import Path


def get_folder_names(directory):
    """
    Returns a list of all the folder names inside the specified directory.
    """
    folder_names = list()
    for filename in os.listdir(directory):
        if os.path.isdir(Path(directory, filename)):
            folder_names.append(filename)
    return folder_names


def get_dict_element(dict_object, key_path):
    keys = key_path.split(".")
    value = dict_object

    for key in keys:
        if value and isinstance(value, list):
            value = value[0]
        if key in value:
            value = value[key]
        else:
            return None

    return value


def wait_between_requests(func):
    def wrapper(self, *args, **kwargs):
        result = func(self, *args, **kwargs)
        time.sleep(3)
        return result

    return wrapper


def replace_at_links(text):
    if isinstance(text, str):
        return text.replace("@", "@ ")
    else:
        return text