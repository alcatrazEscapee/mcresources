#  Part of mcresources by Alex O'Neill
#  Work under copyright. Licensed under MIT
#  For more information see the project LICENSE file

from type_definitions import Json, ResourceLocation

import utils


class RecipeContext:
    """
    Contextual information about a recipe, used to simplify similar json calls
    """

    def __init__(self, rm, res: ResourceLocation):
        self.rm = rm
        self.res: ResourceLocation = res

    def with_advancement(self, unlock_item: Json, parent: str = 'minecraft:recipes/root') -> 'RecipeContext':
        """
        Shortcut to ResourceManager#advancement, with a standard recipe advancement
        :param unlock_item: The item required to unlock the recipe. Uses the 'minecraft:inventory_changed' trigger
        :param parent: the parent advancement
        """
        recipe_name = self.res.join()
        self.rm.advancement(self.res, parent=parent, criteria={
            'has_item': {
                'trigger': 'minecraft:inventory_changed',
                'conditions': {'items': [utils.item_stack(unlock_item)]}
            },
            'has_the_recipe': {
                'trigger': 'minecraft:recipe_unlocked',
                'conditions': {'recipe': recipe_name}
            }
        }, requirements=[['has_item', 'has_the_recipe']], rewards={'recipes': [recipe_name]})
        return self
