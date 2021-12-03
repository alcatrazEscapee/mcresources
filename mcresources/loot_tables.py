#  Part of mcresources by Alex O'Neill
#  Work under copyright. Licensed under MIT
#  For more information see the project LICENSE file

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

def or_condition(*terms: Json) -> JsonObject:
    return {
        'condition': 'minecraft:alternative',
        'terms': utils.loot_conditions(terms)
    }

def not_condition(term: Json) -> JsonObject:
    condition = utils.loot_conditions(term)
    assert len(condition) == 1, 'Expected one condition for not_condition() term'
    return {
        'condition': 'minecraft:not',
        'term': condition[0]
    }

def random_chance(chance: float) -> JsonObject:
    return {
        'condition': 'minecraft:random_chance',
        'chance': chance
    }

def block_state_property(data: Json) -> JsonObject:
    """ Accepts a block like 'minecraft:grass[snowy=true]', or a dictionary with 'Name' and 'Properties' entries """
    block_state = utils.block_state(data)
    assert 'Name' in block_state, 'Missing Name'
    assert 'Properties' in block_state and len(block_state['Properties']) > 0, 'Requires at least one property'
    return {
        'condition': 'minecraft:block_state_property',
        'block': block_state['Name'],
        'properties': block_state['Properties']
    }

def match_tag(tag: str) -> JsonObject:
    return {
        'condition': 'minecraft:match_tool',
        'predicate': {'tag': tag}
    }

def silk_touch() -> JsonObject:
    return {
        'condition': 'minecraft:match_tool',
        'predicate': {
            'enchantments': [{
                'enchantment': 'minecraft:silk_touch',
                'levels': {'min': 1}
            }]
        }
    }

def fortune_table(chances: Sequence[float]) -> JsonObject:
    return {
        'condition': 'minecraft:table_bonus',
        'enchantment': 'minecraft:fortune',
        'chances': chances
    }

def survives_explosion() -> JsonObject:
    return {
        'condition': 'minecraft:survives_explosion'
    }


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

def copy_block_entity_name() -> JsonObject:
    return {
        'function': 'minecraft:copy_name',
        'source': 'block_entity'
    }

def copy_block_entity_nbt() -> JsonObject:
    return {
        'function': 'minecraft:copy_nbt',
        'source': 'block_entity',
        'ops': [{
            'source': '',
            'target': 'BlockEntityTag',
            'op': 'replace'
        }]
    }
