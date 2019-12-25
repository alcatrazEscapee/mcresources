#  Part of mcresources by Alex O'Neill
#  Work under copyright. Licensed under GPL-3.0
#  For more information see the project LICENSE file

from mcresources.parts import *


class ResourceManager:
    def __init__(self, domain: str = 'minecraft', resource_dir: str = ('src', 'main', 'resources'), indent: int = 2):
        """
        Creates a new Resource Manager. This is the supplier for all resource creation calls.
        :param domain: the domain / mod id for current resources.
        :param indent: the indentation level for all generated json files
        """
        self.resource_dir = str_path(resource_dir)
        self.domain = domain
        self.indent = indent

    def blockstate(self, name_parts: str or list or tuple, model: str = None, variants: dict = None) -> None:
        """
        Creates a blockstate file
        :param name_parts: the resource location, including path elements.
        :param model: the model, used if there are no variants. Defaults to 'domain:block/name/parts'
        :param variants: the variants, as they would be present in json
        """
        if model is None:
            model = '%s:block/%s' % (self.domain, '/'.join(str_list(name_parts)))
        if variants is None:
            variants = {'': {'model': model}}
        write((*self.resource_dir, 'assets', self.domain, 'blockstates', *str_path(name_parts)), {
            'variants': variants
        }, self.indent)

    def block_model(self, name_parts: str or list or tuple, textures: str or dict = None,
                    parent: str = 'block/cube_all') -> None:
        """
        Creates a block model file
        :param name_parts: the resource location, including path elements.
        :param textures: the textures for the model. Defaults to 'domain:block/name/parts'
        :param parent: the parent model.
        """
        if textures is None:
            textures = {'all': '%s:block/%s' % (self.domain, '/'.join(str_path(name_parts)))}
        if type(textures) is str:
            textures = {'all': textures}
        write((*self.resource_dir, 'assets', self.domain, 'models', 'block', *str_path(name_parts)), {
            'parent': parent,
            'textures': textures
        }, self.indent)

    def item_model(self, name_parts: str or list or tuple, *textures: str or dict,
                   parent: str = 'item/generated') -> None:
        """
        Creates an item model file
        :param name_parts: the resource location, including path elements.
        :param textures: the textures for the model. Defaults to 'domain:item/name/parts'
        :param parent: the parent model.
        """
        if textures is None or len(textures) == 0:
            textures = '%s:item/%s' % (self.domain, '/'.join(str_path(name_parts)))
        write((*self.resource_dir, 'assets', self.domain, 'models', 'item', *str_path(name_parts)), {
            'parent': parent,
            'textures': item_model_textures(textures)
        }, self.indent)

    def crafting_shapeless(self, name_parts: str or list or tuple, ingredients: str or dict or list or tuple,
                           result: str or dict, group: str = None, conditions: str or dict or list = None) -> None:
        """
        Creates a shapeless crafting recipe.
        :param name_parts: The resource location, including path elements.
        :param ingredients: The ingredients.
        :param result: The result of crafting the recipe.
        :param group: The group.
        :param conditions: Any conditions for the recipe to be enabled.
        """
        write((*self.resource_dir, 'data', self.domain, 'recipes', *str_path(name_parts)), {
            'type': 'crafting_shapeless',
            'group': group,
            'ingredients': item_stack_list(ingredients),
            'result': item_stack(result),
            'conditions': recipe_condition(conditions)
        }, self.indent)

    def crafting_shaped(self, name_parts: str or list or tuple, pattern: list, ingredients: str or dict,
                        result: str or dict, group: str = None, conditions: str or dict or list = None) -> None:
        """
        Creates a shaped crafting recipe.
        :param name_parts: The resource location, including path elements.
        :param pattern: The pattern for the recipe.
        :param ingredients: The ingredients, indexed by key in pattern.
        :param result: The result of crafting the recipe.
        :param group: The group.
        :param conditions: Any conditions for the recipe to be enabled.
        """
        write((*self.resource_dir, 'data', self.domain, 'recipes', *str_path(name_parts)), {
            'type': 'crafting_shaped',
            'group': group,
            'pattern': pattern,
            'key': item_stack_dict(ingredients, ''.join(pattern)[0]),
            'result': item_stack(result),
            'conditions': recipe_condition(conditions)
        }, self.indent)

    def recipe(self, name_parts: str or list or tuple, type_in: str, data_in: dict, group: str = None,
               conditions: str or dict or list = None) -> None:
        """
        Creates a non-crafting recipe file, used for custom mod recipes using vanilla's data pack system
        :param name_parts: The resource location, including path elements.
        :param type_in: The type of the recipe.
        :param data_in: Data required by the recipe, as present in json
        :param group: The group.
        :param conditions: Any conditions for the recipe to be enabled.
        """
        write((*self.resource_dir, 'data', self.domain, 'recipes', *str_path(name_parts)), {
            'type': type_in,
            'group': group,
            **data_in,
            'conditions': conditions
        }, self.indent)

    def item_tag(self, name_parts: str or list or tuple, *values: str or list or tuple, replace: bool = False) -> None:
        """
        Creates an item tag file.
        :param name_parts: The resource location, including path elements.
        :param values: The resource location values for the tag
        :param replace: If the tag should replace previous values
        """
        write((*self.resource_dir, 'data', self.domain, 'tags', 'items', *str_path(name_parts)), {
            'replace': replace,
            'values': str_list(values)
        }, self.indent)

    def block_tag(self, name_parts: str or list or tuple, *values: str or list, replace: bool = False) -> None:
        """
        Creates a block tag file.
        :param name_parts: The resource location, including path elements.
        :param values: The resource location values for the tag
        :param replace: If the tag should replace previous values
        """
        write((*self.resource_dir, 'data', self.domain, 'tags', 'blocks', *str_path(name_parts)), {
            'replace': replace,
            'values': str_list(values)
        }, self.indent)

    def entity_tag(self, name_parts: str or list or tuple, *values: str or list, replace: bool = False) -> None:
        """
        Creates an entity tag file
        :param name_parts: The resource location, including path elements.
        :param values: The resource location values for the tag
        :param replace: If the tag should replace previous values
        """
        write((*self.resource_dir, 'data', self.domain, 'tags', 'entity_types', *str_path(name_parts)), {
            'replace': replace,
            'values': str_list(values)
        }, self.indent)

    def fluid_tag(self, name_parts: str or list or tuple, *values: str or list, replace: bool = False) -> None:
        """
        Creates an fluid tag file
        :param name_parts: The resource location, including path elements.
        :param values: The resource location values for the tag
        :param replace: If the tag should replace previous values
        """
        write((*self.resource_dir, 'data', self.domain, 'tags', 'fluids', *str_path(name_parts)), {
            'replace': replace,
            'values': str_list(values)
        }, self.indent)

    def block_loot(self, name_parts: str or list or tuple, loot_pools: list or tuple or dict or str) -> None:
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
        name = str_path(name_parts)
        write((*self.resource_dir, 'data', self.domain, 'loot_tables', 'blocks', *name), {
            'type': 'minecraft:block',
            'pools': loot_pool_list(loot_pools, 'block')
        })