#  Part of mcresources by Alex O'Neill
#  Work under copyright. Licensed under MIT
#  For more information see the project LICENSE file
import utils
from mcresources.type_definitions import Json, JsonObject, ResourceIdentifier, ResourceLocation, T, K, V, DefaultValue, MapValue, VerticalAnchor

from typing import List, Tuple, Dict, Sequence, Optional, Callable, Any, Literal, Union

import enum
import json
import os


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
                with open(sub_path, 'r', encoding='utf-8') as file:
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
            with open(path, 'r', encoding='utf-8') as file:
                old_data = json.load(file)
            if old_data == data:
                return WriteFlag.UNCHANGED
            exists = True
        with open(path, 'w', encoding='utf-8') as file:
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
        raise ValueError('Must take one or two arguments: [optional] domain, and path elements')
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
        raise ValueError('Unknown object %s at str_path' % str(data_in))


def str_list(data_in: Sequence[str]) -> List[str]:
    # Converts an iterable or string to a string list
    if isinstance(data_in, str):
        return [data_in]
    elif isinstance(data_in, Sequence):
        return [*flatten_list(data_in)]
    else:
        raise ValueError('Unknown object %s at str_list' % str(data_in))


def domain_path_parts(name_parts: Sequence[str], default_domain: str) -> Tuple[str, List[str]]:
    joined = '/'.join(str_path(name_parts))
    if ':' in joined:
        i = joined.index(':')
        return joined[:i], joined[i + 1:].split('/')
    else:
        return default_domain, str_path(joined)


def flatten_list(container: Sequence[T]) -> Sequence[T]:
    # Turns nested lists of lists into a flat list of items
    # Use for part functions that need to be wrapped in a single list:
    # [*flatten_list([function_returns_list(p) for p in iterable])]
    for i in container:
        if is_sequence(i):
            for j in flatten_list(i):
                yield j
        else:
            yield i


def dict_get(data_in: Dict[K, V], key: K, default: DefaultValue = None, map_function: Optional[Callable[[V], MapValue]] = None) -> Union[V, DefaultValue, MapValue]:
    # Gets an optional element from a dictionary by key
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


def unordered_pair(data_in: Sequence[Any], first_type: type, second_type: type) -> Tuple[Any, Any]:
    pair = maybe_unordered_pair(data_in, first_type, second_type)
    assert pair is not None, 'Not an unordered pair of (%s, %s), got: %s' % (str(first_type), str(second_type), str(data_in))
    return pair

def maybe_unordered_pair(data_in: Any, first_type: type, second_type: type) -> Optional[Tuple[Any, Any]]:
    if is_sequence(data_in) and len(data_in) == 2:
        a, b = data_in
        if isinstance(a, first_type) and isinstance(b, second_type):
            return a, b
        elif isinstance(b, first_type) and isinstance(a, second_type):
            return b, a
    return None

# ================== ASSET PARTS ===================


def recipe_condition(data_in: Json, strict: bool = False) -> Optional[List[JsonObject]]:
    if data_in is None:
        return None
    elif isinstance(data_in, str):
        return [{'type': data_in}]
    elif isinstance(data_in, Dict):
        return [data_in]
    elif is_sequence(data_in) and not strict:
        return [*flatten_list([recipe_condition(c, True) for c in data_in])]
    else:
        raise ValueError('Unknown object %s at recipe_condition' % str(data_in))


def ingredient(data_in: Json) -> Json:
    ing = item_stack_list(data_in)
    if len(ing) == 1:
        return ing[0]
    else:
        return ing


def item_predicate(data_in: Json) -> Json:
    if isinstance(data_in, dict):
        return data_in
    elif is_sequence(data_in):  # List of item IDs
        return {'items': [utils.resource_location(e).join() for e in data_in]}
    elif isinstance(data_in, str):  # Single item or tag
        item, tag, count, _ = parse_item_stack(data_in, False)
        d: Json = {'tag': item} if tag else {'items': [item]}
        if count:
            d['count'] = count
        return d
    else:
        raise ValueError('Unknown object %s at item_predicate' % str(data_in))


def item_stack(data_in: Json) -> JsonObject:
    if isinstance(data_in, dict):
        return data_in
    elif is_sequence(data_in):
        item, count = unordered_pair(data_in, str, int)
        return {'item': item, 'count': count}
    elif isinstance(data_in, str):
        item, tag, count, _ = parse_item_stack(data_in, False)
        d = {'tag' if tag else 'item': item}
        if count:
            d['count'] = count
        return d
    else:
        raise ValueError('Unknown object %s at item_stack' % str(data_in))


def item_stack_list(data_in: Json) -> List[JsonObject]:
    if isinstance(data_in, str) or isinstance(data_in, Dict):
        return [item_stack(data_in)]
    elif is_sequence(data_in):
        return [*flatten_list([item_stack(s) for s in data_in])]
    else:
        raise ValueError('Unknown object %s at item_stack_list' % str(data_in))


