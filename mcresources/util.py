#  Part of mcresources by Alex O'Neill
#  Work under copyright. Licensed under MIT
#  For more information see the project LICENSE file

from json import dump as json_dump
from os import makedirs, listdir, remove as rmf, rmdir
from os.path import join as path_join, dirname, isfile


def clean_generated_resources(path='src/main/resources') -> None:
    """
    Recursively removes all files generated using by mcresources, as identified by the inserted comment.
    Removes empty directories
    :param path: the initial path to search through
    """
    for subdir in listdir(path):
        sub_path = path_join(path, subdir)
        if isfile(sub_path):
            # File, check if valid and then delete
            if subdir.endswith('.json'):
                delete = False
                with open(sub_path, 'r') as file:
                    if '"__comment__": "This file was automatically created by mcresources"' in file.read():
                        delete = True
                if delete:
                    rmf(sub_path)
        else:
            # Folder, search recursively
            clean_generated_resources(sub_path)

        if not listdir(path):
            # Delete empty folder
            rmdir(path)


def del_none(data_in: dict or list or tuple) -> object:
    # Removes all "None" entries in a dictionary, list or tuple, recursively
    if type(data_in) is dict:
        for key, value in list(data_in.items()):
            if value is None:
                del data_in[key]
            else:
                del_none(data_in[key])
        return data_in
    elif type(data_in) in (list, tuple):
        return [del_none(p) for p in data_in if p is not None]


def write(path_parts: tuple, data: dict, indent: int = 2) -> None:
    # write output to json
    path = path_join(*path_parts) + '.json'
    makedirs(dirname(path), exist_ok=True)
    data = del_none({'__comment__': 'This file was automatically created by mcresources', **data})
    with open(path, 'w') as file:
        json_dump(data, file, indent=indent)


def str_path(data_in: str or list or tuple) -> list:
    # Converts an iterable or string to a string list, but respects '/', for use in path construction
    if type(data_in) is str:
        return [s for s in data_in.split('/')]
    elif type(data_in) in (list, tuple):
        return [*flatten_list(data_in)]
    else:
        raise RuntimeError('Unknown object %s at str_path' % str(data_in))


def str_list(data_in: str or list or tuple) -> list:
    # Converts an iterable or string to a string list
    if type(data_in) is str:
        return [data_in]
    elif type(data_in) in [list, tuple]:
        return [*flatten_list(data_in)]
    else:
        raise RuntimeError('Unknown object %s at str_list' % str(data_in))


def flatten_list(container: tuple or list):
    # Turns nested lists of lists into a flat list of items
    # Use for part functions that need to be wrapped in a single list:
    # [*flatten_list([function_returns_list(p) for p in iterable])]
    for i in container:
        if isinstance(i, (list, tuple)):
            for j in flatten_list(i):
                yield j
        else:
            yield i


def dict_get(data_in: dict, key: str, default: object = None, map_function: callable(object) = None) -> object:
    # Gets an element from a dictionary by key
    # If the element is not present, it returns the default value
    # If the element is present, and a map function is supplied, it will apply the map function to the object
    if key in data_in.keys():
        if map_function is None:
            return data_in[key]
        else:
            return map_function(data_in[key])
    else:
        return default
