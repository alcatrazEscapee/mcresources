#  Part of mcresources by Alex O'Neill
#  Work under copyright. Licensed under MIT
#  For more information see the project LICENSE file

from collections import defaultdict
from typing import Sequence, Dict, Union, Any

import mcresources.utils as utils
from mcresources.block_context import BlockContext
from mcresources.item_context import ItemContext
from mcresources.recipe_context import RecipeContext
from mcresources.tag import Tag


class ResourceManager:
    def __init__(self, domain: str = 'minecraft', resource_dir: Sequence[str] = ('src', 'main', 'resources'), indent: int = 2, default_language: str = 'en_us'):
        """
        Creates a new Resource Manager. This is the supplier for all resource creation calls.
        :param domain: the domain / mod id for current resources.
        :param indent: the indentation level for all generated json files
        """
        self.resource_dir = utils.str_path(resource_dir)
        self.domain = domain
        self.indent = indent
        self.default_language = default_language

        # Internal buffers, used for tags and lang entries, which are all written at the same time
        self.lang_buffer: Dict[str, Dict[str, str]] = defaultdict(dict)  # Keys are (language, translation key)
        self.tags_buffer: Dict[str, Dict[utils.ResourceLocation, Tag]] = defaultdict(dict)  # Keys are (tag type, tag name)

    def flush(self):
        """
        Flushes all buffered tags and lang files
        """
        for language, contents in self.lang_buffer.items():
            utils.write((*self.resource_dir, 'assets', self.domain, 'lang', language), contents, self.indent)

        for tag_type, tags in self.tags_buffer.items():
            for tag_res, tag in tags.items():
                utils.write((*self.resource_dir, 'data', tag_res.domain, 'tags', tag_type, tag_res.path), {
                    'replace': tag.replace,
                    'values': [utils.simple_resource_location(v, True) for v in tag.values]
                }, self.indent)

        self.lang_buffer.clear()
        self.tags_buffer.clear()

    def block(self, name_parts: utils.ResourceIdentifier) -> BlockContext:
        return BlockContext(self, utils.resource_location(self.domain, name_parts))

    def item(self, name_parts: utils.ResourceIdentifier) -> ItemContext:
        return ItemContext(self, utils.resource_location(self.domain, name_parts))

    def blockstate(self, name_parts: utils.ResourceIdentifier, model: str = None, variants: Dict[str, utils.Json] = None, use_default_model: bool = True) -> BlockContext:
        """
        Creates a blockstate file
        :param name_parts: the resource location, including path elements.
        :param model: the model, used if there are no variants. Defaults to 'domain:block/name/parts'
        :param variants: the variants, as they would be present in json
        :param use_default_model: if a model is missing for a variant, should this populate the variant using the assumed model
        """
        res = utils.resource_location(self.domain, name_parts)
        if model is None:
            model = '%s:block/%s' % res
        if variants is None:
            variants = {'': {'model': model}}
        if use_default_model:
            for key, prop in variants.items():
                if 'model' not in prop:
                    prop['model'] = model
        utils.write((*self.resource_dir, 'assets', res.domain, 'blockstates', res.path), {
            'variants': variants
        }, self.indent)
        return BlockContext(self, res)

    def blockstate_multipart(self, name_parts: utils.ResourceIdentifier, parts: Sequence[utils.Json]) -> BlockContext:
        """
        Creates a blockstate file, using the multipart model syntax
        :param name_parts: the resource location, including path elements.
        :param parts: The parts. Each element can be a 2-element sequence of a 'when' and 'apply' json, or a single 'apply' json.
        """
        res = utils.resource_location(self.domain, name_parts)
        utils.write((*self.resource_dir, 'assets', res.domain, 'blockstates', res.path), {
            'multipart': utils.blockstate_multipart_parts(parts)
        }, self.indent)
        return BlockContext(self, res)

    def block_model(self, name_parts: utils.ResourceIdentifier, textures: Union[Dict[str, str], Sequence[str]] = None, parent: Union[str, None] = 'block/cube_all', elements: utils.Json = None) -> BlockContext:
        """
        Creates a block model file
        :param name_parts: the resource location, including path elements.
        :param textures: the textures for the model. Defaults to 'domain:block/name/parts'
        :param parent: the parent model. If none, it is omitted
        :param elements: elements of the model. Can be a single element, which will get expanded to a list of one element
        """
        res = utils.resource_location(self.domain, name_parts)
        if textures is None:
            textures = {'all': '%s:block/%s' % res}
        elif isinstance(textures, str):
            textures = {'all': textures}
        elif isinstance(textures, Sequence):
            textures = dict((k, '%s:block/%s' % res) for k in textures)
        if isinstance(elements, Dict):
            elements = [elements]
        utils.write((*self.resource_dir, 'assets', res.domain, 'models', 'block', res.path), {
            'parent': parent,
            'textures': textures,
            'elements': elements
        }, self.indent)
        return BlockContext(self, res)

    def item_model(self, name_parts: utils.ResourceIdentifier, *textures: Union[utils.Json, str], parent: utils.ResourceIdentifier = 'item/generated', no_textures: bool = False) -> ItemContext:
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
                textures = '%s:item/%s' % res
            textures = utils.item_model_textures(textures)
        utils.write((*self.resource_dir, 'assets', res.domain, 'models', 'item', res.path), {
            'parent': utils.simple_resource_location(parent),
            'textures': textures
        }, self.indent)
        return ItemContext(self, res)

    def crafting_shapeless(self, name_parts: utils.ResourceIdentifier, ingredients: utils.Json, result: utils.Json, group: str = None, conditions: utils.Json = None) -> RecipeContext:
        """
        Creates a shapeless crafting recipe.
        :param name_parts: The resource location, including path elements.
        :param ingredients: The ingredients.
        :param result: The result of crafting the recipe.
        :param group: The group.
        :param conditions: Any conditions for the recipe to be enabled.
        """
        res = utils.resource_location(self.domain, name_parts)
        utils.write((*self.resource_dir, 'data', res.domain, 'recipes', res.path), {
            'type': 'minecraft:crafting_shapeless',
            'group': group,
            'ingredients': utils.item_stack_list(ingredients),
            'result': utils.item_stack(result),
            'conditions': utils.recipe_condition(conditions)
        }, self.indent)
        return RecipeContext(self, res)

    def crafting_shaped(self, name_parts: utils.ResourceIdentifier, pattern: Sequence[str], ingredients: utils.Json, result: utils.Json, group: str = None, conditions: utils.Json = None) -> RecipeContext:
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
        utils.write((*self.resource_dir, 'data', res.domain, 'recipes', res.path), {
            'type': 'minecraft:crafting_shaped',
            'group': group,
            'pattern': pattern,
            'key': utils.item_stack_dict(ingredients, ''.join(pattern)[0]),
            'result': utils.item_stack(result),
            'conditions': utils.recipe_condition(conditions)
        }, self.indent)
        return RecipeContext(self, res)

    def recipe(self, name_parts: utils.ResourceIdentifier, type_in: str, data_in: Dict[str, Any], group: str = None, conditions: utils.Json = None) -> RecipeContext:
        """
        Creates a non-crafting recipe file, used for custom mod recipes using vanilla's data pack system
        :param name_parts: The resource location, including path elements.
        :param type_in: The type of the recipe.
        :param data_in: Data required by the recipe, as present in json
        :param group: The group.
        :param conditions: Any conditions for the recipe to be enabled.
        """
        res = utils.resource_location(self.domain, name_parts)
        utils.write((*self.resource_dir, 'data', res.domain, 'recipes', res.path), {
            'type': type_in,
            'group': group,
            **data_in,
            'conditions': utils.recipe_condition(conditions)
        }, self.indent)
        return RecipeContext(self, res)

    def data(self, name_parts: utils.ResourceIdentifier, data_in: Dict[str, Any], root_domain: str = 'data'):
        """
        Creates a generic data file. Used for anything and everything under the sun.
        :param name_parts: The resource location, including path elements.
        :param data_in: Data to be inserted into the json
        :param root_domain: The root location (either data or assets) to insert into
        """
        res = utils.resource_location(self.domain, name_parts)
        utils.write((*self.resource_dir, root_domain, res.domain, res.path), data_in, self.indent)

    def advancement(self, name_parts: utils.ResourceIdentifier, display: utils.Json = None, parent: str = None, criteria: Dict[str, Dict[str, utils.Json]] = None, requirements: Sequence[Sequence[str]] = None, rewards: Dict[str, utils.Json] = None):
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
        utils.write((*self.resource_dir, 'data', res.domain, 'advancements', res.path), {
            'parent': parent,
            'criteria': criteria,
            'display': display,
            'requirements': requirements,
            'rewards': rewards
        }, self.indent)

    def tag(self, name_parts: utils.ResourceIdentifier, root_domain: str, *values: utils.ResourceIdentifier, replace: bool = None):
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
            self.tags_buffer[root_domain][res] = Tag(replace, values)
        else:
            self.tags_buffer[root_domain][res].values += values
            if replace is not None:
                self.tags_buffer[root_domain][res].replace = replace

    def item_tag(self, name_parts: utils.ResourceIdentifier, *values: utils.ResourceIdentifier, replace: bool = None):
        self.tag(name_parts, 'items', *values, replace=replace)

    def block_tag(self, name_parts: utils.ResourceIdentifier, *values: utils.ResourceIdentifier, replace: bool = None):
        self.tag(name_parts, 'blocks', *values, replace=replace)

    def entity_tag(self, name_parts: utils.ResourceIdentifier, *values: utils.ResourceIdentifier, replace: bool = None):
        self.tag(name_parts, 'entity_types', *values, replace=replace)

    def fluid_tag(self, name_parts: utils.ResourceIdentifier, *values: utils.ResourceIdentifier, replace: bool = None):
        self.tag(name_parts, 'fluids', *values, replace=replace)

    def block_loot(self, name_parts: utils.ResourceIdentifier, loot_pools: utils.Json):
        """
        Creates a loot table for a block
        If loot_pools is passed in as a list or tuple, it will attempt to create a pool for each entry in the tuple
        It can also be passed in as a string or dict, in which case it will create one pool from that input
        The simplest loot pool is a string, i.e. 'minecraft:dirt', which will create a pool with one entry of type item
        with the value of 'minecraft:dirt', with one roll, and the default condition ('minecraft:survives_explosion')
        If a loot pool is a dict, it will look for each possible element of a pool entry, and try to populate them
        accordingly.
        'entries' can be a dict or a string. A string will expand to 'type': 'minecraft:item'
        'conditions' can be a list, tuple, dict, or string. A string will expand to {'condition': value}
        A dict will be inserted as raw json.
        'functions' can be a list, tuple, dict, or string. A string will expand to {'function': value}
        A dict will be inserted as raw json.
        'rolls' will be inserted as raw json. If not present, it will default to 'rolls': 1
        'children', 'name', 'bonus_rolls', 'weight', and 'quality' will be inserted as raw json if present
        :param name_parts: The resource location, including path elements.
        :param loot_pools: The loot table elements
        """
        res = utils.resource_location(self.domain, name_parts)
        utils.write((*self.resource_dir, 'data', res.domain, 'loot_tables', 'blocks', res.path), {
            'type': 'minecraft:block',
            'pools': utils.loot_pool_list(loot_pools, 'block')
        })

    def lang(self, *args: Union[str, Sequence[str], Dict[str, str]], language: str = None):
        """
        :param args: The lang entries. Can be paired key, value strings, or a dictionary of key -> value maps
        :param language: The language key. Defaults to the default language supplied in the resource manager constructor
        """
        if language is None:
            language = self.default_language
        for key, val in utils.lang_parts(args).items():
            self.lang_buffer[language][key] = val
