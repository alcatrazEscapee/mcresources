#  Part of mcresources by Alex O'Neill
#  Work under copyright. Licensed under MIT
#  For more information see the project LICENSE file

import enum
import json
import os
from typing import Union, Sequence, Any, Dict, List, Tuple, Optional, NamedTuple, Callable


class ResourceLocation(NamedTuple('ResourceLocation', domain=str, path=str)):

    def join(self, prefix: str = '', simple: bool = False) -> str:
        if simple and self.domain == 'minecraft':
            return prefix + self.path
        else:
            return self.domain + ':' + prefix + self.path


ResourceIdentifier = Union[ResourceLocation, Sequence[str], str]
Json = Union[Dict[str, Any], Sequence[Any], str]


class WriteFlag(enum.IntEnum):
    NEW = enum.auto()
    MODIFIED = enum.auto()
    UNCHANGED = enum.auto()
    ERROR = enum.auto()


def clean_generated_resources(path: str = 'src/main/resources'):
    """
    Recursively removes all files generated using by mcresources, as identified by the inserted comment.
    Removes empty directories
    :param path: the initial path to search through
    """
    for subdir in os.listdir(path):
        sub_path = os.path.join(path, subdir)
        if os.path.isfile(sub_path):
            # File, check if valid and then delete
            if subdir.endswith('.json'):
                delete = False
                with open(sub_path, 'r') as file:
                    if '"__comment__": "This file was automatically created by mcresources"' in file.read():
                        delete = True
                if delete:
                    os.remove(sub_path)
        else:
            # Folder, search recursively
            clean_generated_resources(sub_path)

        if not os.listdir(path):
            # Delete empty folder
            os.rmdir(path)


def del_none(data_in: Json) -> Json:
    # Removes all "None" entries in a dictionary, list or tuple, recursively
    if isinstance(data_in, Dict):
        return dict((key, del_none(value)) for key, value in data_in.items() if value is not None)
    elif is_sequence(data_in):
        return [del_none(p) for p in data_in if p is not None]
    elif data_in is not None:
        return data_in
    else:
        raise ValueError('None passed to `del_none`, should not be possible.')


def write(path_parts: Sequence[str], data: Json, indent: int = 2, on_error: Callable[[str, Exception], Any] = None) -> WriteFlag:
    """
    Writes json to a file.
    :param path_parts: The path elements of the file
    :param data: The data to write
    :param indent: The indent level for the json output
    :param on_error: A consumer of a file name and error if one occurs
    :return: 0 if the file was new, 1 if the file was modified, 2 if the file was not modified, 3 if an error occurred
    """
    path = os.path.join(*path_parts) + '.json'
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        exists = False
        if os.path.isfile(path):
            with open(path, 'r') as file:
                old_data = json.load(file)
            if old_data == data:
                return WriteFlag.UNCHANGED
            exists = True
        with open(path, 'w') as file:
            json.dump(data, file, indent=indent)
            return WriteFlag.MODIFIED if exists else WriteFlag.NEW
    except Exception as e:
        on_error(path, e)
        return WriteFlag.ERROR


def resource_location(*elements: ResourceIdentifier) -> ResourceLocation:
    """
    Parses a ResourceLocation from a series of elements. Can accept:
    - A ResourceLocation, return it
    - A Sequence[str], representing a '/' joined resource path.
    - A 'domain:path' representing a domain specification
    Then either a single element, or an optional domain followed by data element.
    If a domain is present in the data, the first optional domain is ignored.
    If no domain is present, the `minecraft` domain is inferred.
    """
    if len(elements) not in {1, 2}:
        raise RuntimeError('Must take one or two arguments: [optional] domain, and path elements')
    if len(elements) == 1:
        domain, data = 'minecraft', elements[0]
    else:
        domain, data = elements[0], elements[1]
    if isinstance(data, ResourceLocation):
        return data
    else:
        joined = '/'.join(str_path(data))
        if ':' in joined:
            i = joined.index(':')
            return ResourceLocation(joined[:i], joined[i + 1:])
        else:
            return ResourceLocation(domain, joined)


def str_path(data_in: Sequence[str]) -> List[str]:
    # Converts an iterable or string to a string list, but respects '/', for use in path construction
    if isinstance(data_in, str):
        return [s for s in data_in.split('/')]
    elif isinstance(data_in, Sequence):
        return [*flatten_list([str_path(s) for s in data_in])]
    else:
        raise RuntimeError('Unknown object %s at str_path' % str(data_in))


