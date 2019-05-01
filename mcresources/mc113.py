#  Part of mcresources by Alex O'Neill
#  Work under copyright. Licensed under GPL-3.0
#  For more information see the project LICENSE file

import json
import os


class ResourceManager:
    def __init__(self, domain: str = 'minecraft', indent: int = 2):
        """
        Creates a new Resource Manager. This is the supplier for all resource creation calls.
        :param domain: the domain / mod id for current resources.
        :param indent: the indentation level for all generated json files
        """
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
        write(('assets', self.domain, 'blockstates', *str_list(name_parts)), {
            'variants': variants
        }, self.indent)

    def block_model(self, name_parts: str or list or tuple, textures: str or dict = None,
                    parent: str = 'cube_all') -> None:
        """
        Creates a block model file
        :param name_parts: the resource location, including path elements.
        :param textures: the textures for the model. Defaults to 'domain:block/name/parts'
        :param parent: the parent model.
        """
        if textures is None:
            textures = {'texture': '%s:block/%s' % (self.domain, '/'.join(str_list(name_parts)))}
        if type(textures) is str:
            textures = {'texture': textures}
        write(('assets', self.domain, 'models', 'block', *str_list(name_parts)), {
            'parent': parent,
            'textures': textures
        }, self.indent)

    def item_model(self, name_parts: str or list or tuple, *textures: str or dict, parent: str = 'item/generated'):
        """
        Creates an item model file
        :param name_parts: the resource location, including path elements.
        :param textures: the textures for the model. Defaults to 'domain:item/name/parts'
        :param parent: the parent model.
        :return:
        """
        if textures is None or len(textures) == 0:
            textures = '%s:item/%s' % (self.domain, '/'.join(str_list(name_parts)))
        write(('assets', self.domain, 'models', 'item', *str_list(name_parts)), {
            'parent': parent,
            'textures': item_model_textures(textures)
        }, self.indent)

    def crafting_shapeless(self, name_parts: str or list or tuple, ingredients: str or dict or list or tuple,
                           result: str or dict, group: str = None, conditions: str or dict or list = None):
        """
        Creates a shapeless crafting recipe.
        :param name_parts: The resource location, including path elements.
        :param ingredients: The ingredients.
        :param result: The result of crafting the recipe.
        :param group: The group.
        :param conditions: Any conditions for the recipe to be enabled.
        :return:
        """
        write(('data', self.domain, 'recipes', *str_list(name_parts)), {
            'type': 'crafting_shapeless',
            'group': group,
            'ingredients': item_stack_list(ingredients),
            'result': item_stack(result),
            'conditions': recipe_condition(conditions)
        }, self.indent)

    def crafting_shaped(self, name_parts: str or list or tuple, pattern: list, ingredients: str or dict, result,
                        group: str = None, conditions: str or dict or list = None) -> None:
        """
        Creates a shaped crafting recipe.
        :param name_parts: The resource location, including path elements.
        :param pattern: The pattern for the recipe.
        :param ingredients: The ingredients, indexed by key in pattern.
        :param result: The result of crafting the recipe.
        :param group: The group.
        :param conditions: Any conditions for the recipe to be enabled.
        """
        write(('data', self.domain, 'recipes', *str_list(name_parts)), {
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
        write(('data', self.domain, 'recipes', *str_list(name_parts)), {
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
        write(('data', self.domain, 'tags', 'items', *str_list(name_parts)), {
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
        write(('data', self.domain, 'tags', 'blocks', *str_list(name_parts)), {
            'replace': replace,
            'values': str_list(values)
        }, self.indent)


def clean_generated_resources(path='src/main/resources') -> None:
    """
    Recursively removes all files generated using mc_1_13.py, as identified by the inserted comment. Removes empty directories
    :param path: the initial path to search through
    """
    for subdir in os.listdir(path):
        sub_path = os.path.join(path, subdir)
        if os.path.isfile(sub_path):
            # File, check if valid and then delete
            if subdir.endswith('.json'):
                delete = False
                with open(sub_path, 'r') as file:
                    if '"__comment__": "This file was automatically created by mc_1_13.py"' in file.read():
                        delete = True
                if delete:
                    os.remove(sub_path)
        else:
            # Folder, search recursively
            clean_generated_resources(sub_path)

        if not os.listdir(path):
            # Delete empty folder
            os.rmdir(path)


def del_none(d: dict) -> dict:
    for key, value in list(d.items()):
        if value is None:
            del d[key]
        elif isinstance(value, dict):
            del_none(value)
    return d


def write(path_parts: tuple, data: dict, indent: int = 2) -> None:
    path = os.path.join('src', 'main', 'resources', *path_parts) + '.json'
    os.makedirs(os.path.dirname(path), exist_ok=True)
    data = del_none({'__comment__': 'This file was automatically created by mcresources', **data})
    with open(path, 'w') as file:
        json.dump(data, file, indent=indent)


def recipe_condition(data_in: str or dict or list or tuple, strict: bool = False) -> list or None:
    if data_in is None:
        return data_in
    elif type(data_in) is str:
        return [{'type': data_in}]
    elif type(data_in) is dict:
        return [data_in]
    elif type(data_in) in [list, tuple] and not strict:
        return [recipe_condition(c, True) for c in data_in]
    else:
        raise RuntimeError('Unable to parse recipe condition: ' + str(data_in))


def item_stack(data_in: str or dict) -> dict:
    if type(data_in) is str:
        if data_in[0:4] == 'tag!':
            return {'tag': data_in[4:]}
        else:
            return {'item': data_in}
    if type(data_in) is dict:
        return data_in
    else:
        raise RuntimeError('Unable to parse item stack: ' + str(data_in))


def item_stack_list(data_in: str or dict or list or tuple) -> list:
    if type(data_in) in [list, tuple]:
        return [item_stack(s) for s in data_in]
    else:
        return [item_stack(data_in)]


def item_stack_dict(data_in: str or dict, default_char: str = '#') -> dict:
    if type(data_in) is dict:
        return dict((k, item_stack(v)) for k, v in data_in.items())
    else:
        return {default_char: item_stack(data_in)}


def str_list(data_in: str or list or tuple) -> list:
    if type(data_in) is str:
        return [data_in]
    elif type(data_in) in [list, tuple]:
        return [*data_in]
    else:
        raise RuntimeError('Unable to parse string list: ' + str(data_in))


def item_model_textures(data_in: str or dict or list or tuple) -> dict:
    if type(data_in) is str:
        return {'layer0': data_in}
    elif type(data_in) in [list, tuple]:
        return dict(('layer%d' % i, data_in[i]) for i in range(len(data_in)))
    elif type(data_in) is dict:
        return data_in
    else:
        raise RuntimeError('Unable to parse item model textures: ' + str(data_in))
