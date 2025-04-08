import os.path

from mcresources.type_definitions import Json, JsonObject, ResourceLocation, ResourceIdentifier, TypeWithOptionalConfig
from mcresources import utils

from mcresources.block_context import BlockContext
from mcresources.item_context import ItemContext
from mcresources.recipe_context import RecipeContext
from mcresources.tag import Tag

from typing import Sequence, Dict, Union, Optional, Callable, Any
from collections import defaultdict


class ResourceManager:
    """
    This is the central class for generating resources to a specific domain (modid), and output path. It contains methods for generating
    individual resource types and files. Refer to the documentation on each method for specifics.

    Example Usage:
    ```python
    from mcresources import ResourceManager

    rm = ResourceManager('my_fancy_modid')
    # resource generation here
    rm.flush()  # call flush to finish any tag or lang files, see note below
    ```

    <strong>Important:</strong> When generating files such as tags or lang, the `ResourceManager` does not create the files every time `.tag()` or `.lang()` is invoked. Rather, it collects all values from all invocations, until a call to `.flush()` is made, which then writes all tag and lang files together.

    All resource generation methods take a `ResourceIdentifier` as the `name_parts. This is akin to a deconstructed `ResourceLocation` in Minecraft.
    It accepts strings, or lists/tuples of strings, where sequences of strings are interpreted as `/` seperated parts, i.e.

    ```
    rm.block(('foo', 'bar'))  # Creates the block `modid:foo/bar`
    ```

    The namespace is assumed to be the same as the namespace of the `ResourceManager`, if omitted.
    """

    def __init__(self, domain: str = 'minecraft', resource_dir: str = 'src/main/resources', indent: int = 2, ensure_ascii: bool = False, default_language: str = 'en_us', on_error: Callable[[str, Exception], Any] = None):
        """
        Creates a new Resource Manager. This is the supplier for all resource creation calls.
        :param domain: the domain / mod id for current resources.
        :param indent: the indentation level for all generated json files
        :param ensure_ascii: The ensure_ascii passed to json.dump - if non-ascii characters should be replaced with escape sequences.
        """
        self.resource_dir: str = os.path.normpath(resource_dir)
        self.domain: str = domain
        self.indent: int = indent
        self.ensure_ascii: bool = ensure_ascii
        self.default_language: str = default_language
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
        self.written_files: set[str] = set()

    def flush(self):
        """
        Flushes all buffered tags and lang files
        """
        for language, contents in self.lang_buffer.items():
            self.write(('assets', self.domain, 'lang', language), contents)

        for tag_type, tags in self.tags_buffer.items():
            for tag_res, tag in tags.items():
                self.write(('data', tag_res.domain, 'tags', tag_type, tag_res.path), {
                    'replace': tag.replace,
                    'values': tag.values
                })

        self.lang_buffer.clear()
        self.tags_buffer.clear()

    def block(self, name_parts: ResourceIdentifier) -> BlockContext:
        """
        Creates a new {@link BlockContext} without creating any resource files.
        """
        return BlockContext(self, utils.resource_location(self.domain, name_parts))

    def item(self, name_parts: ResourceIdentifier) -> ItemContext:
        """
        Creates a new {@link ItemContext} without creating any resource files.`
        """
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
        self.write(('assets', res.domain, 'blockstates', res.path), {
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
        self.write(('assets', res.domain, 'blockstates', res.path), {
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
        self.write(('assets', res.domain, 'models', 'block', res.path), {
            'parent': parent,
            'textures': textures,
            'elements': elements
        })
        return BlockContext(self, res)

    def custom_block_model(self, name_parts: ResourceIdentifier, loader: ResourceIdentifier, data: JsonObject) -> BlockContext:
        res = utils.resource_location(self.domain, name_parts)
        self.write(('assets', res.domain, 'models', 'block', res.path), {
            'loader': utils.resource_location(loader).join(),
            **data,
        })
        return BlockContext(self, res)

    def item_model(self, name_parts: ResourceIdentifier, *textures: Json, parent: ResourceIdentifier = 'item/generated', no_textures: bool = False, overrides: list[Json] = None) -> ItemContext:
        """
        Creates an item model file
        :param name_parts: the resource location, including path elements.
        :param textures: the textures for the model. Defaults to 'domain:item/name/parts'
        :param parent: the parent model.
        :param no_textures: if the textures element should be ignored
        :param overrides: overrides to add to the item model if present
        """
        res = utils.resource_location(self.domain, name_parts)
        if no_textures:
            textures = None
        else:
            if textures is None or len(textures) == 0:
                textures = res.join('item/'),
            textures = utils.item_model_textures(textures)
        self.write(('assets', res.domain, 'models', 'item', res.path), {
            'parent': utils.resource_location(parent).join(simple=True),
            'textures': textures,
            'overrides': overrides
        })
        return ItemContext(self, res)

    def custom_item_model(self, name_parts: ResourceIdentifier, loader: ResourceIdentifier, data: JsonObject) -> ItemContext:
        res = utils.resource_location(self.domain, name_parts)
        self.write(('assets', res.domain, 'models', 'item', res.path), {
            'loader': utils.resource_location(loader).join(),
            **data
        })
        return ItemContext(self, res)

    def atlas(self, name_parts: ResourceIdentifier, *sources: Json):
        res = utils.resource_location(self.domain, name_parts)
        self.write(('assets', res.domain, 'atlases', res.path), {
            'sources': [s for s in sources]
        })

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
        self.write(('data', res.domain, 'recipes', res.path), {
            'type': 'minecraft:crafting_shapeless',
            'group': group,
            'ingredients': utils.ingredient_list(ingredients),
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
        utils.validate_crafting_pattern(pattern)
        res = utils.resource_location(self.domain, name_parts)
        self.write(('data', res.domain, 'recipes', res.path), {
            'type': 'minecraft:crafting_shaped',
            'group': group,
            'pattern': pattern,
            'key': utils.item_stack_dict(ingredients, ''.join(pattern)[0]),
            'result': utils.item_stack(result),
            'conditions': utils.recipe_condition(conditions)
        })
        return RecipeContext(self, res)

    def recipe(self, name_parts: ResourceIdentifier, type_in: Optional[str], data_in: JsonObject, group: Optional[str] = None, conditions: Json = None) -> RecipeContext:
        """
        Creates a non-crafting recipe file, used for custom mod recipes using vanilla's data pack system
        :param name_parts: The resource location, including path elements.
        :param type_in: The type of the recipe.
        :param data_in: Data required by the recipe, as present in json
        :param group: The group.
        :param conditions: Any conditions for the recipe to be enabled.
        """
        res = utils.resource_location(self.domain, name_parts)
        self.write(('data', res.domain, 'recipes', res.path), {
            'type': type_in,
            'group': group,
            **data_in,
            'conditions': utils.recipe_condition(conditions)
        })
        return RecipeContext(self, res)

    def data(self, name_parts: ResourceIdentifier, data_in: JsonObject, root_domain: str = 'data', prefix_path: str = ''):
        """
        Creates a generic data file. Used for anything and everything under the sun.
        :param name_parts: The resource location, including path elements.
        :param data_in: Data to be inserted into the json
        :param root_domain: The root location (either data or assets) to insert into
        :param prefix_path: A prefix for the path to be inserted to. For example, `prefix_path = 'recipes'` and `name_parts = 'minecraft:foo'` will place data at `data/minecraft/recipes/foo/`
        """
        res = utils.resource_location(self.domain, name_parts)
        self.write((root_domain, res.domain, prefix_path + res.path), data_in)

    def advancement(self, name_parts: ResourceIdentifier, display: Json = None, parent: str = None, criteria: Dict[str, Dict[str, Json]] = None, requirements: Sequence[Sequence[str]] = None, rewards: Dict[str, Json] = None):
        """
        Creates a generic advancement. Performs basic filling in of data types
        :param name_parts: The resource location, including path elements.
        :param display: The display data. Inserted as is.
        :param parent: The parent advancement registry name
        :param criteria: The criteria for an advancement. Inserted as is.
        :param requirements: The requirements. If None or 'or', the criteria names will in one list. If 'and', the criteria will each get their own sublist, which requires all of them to be achieved.
        :param rewards: The rewards. Inserted as is.
        """
        res = utils.resource_location(self.domain, name_parts)
        if requirements is None or requirements == 'or':
            requirements = [[k for k in criteria.keys()]]
        elif requirements == 'and':
            requirements = [[k] for k in criteria.keys()]
        self.write(('data', res.domain, 'advancements', res.path), {
            'parent': parent,
            'criteria': criteria,
            'display': display,
            'requirements': requirements,
            'rewards': rewards
        })

    def block_loot(self, name_parts: ResourceIdentifier, *loot_pools: Json) -> BlockContext:
        """
        Creates a loot table for a block
        :param name_parts: The resource location, including path elements.
        :param loot_pools: Loot pools. Each argument is interpreted as a single pool. Loot pools may be a single string (which will be expanded to a single default `minecraft:item` entry), or a dictionary, which will be expanded into either a single loot pool, or single loot entry based on context, or a sequence of loot entries, which will be expanded into a `minecraft:alternatives` loot entry, and loot pool.
        """
        res = self.loot(name_parts, *loot_pools, path='blocks', loot_type='minecraft:block')
        return BlockContext(self, res)

    def entity_loot(self, name_parts: ResourceIdentifier, *loot_pools: Json):
        """
        Creates a loot table for an entity.
        Parameters are the same as {@link ResourceManager#block_loot}.
        """
        self.loot(name_parts, *loot_pools, path='entities', loot_type='minecraft:entity')

    def loot(self, name_parts: ResourceIdentifier, *loot_pools: Json, path: str, loot_type: str) -> ResourceLocation:
        """
        Creates a generic loot table.
        :param name_parts: The resource location, including path elements.
        :param loot_pools: Loot pools. Each argument is interpreted as a single pool. Loot pools may be a single string (which will be expanded to a single default `minecraft:item` entry), or a dictionary, which will be expanded into either a single loot pool, or single loot entry based on context, or a sequence of loot entries, which will be expanded into a `minecraft:alternatives` loot entry, and loot pool.
        :param path: The root loot table path.
        :param loot_type: The type of the loot table.
        """
        res = utils.resource_location(self.domain, name_parts)
        self.write(('data', res.domain, 'loot_table', path, res.path), {
            'type': loot_type,
            'pools': [
                utils.loot_pool(pool, path)
                for pool in loot_pools
            ]
        })
        return res

    def lang(self, *args: Union[str, Sequence[str], Dict[str, str]], language: str = None):
        """
        Adds lang entries to the `ResourceManager`. Note that this method does not create any resource files and requires a call to
        {@link ResourceManager#flush} to generate all language files.
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
        self.write(('data', res.domain, 'dimension', res.path), {
            'type': utils.resource_location(dimension_type).join(),
            'generator': generator
        })

    def dimension_type(self, name_parts: ResourceIdentifier, fixed_time: int, has_skylight: bool, has_ceiling: bool, ultrawarm: bool, natural: bool, coordinate_scale: float, piglin_safe: bool, bed_works: bool, respawn_anchor_works: bool, has_raids: bool, min_y: int, height: int, logical_height: int, infiniburn: ResourceIdentifier, effects: ResourceIdentifier, ambient_light: float):
        res = utils.resource_location(self.domain, name_parts)
        self.write(('data', res.domain, 'dimension_type', res.path), {
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

    def biome(self, name_parts: ResourceIdentifier, has_precipitation: bool = True, temperature: float = 0, temperature_modifier: str = None, downfall: float = 0.5, effects: Json = None, air_carvers: Sequence[str] = None, water_carvers: Sequence[str] = None, features: Sequence[Sequence[str]] = None, structures: Sequence[str] = None, spawners: Json = None, creature_spawn_probability: float = 0.5, spawn_costs: Json = None):
        """ Creates a biome, with all possible optional parameters filled in to the minimum required state. Parameters are exactly as they appear in the final biome. """
        if effects is None:
            effects = {}
        for required_effect in ('fog_color', 'sky_color', 'water_color', 'water_fog_color'):
            if required_effect not in effects:
                effects[required_effect] = 0
        if features is None:
            features = []
        if spawners is None:
            spawners = {}
        if spawn_costs is None:
            spawn_costs = {}

        res = utils.resource_location(self.domain, name_parts)
        self.write(('data', res.domain, 'worldgen', 'biome', res.path), {
            'has_precipitation': has_precipitation,
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
            'creature_spawn_probability': creature_spawn_probability,
            'spawn_costs': spawn_costs
        })

    def configured_carver(self, name_parts: ResourceIdentifier, carver: ResourceIdentifier, config: Json = None):
        """
        Creates a configured carver file from a carver name and an optional config.
        :param name_parts: The resource location, including path elements
        :param carver: The resource location of the world carver to use
        :param config: The config JSON
        """
        return self.configured(name_parts, carver, config, 'configured_carver')

    def configured_feature(self, name_parts: ResourceIdentifier, feature: ResourceIdentifier, config: Json = None):
        """
        Creates a configured feature file from a feature name and an optional config.
        :param name_parts: The resource location, including path elements
        :param feature: The resource location of the feature to use
        :param config: The config JSON
        """
        return self.configured(name_parts, feature, config, 'configured_feature')

    def configured_structure_feature(self, name_parts: ResourceIdentifier, feature: ResourceIdentifier, config: Json = None):
        """
        Creates a configured structure feature file from a carver name and an optional config.
        :param name_parts: The resource location, including path elements
        :param feature: The resource location of the structure feature to use
        :param config: The config JSON
        """
        return self.configured(name_parts, feature, config, 'configured_structure_feature')

    def configured(self, name_parts: ResourceIdentifier, feature: ResourceIdentifier, config: Json = None, root: str = ''):
        res = utils.resource_location(self.domain, name_parts)
        self.write(('data', res.domain, 'worldgen', root, res.path), utils.configure(feature, config))

    def placed_feature(self, name_parts: ResourceIdentifier, feature: ResourceIdentifier, *placements: TypeWithOptionalConfig):
        """
        Creates a placed feature resource from a feature and a sequence of placements. Placements may be a resource location
        identifying a placement modifier, which will be expanded as `{ type: "my_placement_modifier" }` or a pair of a resource location
        and configuration data, or a raw JSON blob with a `type` field already included.

        :param name_parts: The resource location, including path elements
        :param feature: The resource location of the configured feature to use
        :param placements: A list of placements.
        """
        res = utils.resource_location(self.domain, name_parts)
        self.write(('data', res.domain, 'worldgen', 'placed_feature', res.path), {
            'feature': utils.resource_location(feature).join(),
            'placement': [
                utils.configured_placement(p)
                for p in placements
            ]
        })

    def noise(self, name_parts: ResourceIdentifier, first_octave: float, *amplitudes: float):
        res = utils.resource_location(self.domain, name_parts)
        self.write(('data', res.domain, 'worldgen', 'noise', res.path), {
            'firstOctave': first_octave,
            'amplitudes': amplitudes
        })

    def noise_settings(self, name_parts: ResourceIdentifier, ore_veins_enabled: bool, noodle_caves_enabled: bool, legacy_random_source: bool, disable_mob_generation: bool, aquifers_enabled: bool, noise_caves_enabled: bool, default_block: Json, default_fluid: Json, sea_level: int, noise: Json, surface_rule: Json, structures: Json):
        res = utils.resource_location(self.domain, name_parts)
        self.write(('data', res.domain, 'worldgen', 'noise_settings', res.path), {
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
        self.write(('data', res.domain, 'worldgen', 'processor_list', res.path), {
            'processors': processors
        })

    def template_pool(self, name_parts: ResourceIdentifier, data: Json):
        res = utils.resource_location(self.domain, name_parts)
        self.write(('data', res.domain, 'worldgen', 'template_pool', res.path), data)

    def world_preset(self, name_parts: ResourceIdentifier, dimensions: Json, is_normal: bool = False):
        """
        Creates a world preset from the provided data.
        :param name_parts: The resource location, including path elements.
        :param dimensions: The world preset dimensions.
        :param is_normal: If `True`, then the world preset will be tagged as `minecraft:normal`
        """
        res = utils.resource_location(self.domain, name_parts)
        self.write(('data', res.domain, 'worldgen', 'world_preset', res.path), {'dimensions': dimensions})
        if is_normal:
            self.world_preset_tag('minecraft:normal', name_parts)

    # === Tags === #

    def item_tag(self, name_parts: ResourceIdentifier, *values: Union[ResourceIdentifier, JsonObject], replace: bool = None):
        """ Specialization for {@link #tag} for item tags. """
        self.tag(name_parts, 'item', *values, replace=replace)

    def block_tag(self, name_parts: ResourceIdentifier, *values: Union[ResourceIdentifier, JsonObject], replace: bool = None):
        """ Specialization for {@link #tag} for block tags. """
        self.tag(name_parts, 'block', *values, replace=replace)

    def block_and_item_tag(self, name_parts: ResourceIdentifier, *values: Union[ResourceIdentifier, JsonObject], replace: bool = None):
        """ Calls both `.block_tag()` and `.item_tag()` with the same arguments. """
        self.tag(name_parts, 'item', *values, replace=replace)
        self.tag(name_parts, 'block', *values, replace=replace)

    def entity_tag(self, name_parts: ResourceIdentifier, *values: Union[ResourceIdentifier, JsonObject], replace: bool = None):
        """ Specialization of {@link #tag} for entity tags. """
        self.tag(name_parts, 'entity_type', *values, replace=replace)

    def fluid_tag(self, name_parts: ResourceIdentifier, *values: Union[ResourceIdentifier, JsonObject], replace: bool = None):
        """ Specialization of {@link #tag} for fluid tags """
        self.tag(name_parts, 'fluid', *values, replace=replace)

    def dimension_tag(self, name_parts: ResourceIdentifier, *values: Union[ResourceIdentifier, JsonObject], replace: bool = None):
        """ Specialization of {@link #tag} for dimension tags """
        self.tag(name_parts, 'dimension', *values, replace=replace)

    def dimension_type_tag(self, name_parts: ResourceIdentifier, *values: Union[ResourceIdentifier, JsonObject], replace: bool = None):
        """ Specialization of {@link #tag} for dimension type tags """
        self.tag(name_parts, 'dimension_type', *values, replace=replace)

    def configured_carver_tag(self, name_parts: ResourceIdentifier, *values: Union[ResourceIdentifier, JsonObject], replace: bool = None):
        """ Specialization of {@link #tag} for configured carver tags """
        self.tag(name_parts, 'worldgen/configured_carver', *values, replace=replace)

    def configured_structure_feature_tag(self, name_parts: ResourceIdentifier, *values: Union[ResourceIdentifier, JsonObject], replace: bool = None):
        """ Specialization of {@link #tag} for configured structure feature tags """
        self.tag(name_parts, 'worldgen/configured_structure_feature', *values, replace=replace)

    def configured_feature_tag(self, name_parts: ResourceIdentifier, *values: Union[ResourceIdentifier, JsonObject], replace: bool = None):
        """ Specialization of {@link #tag} for configured feature tags """
        self.tag(name_parts, 'worldgen/configured_feature', *values, replace=replace)

    def placed_feature_tag(self, name_parts: ResourceIdentifier, *values: Union[ResourceIdentifier, JsonObject], replace: bool = None):
        """ Specialization of {@link #tag} for placed feature tags """
        self.tag(name_parts, 'worldgen/placed_feature', *values, replace=replace)

    def biome_tag(self, name_parts: ResourceIdentifier, *values: Union[ResourceIdentifier, JsonObject], replace: bool = None):
        """ Specialization of {@link #tag} for biome tags """
        self.tag(name_parts, 'worldgen/biome', *values, replace=replace)

    def world_preset_tag(self, name_parts: ResourceIdentifier, *values: Union[ResourceIdentifier, JsonObject], replace: bool = None):
        """ Specialization of {@link #tag} for world preset tags """
        self.tag(name_parts, 'worldgen/world_preset', *values, replace=replace)

    def tag(self, name_parts: ResourceIdentifier, root_domain: ResourceIdentifier, *values: Union[ResourceIdentifier, JsonObject], replace: bool = None):
        """
        Creates or appends to a tag entry
        :param name_parts: The resource location, including path elements.
        :param root_domain: The root domain of the tag. Should be 'blocks', 'items', 'fluids', or 'entity_types', or a world generation folder.
        :param values: The resource location values for the tag. Can specify optional tags by suffixing with `?`, i.e. `'minecraft:foo?'`. Can also accept explicit optional tags via a dictionary with `id` and `required`.
        :param replace: If the tag should replace previous values
        """
        res = utils.resource_location(self.domain, name_parts)
        values = [utils.tag_entry(v, self.domain) for v in values]
        root = '/'.join(utils.str_path(root_domain))
        if res not in self.tags_buffer[root]:
            if replace is None:
                replace = False
            tag = Tag(replace)
            tag.add_all(values)
            self.tags_buffer[root][res] = tag
        else:
            self.tags_buffer[root][res].add_all(values)
            if replace is not None:
                self.tags_buffer[root][res].replace = replace

    def write(self, path_parts: Sequence[str], data: Json):
        """
        Writes data to a file, inserting an autogenerated comment and deletes None entries from the data
        :param path_parts: The path elements of the file
        :param data: The json data to write
        """
        path = os.path.normpath(os.path.join(self.resource_dir, *path_parts)) + '.json'
        data = utils.del_none({'__comment__': 'This file was automatically created by mcresources', **data})
        flag = utils.write(path, data, self.indent, self.ensure_ascii, self.on_error)
        self.written_files.add(path)
        if flag == utils.WriteFlag.NEW:
            self.new_files += 1
        elif flag == utils.WriteFlag.MODIFIED:
            self.modified_files += 1
        elif flag == utils.WriteFlag.UNCHANGED:
            self.unchanged_files += 1
        elif flag == utils.WriteFlag.ERROR:
            self.error_files += 1
