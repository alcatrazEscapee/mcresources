#  Part of mcresources by Alex O'Neill
#  Work under copyright. Licensed under MIT
#  For more information see the project LICENSE file

from mcresources.type_definitions import Json, ResourceLocation, ResourceIdentifier, TypeWithOptionalConfig
from mcresources import utils

from mcresources.block_context import BlockContext
from mcresources.item_context import ItemContext
from mcresources.recipe_context import RecipeContext
from mcresources.tag import Tag

from typing import Sequence, Dict, Union, Optional, Callable, Any
from collections import defaultdict


class ResourceManager:
    def __init__(self, domain: str = 'minecraft', resource_dir: Sequence[str] = ('src', 'main', 'resources'), indent: int = 2, default_language: str = 'en_us', on_error: Callable[[str, Exception], Any] = None):
        """
        Creates a new Resource Manager. This is the supplier for all resource creation calls.
        :param domain: the domain / mod id for current resources.
        :param indent: the indentation level for all generated json files
        """
        self.resource_dir = utils.str_path(resource_dir)
        self.domain = domain
        self.indent = indent
        self.default_language = default_language
        self.on_error = on_error

        if self.on_error is None:
            self.on_error = lambda file, err: None  # Ignore errors

        # Internal buffers, used for tags and lang entries, which are all written at the same time
        self.lang_buffer: Dict[str, Dict[str, str]] = defaultdict(dict)  # Keys are (language, translation key)
        self.tags_buffer: Dict[str, Dict[ResourceLocation, Tag]] = defaultdict(dict)  # Keys are (tag type, tag name)

        # Statistics
        self.new_files: int = 0
        self.modified_files: int = 0
        self.unchanged_files: int = 0
        self.error_files: int = 0

    def flush(self):
        """
        Flushes all buffered tags and lang files
        """
        for language, contents in self.lang_buffer.items():
            self.write((*self.resource_dir, 'assets', self.domain, 'lang', language), contents)

        for tag_type, tags in self.tags_buffer.items():
            for tag_res, tag in tags.items():
                self.write((*self.resource_dir, 'data', tag_res.domain, 'tags', tag_type, tag_res.path), {
                    'replace': tag.replace,
                    'values': [v.join() for v in tag.values]
                })

        self.lang_buffer.clear()
        self.tags_buffer.clear()

    def block(self, name_parts: ResourceIdentifier) -> BlockContext:
        return BlockContext(self, utils.resource_location(self.domain, name_parts))

    def item(self, name_parts: ResourceIdentifier) -> ItemContext:
        return ItemContext(self, utils.resource_location(self.domain, name_parts))

    def blockstate(self, name_parts: ResourceIdentifier, model: str = None, variants: Dict[str, Json] = None, use_default_model: bool = True) -> BlockContext:
        """
        Creates a blockstate file
        :param name_parts: the resource location, including path elements.
        :param model: the model, used if there are no variants. Defaults to 'domain:block/name/parts'
        :param variants: the variants, as they would be present in json
        :param use_default_model: if a model is missing for a variant, should this populate the variant using the assumed model
        """
        res = utils.resource_location(self.domain, name_parts)
        if model is None:
            model = res.join('block/')
        if variants is None:
            variants = {'': {'model': model}}
        if use_default_model:
            for key, prop in variants.items():
                if 'model' not in prop:
                    prop['model'] = model
        self.write((*self.resource_dir, 'assets', res.domain, 'blockstates', res.path), {
            'variants': variants
        })
        return BlockContext(self, res)

    def blockstate_multipart(self, name_parts: ResourceIdentifier, *parts: Json) -> BlockContext:
        """
        Creates a blockstate file, using the multipart model syntax
        :param name_parts: the resource location, including path elements.
        :param parts: The parts. Each element can be a 2-element sequence of a 'when' and 'apply' json, or a single 'apply' json.
        """
        res = utils.resource_location(self.domain, name_parts)
        self.write((*self.resource_dir, 'assets', res.domain, 'blockstates', res.path), {
            'multipart': utils.blockstate_multipart_parts(parts)
        })
        return BlockContext(self, res)

    def block_model(self, name_parts: ResourceIdentifier, textures: Union[Dict[str, str], Sequence[str]] = None, parent: Union[str, None] = 'block/cube_all', elements: Json = None, no_textures: bool = False) -> BlockContext:
        """
        Creates a block model file
        :param name_parts: the resource location, including path elements.
        :param textures: the textures for the model. Defaults to 'domain:block/name/parts'
        :param parent: the parent model. If none, it is omitted
        :param elements: elements of the model. Can be a single element, which will get expanded to a list of one element
        :param no_textures: If true, textures will be ignored.
        """
        res = utils.resource_location(self.domain, name_parts)
        if textures is None:
            if not no_textures:
                textures = {'all': res.join('block/')}
        elif isinstance(textures, str):
            textures = {'all': textures}
        elif isinstance(textures, Sequence):
            textures = dict((k, res.join('block')) for k in textures)
        if isinstance(elements, Dict):
            elements = [elements]
        self.write((*self.resource_dir, 'assets', res.domain, 'models', 'block', res.path), {
            'parent': parent,
            'textures': textures,
            'elements': elements
        })
        return BlockContext(self, res)

    def custom_block_model(self, name_parts: ResourceIdentifier, loader: ResourceIdentifier, data: Dict[str, Any]) -> BlockContext:
        res = utils.resource_location(self.domain, name_parts)
        self.write((*self.resource_dir, 'assets', res.domain, 'models', 'block', res.path), {
            'loader': utils.resource_location(loader).join(),
            **data,
        })
        return BlockContext(self, res)

    def item_model(self, name_parts: ResourceIdentifier, *textures: Union[Json, str], parent: ResourceIdentifier = 'item/generated', no_textures: bool = False) -> ItemContext:
        """
        Creates an item model file
        :param name_parts: the resource location, including path elements.
        :param textures: the textures for the model. Defaults to 'domain:item/name/parts'
        :param parent: the parent model.
        :param no_textures: if the textures element should be ignored
        """
        res = utils.resource_location(self.domain, name_parts)
        if no_textures:
            textures = None
        else:
            if textures is None or len(textures) == 0:
                textures = res.join('item/'),
            textures = utils.item_model_textures(textures)
        self.write((*self.resource_dir, 'assets', res.domain, 'models', 'item', res.path), {
            'parent': utils.resource_location(parent).join(simple=True),
            'textures': textures
        })
        return ItemContext(self, res)

    def custom_item_model(self, name_parts: ResourceIdentifier, loader: ResourceIdentifier, data: Dict[str, Any]) -> ItemContext:
        res = utils.resource_location(self.domain, name_parts)
        self.write((*self.resource_dir, 'assets', res.domain, 'models', 'item', res.path), {
            'loader': utils.resource_location(loader).join(),
            **data
        })
        return ItemContext(self, res)

    def crafting_shapeless(self, name_parts: ResourceIdentifier, ingredients: Json, result: Json, group: str = None, conditions: Optional[Json] = None) -> RecipeContext:
        """
        Creates a shapeless crafting recipe.
        :param name_parts: The resource location, including path elements.
        :param ingredients: The ingredients.
        :param result: The result of crafting the recipe.
        :param group: The group.
        :param conditions: Any conditions for the recipe to be enabled.
        """
        res = utils.resource_location(self.domain, name_parts)
        self.write((*self.resource_dir, 'data', res.domain, 'recipes', res.path), {
            'type': 'minecraft:crafting_shapeless',
            'group': group,
            'ingredients': utils.item_stack_list(ingredients),
            'result': utils.item_stack(result),
            'conditions': utils.recipe_condition(conditions)
        })
        return RecipeContext(self, res)

    def crafting_shaped(self, name_parts: ResourceIdentifier, pattern: Sequence[str], ingredients: Json, result: Json, group: str = None, conditions: Optional[Json] = None) -> RecipeContext:
        """
        Creates a shaped crafting recipe.
        :param name_parts: The resource location, including path elements.
        :param pattern: The pattern for the recipe.
        :param ingredients: The ingredients, indexed by key in pattern.
        :param result: The result of crafting the recipe.
        :param group: The group.
        :param conditions: Any conditions for the recipe to be enabled.
        """
        res = utils.resource_location(self.domain, name_parts)
        self.write((*self.resource_dir, 'data', res.domain, 'recipes', res.path), {
            'type': 'minecraft:crafting_shaped',
            'group': group,
            'pattern': pattern,
            'key': utils.item_stack_dict(ingredients, ''.join(pattern)[0]),
            'result': utils.item_stack(result),
            'conditions': utils.recipe_condition(conditions)
        })
        return RecipeContext(self, res)

    def recipe(self, name_parts: ResourceIdentifier, type_in: str, data_in: Dict[str, Any], group: str = None, conditions: Json = None) -> RecipeContext:
        """
        Creates a non-crafting recipe file, used for custom mod recipes using vanilla's data pack system
        :param name_parts: The resource location, including path elements.
        :param type_in: The type of the recipe.
        :param data_in: Data required by the recipe, as present in json
        :param group: The group.
        :param conditions: Any conditions for the recipe to be enabled.
        """
        res = utils.resource_location(self.domain, name_parts)
        self.write((*self.resource_dir, 'data', res.domain, 'recipes', res.path), {
            'type': type_in,
            'group': group,
            **data_in,
            'conditions': utils.recipe_condition(conditions)
        })
        return RecipeContext(self, res)

    def data(self, name_parts: ResourceIdentifier, data_in: Dict[str, Any], root_domain: str = 'data'):
        """
        Creates a generic data file. Used for anything and everything under the sun.
        :param name_parts: The resource location, including path elements.
        :param data_in: Data to be inserted into the json
        :param root_domain: The root location (either data or assets) to insert into
        """
        res = utils.resource_location(self.domain, name_parts)
        self.write((*self.resource_dir, root_domain, res.domain, res.path), data_in)

    def advancement(self, name_parts: ResourceIdentifier, display: Json = None, parent: str = None, criteria: Dict[str, Dict[str, Json]] = None, requirements: Sequence[Sequence[str]] = None, rewards: Dict[str, Json] = None):
        """
        Creates a generic advancement. Performs basic filling in of data types
        :param name_parts: The resource location, including path elements.
        :param display: The display data. Inserted as is.
        :param parent: The parent advancement registry name
        :param criteria: The criteria for an advancement. Inserted as is.
        :param requirements: The requirements. If None, will default to a list of all the requirements (OR'd together).
        :param rewards: The rewards. Inserted as is.
        """
        res = utils.resource_location(self.domain, name_parts)
        if requirements is None:
            requirements = [[k for k in criteria.keys()]]
        self.write((*self.resource_dir, 'data', res.domain, 'advancements', res.path), {
            'parent': parent,
            'criteria': criteria,
            'display': display,
            'requirements': requirements,
            'rewards': rewards
        })

    def tag(self, name_parts: ResourceIdentifier, root_domain: str, *values: ResourceIdentifier, replace: bool = None):
        """
        Creates or appends to a tag entry
        :param name_parts: The resource location, including path elements.
        :param root_domain: The root domain of the tag. Should be 'blocks', 'items', 'fluids', or 'entity_types'
        :param values: The resource location values for the tag
        :param replace: If the tag should replace previous values
        """
        res = utils.resource_location(self.domain, name_parts)
        values = [utils.resource_location(self.domain, v) for v in values]
        if res not in self.tags_buffer[root_domain]:
            if replace is None:
                replace = False
            tag = Tag(replace)
            tag.add_all(values)
            self.tags_buffer[root_domain][res] = tag
        else:
            self.tags_buffer[root_domain][res].add_all(values)
            if replace is not None:
                self.tags_buffer[root_domain][res].replace = replace

    def item_tag(self, name_parts: ResourceIdentifier, *values: ResourceIdentifier, replace: bool = None):
        self.tag(name_parts, 'items', *values, replace=replace)

    def block_tag(self, name_parts: ResourceIdentifier, *values: ResourceIdentifier, replace: bool = None):
        self.tag(name_parts, 'blocks', *values, replace=replace)

    def entity_tag(self, name_parts: ResourceIdentifier, *values: ResourceIdentifier, replace: bool = None):
        self.tag(name_parts, 'entity_types', *values, replace=replace)

    def fluid_tag(self, name_parts: ResourceIdentifier, *values: ResourceIdentifier, replace: bool = None):
        self.tag(name_parts, 'fluids', *values, replace=replace)

    def block_loot(self, name_parts: ResourceIdentifier, *loot_pools: Json) -> BlockContext:
        """
        Creates a loot table for a block
        :param name_parts: The resource location, including path elements.
        :param loot_pools: Loot pools. Each argument is interpreted as a single pool.
            Loot pools may be a single string (which will be expanded to a single default 'minecraft:item' entry),
            or a dictionary, which will be expanded into either a single loot pool, or single loot entry based on context,
            or a sequence of loot entries, which will be expanded into a 'minecraft:alternatives' loot entry, and loot pool.
        """
        res = self.loot(name_parts, *loot_pools, path='blocks', loot_type='minecraft:block')
        return BlockContext(self, res)

    def entity_loot(self, name_parts: ResourceIdentifier, *loot_pools: Json):
        """
        Creates a loot table for an entity.
        Parameters are the same as above.
        """
        self.loot(name_parts, *loot_pools, path='entities', loot_type='minecraft:entity')

    def loot(self, name_parts: ResourceIdentifier, *loot_pools: Json, path: str, loot_type: str) -> ResourceLocation:
        res = utils.resource_location(self.domain, name_parts)
        self.write((*self.resource_dir, 'data', res.domain, 'loot_tables', path, res.path), {
            'type': loot_type,
            'pools': [
                utils.loot_pool(pool, path)
                for pool in loot_pools
            ]
        })
        return res

    def lang(self, *args: Union[str, Sequence[str], Dict[str, str]], language: str = None):
        """
        :param args: The lang entries. Can be paired key, value strings, or a dictionary of key -> value maps
        :param language: The language key. Defaults to the default language supplied in the resource manager constructor
        """
        if language is None:
            language = self.default_language
        for key, val in utils.lang_parts(args).items():
            self.lang_buffer[language][key] = val

    # === World Generation === #

    def dimension(self, name_parts: ResourceIdentifier, dimension_type: ResourceIdentifier, generator: Json):
        res = utils.resource_location(self.domain, name_parts)
        self.write((*self.resource_dir, 'data', res.domain, 'dimension', res.path), {
            'type': utils.resource_location(dimension_type).join(),
            'generator': generator
        })

    def dimension_type(self, name_parts: ResourceIdentifier, fixed_time: int, has_skylight: bool, has_ceiling: bool, ultrawarm: bool, natural: bool, coordinate_scale: float, piglin_safe: bool, bed_works: bool, respawn_anchor_works: bool, has_raids: bool, min_y: int, height: int, logical_height: int, infiniburn: ResourceIdentifier, effects: ResourceIdentifier, ambient_light: float):
        res = utils.resource_location(self.domain, name_parts)
        self.write((*self.resource_dir, 'data', res.domain, 'dimension_type', res.path), {
            'fixed_time': fixed_time,
            'has_skylight': has_skylight,
            'has_ceiling': has_ceiling,
            'ultrawarm': ultrawarm,
            'natural': natural,
            'coordinate_scale': coordinate_scale,
            'piglin_safe': piglin_safe,
            'bed_works': bed_works,
            'respawn_anchor_works': respawn_anchor_works,
            'has_raids': has_raids,
            'min_y': min_y,
            'height': height,
            'logical_height': logical_height,
            'infiniburn': utils.resource_location(infiniburn).join(),
            'effects': utils.resource_location(effects).join(),
            'ambient_light': ambient_light
        })

    def biome(self, name_parts: ResourceIdentifier, precipitation: str = 'none', category: str = 'none', temperature: float = 0, temperature_modifier: str = 'none', downfall: float = 0.5, effects: Optional[Json] = None, air_carvers: Optional[Sequence[str]] = None, water_carvers: Optional[Sequence[str]] = None, features: Sequence[Sequence[str]] = None, structures: Sequence[str] = None, spawners: Optional[Json] = None, player_spawn_friendly: bool = True, creature_spawn_probability: float = 0.5, parent: Optional[str] = None, spawn_costs: Optional[Json] = None):
        """ Creates a biome, with all possible optional parameters filled in to the minimum required state. Parameters are exactly as they appear in the final biome. """
        if effects is None:
            effects = {}
        for required_effect in ('fog_color', 'sky_color', 'water_color', 'water_fog_color'):
            if required_effect not in effects:
                effects[required_effect] = 0

        if features is None:
            features = []
        if structures is None:
            structures = []
        if spawners is None:
            spawners = {}
        if spawn_costs is None:
            spawn_costs = {}
        res = utils.resource_location(self.domain, name_parts)
        self.write((*self.resource_dir, 'data', res.domain, 'worldgen', 'biome', res.path), {
            'precipitation': precipitation,
            'category': category,
            'temperature': temperature,
            'temperature_modifier': temperature_modifier,
            'downfall': downfall,
            'effects': effects,
            'carvers': {
                'air': air_carvers,
                'liquid': water_carvers
            },
            'features': features,
            'starts': structures,
            'spawners': spawners,
            'player_spawn_friendly': player_spawn_friendly,
            'creature_spawn_probability': creature_spawn_probability,
            'parent': parent,
            'spawn_costs': spawn_costs
        })

    def configured_carver(self, name_parts: ResourceIdentifier, feature: ResourceIdentifier, config: Json = None):
        return self.configured(name_parts, feature, config, 'configured_carver')

    def configured_feature(self, name_parts: ResourceIdentifier, feature: ResourceIdentifier, config: Json = None):
        return self.configured(name_parts, feature, config, 'configured_feature')

    def configured_structure_feature(self, name_parts: ResourceIdentifier, feature: ResourceIdentifier, config: Json = None):
        return self.configured(name_parts, feature, config, 'configured_structure_feature')

    def configured(self, name_parts: ResourceIdentifier, feature: ResourceIdentifier, config: Json = None, root: str = ''):
        res = utils.resource_location(self.domain, name_parts)
        self.write((*self.resource_dir, 'data', res.domain, 'worldgen', root, res.path), utils.configure(feature, config))

    def placed_feature(self, name_parts: ResourceIdentifier, feature: ResourceIdentifier, *placements: TypeWithOptionalConfig):
        res = utils.resource_location(self.domain, name_parts)
        self.write((*self.resource_dir, 'data', res.domain, 'worldgen', 'placed_feature', res.path), {
            'feature': utils.resource_location(feature).join(),
            'placement': [
                utils.configured_placement(p)
                for p in placements
            ]
        })

    def noise(self, name_parts: ResourceIdentifier, first_octave: float, *amplitudes: float):
        res = utils.resource_location(self.domain, name_parts)
        self.write((*self.resource_dir, 'data', res.domain, 'worldgen', 'noise', res.path), {
            'firstOctave': first_octave,
            'amplitudes': amplitudes
        })

    def noise_settings(self, name_parts: ResourceIdentifier, ore_veins_enabled: bool, noodle_caves_enabled: bool, legacy_random_source: bool, disable_mob_generation: bool, aquifers_enabled: bool, noise_caves_enabled: bool, default_block: Json, default_fluid: Json, sea_level: int, noise: Json, surface_rule: Json, structures: Json):
        res = utils.resource_location(self.domain, name_parts)
        self.write((*self.resource_dir, 'data', res.domain, 'worldgen', 'noise_settings', res.path), {
            'ore_veins_enabled': ore_veins_enabled,
            'noodle_caves_enabled': noodle_caves_enabled,
            'legacy_random_source': legacy_random_source,
            'disable_mob_generation': disable_mob_generation,
            'aquifers_enabled': aquifers_enabled,
            'noise_caves_enabled': noise_caves_enabled,
            'default_block': utils.block_state(default_block),
            'default_fluid': utils.block_state(default_fluid),
            'sea_level': sea_level,
            'noise': noise,
            'surface_rule': surface_rule,
            'structures': structures
        })

    def processor_list(self, name_parts: ResourceIdentifier, *processors: Json):
        res = utils.resource_location(self.domain, name_parts)
        self.write((*self.resource_dir, 'data', res.domain, 'worldgen', 'processor_list', res.path), {
            'processors': processors
        })

    def template_pool(self, name_parts: ResourceIdentifier, data: Json):
        res = utils.resource_location(self.domain, name_parts)
        self.write((*self.resource_dir, 'data', res.domain, 'worldgen', 'template_pool', res.path), data)

    def write(self, path_parts: Sequence[str], data: Json):
        """
        Writes data to a file, inserting an autogenerated comment and deletes None entries from the data
        :param path_parts: The path elements of the file
        :param data: The json data to write
        """
        data = utils.del_none({'__comment__': 'This file was automatically created by mcresources', **data})
        flag = utils.write(path_parts, data, self.indent, self.on_error)
        if flag == utils.WriteFlag.NEW:
            self.new_files += 1
        elif flag == utils.WriteFlag.MODIFIED:
            self.modified_files += 1
        elif flag == utils.WriteFlag.UNCHANGED:
            self.unchanged_files += 1
        elif flag == utils.WriteFlag.ERROR:
            self.error_files += 1
