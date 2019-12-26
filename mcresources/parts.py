#  Part of mcresources by Alex O'Neill
#  Work under copyright. Licensed under MIT
#  For more information see the project LICENSE file

from mcresources.util import *


def recipe_condition(data_in: str or dict or list or tuple, strict: bool = False) -> list or None:
    if data_in is None:
        return None
    elif type(data_in) is str:
        return [{'type': data_in}]
    elif type(data_in) is dict:
        return [data_in]
    elif type(data_in) in [list, tuple] and not strict:
        return [recipe_condition(c, True) for c in data_in]
    else:
        raise RuntimeError('Unknown object %s at recipe_condition' % str(data_in))


def item_stack(data_in: str or dict) -> dict:
    if type(data_in) is str:
        if data_in[0:4] == 'tag!':
            return {'tag': data_in[4:]}
        else:
            return {'item': data_in}
    elif type(data_in) is dict:
        return data_in
    else:
        raise RuntimeError('Unknown object %s at item_stack' % str(data_in))


def item_stack_list(data_in: str or dict or list or tuple) -> list:
    if type(data_in) in (list, tuple):
        return [*flatten_list([item_stack(s) for s in data_in])]
    elif type(data_in) in (str, dict):
        return [item_stack(data_in)]
    else:
        raise RuntimeError('Unknown object %s at item_stack_list' % str(data_in))


def item_stack_dict(data_in: str or dict, default_char: str = '#') -> dict:
    if type(data_in) is dict:
        return dict((k, item_stack(v)) for k, v in data_in.items())
    elif type(data_in) is str:
        return {default_char: item_stack(data_in)}
    else:
        raise RuntimeError('Unknown object %s at item_stack_dict' % str(data_in))


def item_model_textures(data_in: str or dict or list or tuple) -> dict:
    if type(data_in) is str:
        return {'layer0': data_in}
    elif type(data_in) in [list, tuple]:
        return dict(('layer%d' % i, data_in[i]) for i in range(len(data_in)))
    elif type(data_in) is dict:
        return data_in
    else:
        raise RuntimeError('Unknown object %s at item_model_textures' % str(data_in))


# ================== LOOT TABLES ===================


def loot_pool_list(data_in: str or dict or list or tuple, loot_type: str) -> list:
    # Top level loot pool parser
    if type(data_in) is str:
        # Simplest loot pool, construct a single entry
        return [{
            'name': 'loot_pool',
            'rolls': 1,
            'entries': loot_entry_list(data_in),
            'conditions': loot_default_conditions(loot_type),
        }]
    elif type(data_in) is dict:
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
    elif type(data_in) in (list, tuple):
        # List of pools, so flatten the list and try make a loot pool list for each entry
        return [*flatten_list([loot_pool_list(p, loot_type) for p in data_in])]
    else:
        raise RuntimeError('Unknown object %s at loot_pool_list' % str(data_in))


def loot_entry_list(data_in: str or dict or list or tuple) -> list:
    # Creates a single loot pool entry
    if type(data_in) is str:
        # String, so either create an item or a tag based drop
        if data_in[0:4] == 'tag!':
            return [{'type': 'minecraft:tag', 'name': data_in[4:]}]
        else:
            return [{'type': 'minecraft:item', 'name': data_in}]
    elif type(data_in) in (list, tuple):
        # iterable, so create a loot entry list for each element and flatten
        return [*flatten_list([loot_entry_list(p) for p in data_in])]
    elif type(data_in) is dict:
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


def loot_function_list(data_in: str or dict or list or tuple) -> list:
    # a list of loot pool functions
    if type(data_in) is str:
        # string, so just accept a name
        return [{'function': data_in}]
    elif type(data_in) in (list, tuple):
        # iterable, so create a list for each condition and flatten
        return [*flatten_list([loot_function_list(p) for p in data_in])]
    elif type(data_in) is dict:
        # dict, so just use raw data
        return [data_in]
    else:
        raise RuntimeError('Unknown object %s at loot_function_list' % str(data_in))


def loot_condition_list(data_in: str or dict or list or tuple) -> list:
    # a list of loot pool conditions
    if type(data_in) is str:
        # string, so just accept a name
        return [{'condition': data_in}]
    elif type(data_in) in (list, tuple):
        # iterable, so create a list for each condition and flatten
        return [*flatten_list([loot_condition_list(p) for p in data_in])]
    elif type(data_in) is dict:
        # dict, so just use raw data
        return [data_in]
    else:
        raise RuntimeError('Unknown object %s at loot_condition_list' % str(data_in))


def loot_default_conditions(loot_type: str) -> list or None:
    if loot_type == 'block':
        return [{'condition': 'minecraft:survives_explosion'}]
    else:
        return None