def str_list(data_in: Sequence[str]) -> List[str]:
    # Converts an iterable or string to a string list
    if isinstance(data_in, str):
        return [data_in]
    elif isinstance(data_in, Sequence):
        return [*flatten_list(data_in)]
    else:
        raise RuntimeError('Unknown object %s at str_list' % str(data_in))


def domain_path_parts(name_parts: Sequence[str], default_domain: str) -> Tuple[str, List[str]]:
    joined = '/'.join(str_path(name_parts))
    if ':' in joined:
        i = joined.index(':')
        return joined[:i], joined[i + 1:].split('/')
    else:
        return default_domain, str_path(joined)


def flatten_list(container: Sequence[Any]) -> Sequence[Any]:
    # Turns nested lists of lists into a flat list of items
    # Use for part functions that need to be wrapped in a single list:
    # [*flatten_list([function_returns_list(p) for p in iterable])]
    for i in container:
        if is_sequence(i):
            for j in flatten_list(i):
                yield j
        else:
            yield i


def dict_get(data_in: Dict[Any, Any], key: Any, default: Any = None, map_function: Callable[[Any], Any] = None) -> Any:
    # Gets an element from a dictionary by key
    # If the element is not present, it returns the default value
    # If the element is present, and a map function is supplied, it will apply the map function to the object
    if key in data_in:
        if map_function is None:
            return data_in[key]
        else:
            return map_function(data_in[key])
    else:
        return default


def is_sequence(data_in: Any) -> bool:
    return isinstance(data_in, Sequence) and not isinstance(data_in, str)

# ================== ASSET PARTS ===================


def recipe_condition(data_in: Json, strict: bool = False) -> Union[List, None]:
    if data_in is None:
        return None
    elif isinstance(data_in, str):
        return [{'type': data_in}]
    elif isinstance(data_in, Dict):
        return [data_in]
    elif is_sequence(data_in) and not strict:
        return [*flatten_list([recipe_condition(c, True) for c in data_in])]
    else:
        raise RuntimeError('Unknown object %s at recipe_condition' % str(data_in))


def ingredient(data_in: Json) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
    ing = item_stack_list(data_in)
    if len(ing) == 1:
        return ing[0]
    else:
        return ing


def item_stack(data_in: Json) -> Dict[str, Any]:
    if isinstance(data_in, str):
        if data_in[0:4] == 'tag!':
            return {'tag': data_in[4:]}
        else:
            return {'item': data_in}
    elif isinstance(data_in, Dict):
        return data_in
    elif is_sequence(data_in):
        if len(data_in) != 2:
            raise RuntimeError('An item stack as a sequence must have two entries (size, item)')
        return {
            'count': data_in[0],
            **item_stack(data_in[1])
        }
    else:
        raise RuntimeError('Unknown object %s at item_stack' % str(data_in))


def item_stack_list(data_in: Json) -> List[Dict[str, Any]]:
    if isinstance(data_in, str) or isinstance(data_in, Dict):
        return [item_stack(data_in)]
    elif isinstance(data_in, Sequence):
        return [*flatten_list([item_stack(s) for s in data_in])]
    else:
        raise RuntimeError('Unknown object %s at item_stack_list' % str(data_in))


def item_stack_dict(data_in: Union[Dict[str, Any], str], default_char: str = '#') -> dict:
    if isinstance(data_in, Dict):
        return dict((k, item_stack(v)) for k, v in data_in.items())
    elif isinstance(data_in, str):
        return {default_char: item_stack(data_in)}
    else:
        raise RuntimeError('Unknown object %s at item_stack_dict' % str(data_in))


def item_model_textures(data_in: Json) -> Dict[str, Any]:
    if isinstance(data_in, str):
        return {'layer0': data_in}
    elif isinstance(data_in, Sequence):
        return dict(('layer%d' % i, data_in[i]) for i in range(len(data_in)))
    elif isinstance(data_in, Dict):
        return data_in
    else:
        raise RuntimeError('Unknown object %s at item_model_textures' % str(data_in))


def blockstate_multipart_parts(data_in: Sequence[Json]) -> List[Dict[str, Any]]:
    def part(p: Union[Sequence[Json], Json]) -> Dict[str, Any]:
        if isinstance(p, Sequence) and len(p) == 2:
            return {'when': p[0], 'apply': p[1]}
        elif isinstance(p, Dict):
            return {'apply': p}
        else:
            raise RuntimeError('Unknown object %s at blockstate_multipart_parts#part' % str(p))

    return [part(p) for p in data_in]