def item_stack_dict(data_in: Json, default_char: str = '#') -> Dict[str, JsonObject]:
    if isinstance(data_in, Dict):
        return dict((k, item_stack(v)) for k, v in data_in.items())
    elif isinstance(data_in, str):
        return {default_char: item_stack(data_in)}
    else:
        raise ValueError('Unknown object %s at item_stack_dict' % str(data_in))


def parse_item_stack(data_in: str, allow_ranges: bool = True) -> Tuple[str, bool, Optional[int], Optional[int]]:
    """
    Allows the following formats to define either an item or a tag:
    'namespace:path' -> item
    '#namespace:path' -> tag
    Also allows the following count specifiers
    '1 item'
    '3-5 item' (only if allow_ranges = True)
    Returns (item name, is tag, minimum count, maximum count)
    """
    item = data_in
    try:
        if ' ' in data_in:
            count, item = data_in.split(' ')
            if '-' in count:
                if not allow_ranges:
                    raise ValueError('Range in item stack with allow_ranges = False')
                lo, hi = map(int, count.split('-'))
            else:
                lo = hi = int(count)
        else:
            lo = hi = None
    except Exception as e:
        raise ValueError('Malformed item stack: %s' % data_in) from e

    if 'tag!' in data_in:
        raise ValueError('Using old \'tag!\' format for item stack: %s' % str(data_in))

    tag = item[0] == '#'
    if tag:
        item = item[1:]

    return item, tag, lo, hi


def item_model_textures(data_in: Json) -> JsonObject:
    # Input must be in tuple (varargs) format
    if len(data_in) == 1 and isinstance(data_in[0], Dict):
        return data_in[0]
    else:
        return dict(('layer%d' % i, layer) for i, layer in enumerate(flatten_list(data_in)))


def blockstate_multipart_parts(data_in: Sequence[Json]) -> List[JsonObject]:
    def part(p: Json) -> JsonObject:
        if isinstance(p, Sequence) and len(p) == 2:
            return {'when': p[0], 'apply': p[1]}
        elif isinstance(p, Dict):
            return {'apply': p}
        else:
            raise ValueError('Unknown object %s at blockstate_multipart_parts#part' % str(p))

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
            raise ValueError('Unknown object %s at lang_parts' % str(part))
        i += 1
    return entries


# ================== LOOT TABLES ===================


def loot_pool(data_in: Json, loot_type: str) -> JsonObject:
    # Creates a single loot pool
    if isinstance(data_in, str):
        # One 'minecraft:item' entry
        return {
            'name': 'loot_pool',
            'rolls': 1,
            'entries': loot_entries(data_in),
            'conditions': loot_default_conditions(loot_type),
        }
    elif isinstance(data_in, Dict):
        # Infer if this is a pool, or a single entry (with inferred pool). When in doubt, assume an entry
        if 'entries' in data_in or 'rolls' in data_in or 'bonus_rolls' in data_in:
            # Assume pool
            return {
                'name': 'loot_pool',
                'rolls': dict_get(data_in, 'rolls', 1),
                'bonus_rolls': dict_get(data_in, 'bonus_rolls'),
                'entries': dict_get(data_in, 'entries', data_in, map_function=loot_entries),
                'conditions': dict_get(data_in, 'conditions', default=loot_default_conditions(loot_type), map_function=loot_conditions),
                'functions': dict_get(data_in, 'functions', map_function=loot_functions),
            }
        else:
            # Assume single pool, one entry
            return {
                'name': 'loot_pool',
                'rolls': 1,
                'entries': loot_entries(data_in),
                'conditions': loot_default_conditions(loot_type)
            }
    elif isinstance(data_in, Sequence):
        # Infer a 'minecraft:alternatives' pool with multiple entries
        return {
            'name': 'loot_pool',
            'rolls': 1,
            'entries': [{
                'type': 'minecraft:alternatives',
                'children': loot_entries(data_in)
            }],
            'conditions': loot_default_conditions(loot_type)
        }
    else:
        raise ValueError('Unknown object %s at loot_pool' % str(data_in))


def loot_entries(data_in: Json) -> Optional[List[JsonObject]]:
    # Creates a single loot pool entry
    if data_in is None:
        # allow None
        return None
    elif isinstance(data_in, str):
        item, tag, lo, hi = parse_item_stack(data_in, True)
        item = {
            'type': 'minecraft:tag' if tag else 'minecraft:item',
            'name': item
        }
        if lo:
            count = lo if lo == hi else {'type': 'minecraft:uniform', 'min': lo, 'max': hi}
            item['functions'] = [{
                'function': 'minecraft:set_count',
                'count': count
            }]
        return [item]
    elif isinstance(data_in, Sequence):
        # iterable, so create a loot entry list for each element and flatten
        return [*flatten_list([loot_entries(p) for p in data_in])]
    elif isinstance(data_in, Dict):
        # dict, so check through available parameters and construct a loot entry from those
        return [{
            'type': dict_get(data_in, 'type', default='minecraft:item'),
            'name': dict_get(data_in, 'name'),
            'children': dict_get(data_in, 'children', map_function=loot_entries),
            'conditions': dict_get(data_in, 'conditions', map_function=loot_conditions),
            'functions': dict_get(data_in, 'functions', map_function=loot_functions),
            'expand': dict_get(data_in, 'expand'),
            'weight': dict_get(data_in, 'weight'),
            'quality': dict_get(data_in, 'quality')
        }]
    else:
        raise ValueError('Unknown object %s at loot_entries' % str(data_in))


