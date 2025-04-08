"""
Common functions for creating atlas sources and related objects

Usage:
```python
from mcresources import atlases
```
"""

from mcresources.type_definitions import Json
from mcresources import utils

from typing import Tuple, List, Dict

def directory(source: str, prefix: str = None) -> Json:
    """
    Includes a whole directory.
    :param source: the directory, under assets/mod_id/textures/
    :param prefix: the path to be prefixed to the texture name. If left blank it follows the folder -> / convention. For things like particles, the convention is to specify '' (no prefix)
    """
    return {
        'type': 'directory',
        'source': source,
        'prefix': source + '/' if prefix is None else prefix
    }

def single(resource: utils.ResourceIdentifier) -> Json:
    """
    Includes a single file.
    :param resource: the texture location as it would appear in a model file, eg. 'minecraft:block/dirt'
    """
    return {
        'type': 'single',
        'resource': resource
    }

def palette(key: str, textures: List[str], permutations: Dict[str, str]) -> Json:
    """
    Creates a permutation of paletted textures in memory that can be referenced by other files.
    The implementation can be thought of like this:
    
    for suffix, colors in permutations:
        for texture in textures:
            replace texture colors with colors
            save texture as 'texture_suffix'

    :param key: A texture location for the palette key file, typically the grayscale version of the color palette
    :param textures: The textures the permutations of color palettes will be applied to. These are grayscale and have the same colors as the palette key file.
    :param permutations: A dictionary of suffixes to color palettes. The resulting textures get '_' and then the suffix appended. The color palettes should match the length of the palette key file.
    """
    return {
        'type': 'paletted_permutations',
        'palette_key': key,
        'textures': textures,
        'permutations': permutations
    }

def filter(namespace_matcher: str = None, path_matcher: str = None) -> Json:
    """
    Removes sprites from the atlas
    :param namespace_matcher: Regex for namespaces to match. If omitted, matches everything.
    :param path_matcher: Regex for paths to match. If omitted, matches everything.
    """
    return {
        'type': 'filter',
        'namespace': namespace_matcher,
        'path': path_matcher
    }

def unstitch(resource: str, divisor_x: int, divisor_y: int, *regions: Tuple[str, int, int, int, int]) -> Json:
    """
    Copies a rectangle from another image.
    Values such as 'x' in the region specification are transformed to real image coordinates via dividing by their divisor, and then multiplying by the real image size
    :param resource: The texture location of the image to copy from, eg. minecraft:block/dirt
    :divisor_x: The coordinates of the region are divided by this value on the x axis
    :divisor_y: The coordinates of the region are divided by this value on the y axis
    :regions: A tuple of the new sprite name, the x and y coordinates of the top left corner of the region, and the width and height of the region.
    """
    return {
        'type': 'unstitch',
        'resource': resource,
        'divisor_x': divisor_x,
        'divisor_y': divisor_y,
        'regions': [
            {
                'sprite': sprite,
                'x': x,
                'y': y,
                'width': width,
                'height': height
            }
        for sprite, x, y, width, height in regions]
    }