#  Part of mcresources by Alex O'Neill
#  Work under copyright. Licensed under MIT
#  For more information see the project LICENSE file

from typing import Sequence

import mcresources.resource_manager as resource_manager
import mcresources.utils as utils


class RecipeContext:
    """
    Contextual information about a recipe, used to simplify similar json calls
    """

    def __init__(self, rm: 'resource_manager.ResourceManager', recipe_name_parts: Sequence[str]):
        self.recipe_name_parts = recipe_name_parts
        self.rm = rm

    def with_advancement(self, unlock_item: utils.Json, parent: str = 'minecraft:recipes/root') -> 'RecipeContext':
        """
        Shortcut to ResourceManager#advancement, with a standard recipe advancement
        :param unlock_item: The item required to unlock the recipe. Uses the 'minecraft:inventory_changed' trigger
        :param parent: the parent advancement
        """
        recipe_name = utils.resource_location(self.rm.domain, self.recipe_name_parts)
        self.rm.advancement(self.recipe_name_parts, parent=parent, criteria={
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