def loot_functions(data_in: Json) -> Optional[List[JsonObject]]:
    # a list of loot pool functions
    if data_in is None:
        # allow None
        return None
    elif isinstance(data_in, str):
        # string, so just accept a name
        return [{'function': data_in}]
    elif isinstance(data_in, Sequence):
        # iterable, so create a list for each condition and flatten
        return [*flatten_list([loot_functions(p) for p in data_in])]
    elif isinstance(data_in, Dict):
        # dict, so just use raw data
        return [data_in]
    else:
        raise ValueError('Unknown object %s at loot_functions' % str(data_in))


def loot_conditions(data_in: Json) -> Optional[List[JsonObject]]:
    # a list of loot pool conditions
    if data_in is None:
        # allow None
        return None
    if isinstance(data_in, str):
        # string, so just accept a name
        return [{'condition': data_in}]
    elif isinstance(data_in, Sequence):
        # iterable, so create a list for each condition and flatten
        return [*flatten_list([loot_conditions(p) for p in data_in])]
    elif isinstance(data_in, Dict):
        # dict, so just use raw data
        return [data_in]
    else:
        raise ValueError('Unknown object %s at loot_conditions' % str(data_in))


def loot_default_conditions(loot_type: str) -> Optional[List[JsonObject]]:
    if loot_type == 'blocks':
        return [{'condition': 'minecraft:survives_explosion'}]
    else:
        return None


# World Generation


def expand_configured(data: Json) -> JsonObject:
    """ Creates a configured object from multiple possibilities. Accepts:
    - A tuple consisting of exactly two elements, the type name and the config
    - Otherwise, data is assumed to be a ResourceIdentifier indicating a type name
    """
    if pair := maybe_unordered_pair(data, str, dict):
        return configure(*pair)
    elif isinstance(data, str) or is_sequence(data):
        return configure(data)
    else:
        raise ValueError('Unknown object %s at configured' % str(data))


def configured_placement(data: Json) -> JsonObject:
    """ Creates a configured placement from multiple possibilities. Accepts:
    - A tuple consisting of exactly two elements, the type name and optional additional parameters

    - A string type name
    """
    if pair := maybe_unordered_pair(data, str, dict):
        assert 'type' not in pair[1], 'Type specified twice for placement'
        return {'type': resource_location(pair[0]).join(), **pair[1]}
    elif isinstance(data, dict):
        assert 'type' in data, 'Missing \'type\' in placement'
        return data
    elif isinstance(data, str) or is_sequence(data):
        return {'type': resource_location(data).join()}
    else:
        raise ValueError('Unknown object %s at configured_placement' % str(data))


def configure(type_name: ResourceIdentifier, config: Optional[JsonObject] = None) -> JsonObject:
    """
    Creates a configured object with a type and config
    """
    res = resource_location(type_name)
    if config is None:
        config = {}
    return {
        'type': res.join(),
        'config': config
    }


def vertical_anchor(y: int, anchor: Literal['absolute', 'above_bottom', 'below_top'] = 'absolute') -> VerticalAnchor:
    return as_vertical_anchor((anchor, y))


def as_vertical_anchor(va: VerticalAnchor) -> VerticalAnchor:
    types = ('absolute', 'above_bottom', 'below_top')
    if isinstance(va, int):
        return {'absolute': va}
    elif isinstance(va, tuple):
        key, value = unordered_pair(va, str, int)
        return {key: value}
    elif isinstance(va, dict):
        assert len(va) == 1
        assert any(k in va and isinstance(va[k], int) for k in types)
        return va
    raise ValueError('Unknown VerticalAnchor: %s' % str(va))


def block_state(data: Json):
    """ Converts a block state registry name, with optional properties to the format used by all block state codecs """
    if isinstance(data, str):
        property_map = {}
        if '[' in data and data.endswith(']'):
            name, properties = data[:-1].split('[')
            for pair in properties.split(','):
                key, value = pair.split('=')
                property_map[key] = value
        else:
            name = data
        return {'Name': name, 'Properties': property_map}
    elif isinstance(data, dict):
        if 'Name' not in data:
            raise ValueError('Missing \'Name\' key in block_state for object %s' % str(data))
        if 'Properties' not in data:
            data['Properties'] = {}
        return data
    else:
        raise ValueError('Unknown object %s at block_state' % str(data))