def lang_parts(data_in: Sequence[Json], entries: Dict[str, str] = None) -> Dict[str, str]:
    if entries is None:
        entries = {}
    i = 0
    while i < len(data_in):
        part = data_in[i]
        if isinstance(part, str):
            value = data_in[i + 1]
            entries[part] = value
            i += 1
        elif isinstance(part, Sequence):
            lang_parts(part, entries)
        elif isinstance(part, Dict):
            entries.update(part)
        else:
            raise RuntimeError('Unknown object %s at lang_parts' % str(part))
        i += 1
    return entries


# ================== LOOT TABLES ===================


def loot_pool_list(data_in: Json, loot_type: str) -> List[Dict[str, Any]]:
    # Top level loot pool parser
    if isinstance(data_in, str):
        # Simplest loot pool, construct a single entry
        return [{
            'name': 'loot_pool',
            'rolls': 1,
            'entries': loot_entry_list(data_in),
            'conditions': loot_default_conditions(loot_type),
        }]
    elif isinstance(data_in, Dict):
        # Single loot pool with any amount of things specified
        return [{
            'name': 'loot_pool',
            'rolls': dict_get(data_in, 'rolls', 1),
            'bonus_rolls': dict_get(data_in, 'bonus_rolls'),
            'entries': dict_get(data_in, 'entries', data_in, map_function=loot_entry_list),
            'conditions': dict_get(data_in, 'conditions', default=loot_default_conditions(loot_type),
                                   map_function=loot_condition_list),
            'functions': dict_get(data_in, 'functions', map_function=loot_function_list),
        }]
    elif isinstance(data_in, Sequence):
        # List of pools, so flatten the list and try make a loot pool list for each entry
        return [*flatten_list([loot_pool_list(p, loot_type) for p in data_in])]
    else:
        raise RuntimeError('Unknown object %s at loot_pool_list' % str(data_in))


def loot_entry_list(data_in: Json) -> List[Dict[str, Any]]:
    # Creates a single loot pool entry
    if isinstance(data_in, str):
        # String, so either create an item or a tag based drop
        if data_in[0:4] == 'tag!':
            return [{'type': 'minecraft:tag', 'name': data_in[4:]}]
        else:
            return [{'type': 'minecraft:item', 'name': data_in}]
    elif isinstance(data_in, Sequence):
        # iterable, so create a loot entry list for each element and flatten
        return [*flatten_list([loot_entry_list(p) for p in data_in])]
    elif isinstance(data_in, Dict):
        # dict, so check through available parameters and construct a loot entry from those
        return [{
            'type': dict_get(data_in, 'type', default='item'),
            'conditions': dict_get(data_in, 'conditions', map_function=loot_condition_list),
            'name': dict_get(data_in, 'name'),
            'children': dict_get(data_in, 'children'),
            'expand': dict_get(data_in, 'expand'),
            'functions': dict_get(data_in, 'functions', map_function=loot_function_list),
            'weight': dict_get(data_in, 'weight'),
            'quality': dict_get(data_in, 'quality')
        }]
    else:
        raise RuntimeError('Unknown object %s at loot_entry_list' % str(data_in))


def loot_function_list(data_in: Json) -> Optional[List[Dict[str, Any]]]:
    # a list of loot pool functions
    if data_in is None:
        # allow None
        return None
    elif isinstance(data_in, str):
        # string, so just accept a name
        return [{'function': data_in}]
    elif isinstance(data_in, Sequence):
        # iterable, so create a list for each condition and flatten
        return [*flatten_list([loot_function_list(p) for p in data_in])]
    elif isinstance(data_in, Dict):
        # dict, so just use raw data
        return [data_in]
    else:
        raise RuntimeError('Unknown object %s at loot_function_list' % str(data_in))


def loot_condition_list(data_in: Json) -> Optional[List[Dict[str, Any]]]:
    # a list of loot pool conditions
    if data_in is None:
        # allow None
        return None
    if isinstance(data_in, str):
        # string, so just accept a name
        return [{'condition': data_in}]
    elif isinstance(data_in, Sequence):
        # iterable, so create a list for each condition and flatten
        return [*flatten_list([loot_condition_list(p) for p in data_in])]
    elif isinstance(data_in, Dict):
        # dict, so just use raw data
        return [data_in]
    else:
        raise RuntimeError('Unknown object %s at loot_condition_list' % str(data_in))


def loot_default_conditions(loot_type: str) -> Union[List[Dict[str, Any]], None]:
    if loot_type == 'block':
        return [{'condition': 'minecraft:survives_explosion'}]
    else:
        return None
