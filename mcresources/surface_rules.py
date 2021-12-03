from type_definitions import Json, JsonObject, ResourceIdentifier, VerticalAnchor
from mcresources import utils

from typing import Literal, Sequence


# Surface Rules

def block(result_state: Json) -> JsonObject:
    return {
        'type': 'minecraft:block',
        'result_state': utils.block_state(result_state)
    }

def sequence(*rules: JsonObject) -> JsonObject:
    return {
        'type': 'minecraft:sequence',
        'sequence': list(rules)
    }

def condition(predicate: JsonObject, then: JsonObject) -> JsonObject:
    return {
        'type': 'minecraft:condition',
        'if_true': predicate,
        'then_run': then
    }

def badlands() -> JsonObject:
    return {
        'type': 'minecraft:badlands'
    }

# Conditions

def biome_condition(biomes: Sequence[ResourceIdentifier], then: JsonObject) -> JsonObject:
    return condition({
        'type': 'minecraft:biome',
        'biome_is': [utils.resource_location(r).join() for r in utils.str_list(biomes)]
    }, then)

def noise_threshold_condition(noise: ResourceIdentifier, min_value: float, max_value: float, then: JsonObject) -> JsonObject:
    return condition({
        'type': 'minecraft:noise_threshold',
        'noise': utils.resource_location(noise).join(),
        'min_threshold': min_value,
        'max_threshold': max_value
    }, then)

def vertical_gradient_condition(random_name: ResourceIdentifier, true_below: VerticalAnchor, false_above: VerticalAnchor, then: JsonObject) -> JsonObject:
    return condition({
        'type': 'minecraft:vertical_gradient',
        'random_name': random_name,
        'true_at_and_below': utils.as_vertical_anchor(true_below),
        'false_at_and_above': utils.as_vertical_anchor(false_above),
    }, then)

def y_above_condition(anchor: VerticalAnchor, surface_depth_multiplier: int, add_stone_depth: bool, then: JsonObject) -> JsonObject:
    return condition({
        'type': 'minecraft:y_above',
        'anchor': utils.as_vertical_anchor(anchor),
        'surface_depth_multiplier': surface_depth_multiplier,
        'add_stone_depth': add_stone_depth
    }, then)

def water_condition(offset: int, surface_depth_multiplier: int, add_stone_depth: bool, then: JsonObject) -> JsonObject:
    return condition({
        'type': 'minecraft:water',
        'offset': offset,
        'surface_depth_multiplier': surface_depth_multiplier,
        'add_stone_depth': add_stone_depth
    }, then)

def temperature_condition(then: JsonObject) -> JsonObject:
    return condition({'type': 'minecraft:temperature'}, then)

def steep_condition(then: JsonObject) -> JsonObject:
    return condition({'type': 'minecraft:steep'}, then)

def not_condition(invert: JsonObject, then: JsonObject) -> JsonObject:
    return condition({
        'type': 'minecraft:not',
        'invert': invert
    }, then)

def hole_condition(then: JsonObject) -> JsonObject:
    return condition({'type': 'minecraft:hole'}, then)

def above_preliminary_surface_condition(then: JsonObject) -> JsonObject:
    return condition({'type': 'minecraft:above_preliminary_surface'}, then)

def stone_depth_condition(offset: int, add_surface_depth: bool, add_surface_secondary_depth: bool, surface_type: Literal['ceiling', 'floor'], then: JsonObject) -> JsonObject:
    return condition({
        'type': 'minecraft:stone_depth',
        'offset': offset,
        'add_surface_depth': add_surface_depth,
        'add_surface_secondary_depth': add_surface_secondary_depth,
        'surface_type': surface_type
    }, then)
