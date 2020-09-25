#  Part of mcresources by Alex O'Neill
#  Work under copyright. Licensed under MIT
#  For more information see the project LICENSE file

from typing import Union, Sequence, Dict, Any, Optional

from mcresources import utils


def configure(name_parts: utils.ResourceIdentifier, config: Optional[Dict[str, Any]] = None):
    """ Creates a configured object from a resource identifier (the type), and an optional config entry. This can be chained. """
    res = utils.resource_location(name_parts)
    if config is None:
        config = {}
    return {
        'type': res.join(),
        'config': config
    }


def decorated(feature: Dict[str, Any], decorator_name_parts: utils.ResourceIdentifier, config: Optional[Dict[str, Any]] = None) -> utils.Json:
    """ Creates an entry of a 'minecraft:decorated' feature, allowing both a feature and decorator config to be chained. """
    decorator_res = utils.resource_location(decorator_name_parts)
    if config is None:
        config = {}
    return {
        'type': 'minecraft:decorated',
        'config': {
            'feature': feature,
            'decorator': {
                'type': decorator_res.join(),
                'config': config
            }
        }
    }


def surface_builder_config(top_material: Union[str, Dict[str, Any]], under_material: Union[str, Dict[str, Any]], underwater_material: Union[str, Dict[str, Any]]) -> utils.Json:
    """ Creates an instance of a surface builder configuration from three block state identifiers. """
    return {
        'top_material': block_state(top_material),
        'under_material': block_state(under_material),
        'underwater_material': block_state(underwater_material)
    }


def expand_type_config(data: Union[str, Sequence, Dict[str, Any]]) -> utils.Json:
    """ Expands a type-config pattern. """
    if isinstance(data, Dict):
        if 'type' not in data:
            raise RuntimeError('Missing \'type\' key in expand_type_config for object %s' % str(data))
        if 'config' not in data:
            data['config'] = {}
        return data
    elif isinstance(data, str):
        return {'type': data, 'config': {}}
    elif isinstance(data, Sequence) and len(data) == 2 and isinstance(data[0], str) and isinstance(data[1], Dict):
        return {'type': data[0], 'config': data[1]}
    else:
        raise RuntimeError('Unknown object %s at expand_type_config' % str(data))


def block_state(data: Union[str, Dict[str, Any]]):
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
            raise RuntimeError('Missing \'Name\' key in block_state for object %s' % str(data))
        if 'Properties' not in data:
            data['Properties'] = {}
        return data
    else:
        raise RuntimeError('Unknown object %s at block_state' % str(data))
