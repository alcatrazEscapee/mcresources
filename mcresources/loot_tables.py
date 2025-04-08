"""
Common functions for creating loot table related objects, such as loot conditions, functions, or loot pools.

Usage:
```python
from mcresources import loot_tables
```
"""

from mcresources.type_definitions import Json, JsonObject
from mcresources import utils

from typing import Optional, Sequence

# General utils for creating loot pools, and loot entries

def pool(*entries: Json, conditions: Optional[Json] = None, functions: Optional[Json] = None, rolls: int = 1, bonus_rolls: Optional[int] = None) -> JsonObject:
    return {
        'entries': entries,
        'conditions': conditions,
        'functions': functions,
        'rolls': rolls,
        'bonus_rolls': bonus_rolls
    }


def alternatives(*entries: Json, conditions: Optional[Json] = None, functions: Optional[Json] = None) -> JsonObject:
    return {
        'type': 'minecraft:alternatives',
        'children': entries,
        'conditions': conditions,
        'functions': functions
    }


# Loot Conditions

def all_of(*terms: Json) -> Json:
    return {
        'condition': 'minecraft:all_of',
        'terms': utils.loot_conditions(terms)
    }

def any_of(*terms: Json) -> Json:
    return {
        'condition': 'minecraft:any_of',
        'terms': utils.loot_conditions(terms)
    }

def inverted(term: Json) -> Json:
    condition = utils.loot_conditions(term)
    assert len(condition) == 1, 'Expected one condition for inverted() term'
    return {
        'condition': 'minecraft:inverted',
        'term': condition[0]
    }

def random_chance(chance: float) -> Json:
    return {
        'condition': 'minecraft:random_chance',
        'chance': chance
    }

def block_state_property(data: Json) -> Json:
    """ Accepts a block like 'minecraft:grass[snowy=true]', or a dictionary with 'Name' and 'Properties' entries """
    block_state = utils.block_state(data)
    assert 'Name' in block_state, 'Missing Name'
    assert 'Properties' in block_state and len(block_state['Properties']) > 0, 'Requires at least one property'
    return {
        'condition': 'minecraft:block_state_property',
        'block': block_state['Name'],
        'properties': block_state['Properties']
    }

def match_tag(tag: str) -> Json:
    return {
        'condition': 'minecraft:match_tool',
        'predicate': {'tag': tag}
    }

def silk_touch() -> Json:
    return {
        'condition': 'minecraft:match_tool',
        'predicate': {
            'enchantments': [{
                'enchantment': 'minecraft:silk_touch',
                'levels': {'min': 1}
            }]
        }
    }

def fortune_table(chances: Sequence[float]) -> Json:
    return {
        'condition': 'minecraft:table_bonus',
        'enchantment': 'minecraft:fortune',
        'chances': chances
    }

def survives_explosion() -> Json:
    return 'minecraft:survives_explosion'


# Loot Functions

def set_count(min_inclusive: int = 1, max_inclusive: int = -1) -> JsonObject:
    """ `minecraft:set_count` function """
    if max_inclusive == -1:
        count = min_inclusive
    else:
        count = {'min': min_inclusive, 'max': max_inclusive, 'type': 'minecraft:uniform'}
    return {
        'function': 'minecraft:set_count',
        'count': count
    }

def fortune_bonus(multiplier: int = 1) -> JsonObject:
    """ `minecraft:apply_bonus` function with the fortune enchantment, with a uniform bonus count
    :param multiplier: the bonusMultiplier
    """
    return {
        'function': 'minecraft:apply_bonus',
        'enchantment': 'minecraft:fortune',
        'formula': 'minecraft:uniform_bonus_count',
        'parameters': {
            'bonusMultiplier': multiplier
        }
    }

def explosion_decay() -> JsonObject:
    return {
        'function': 'minecraft:explosion_decay'
    }
