from typing import Optional
from type_definitions import Json, ResourceIdentifier

import utils

class AdvancementCategory:
    def __init__(self, rm, category: str, background: str):
        self.rm = rm
        self.category = category
        self.background = background

    def advancement(self, name: str, icon: Json, title: str, description: str, parent: Optional[str], criteria: Json, requirements: Json = None, frame: str = 'task', toast: bool = True, chat: bool = True, hidden: bool = False):
        key = '%s.advancements.%s.%s' % (self.rm.domain, self.category, name)

        if parent is not None:
            parent = utils.resource_location(self.rm.domain, self.category + '/' + parent).join()

        self.rm.advancement((self.category, name), {
            'icon': utils.item_stack(icon),
            'title': {'translate': key + '.title'},
            'description': {'translate': key + '.description'},
            'frame': frame,
            'show_toast': toast,
            'announce_to_chat': chat,
            'hidden': hidden,
            'background': self.background
        }, parent, criteria, requirements)
        self.rm.lang(key + '.title', title)
        self.rm.lang(key + '.description', description)


def inventory_changed(*item_predicates: Json) -> Json:
    return {
        'trigger': 'minecraft:inventory_changed',
        'conditions': {
            'items': [utils.item_predicate(ip) for ip in item_predicates]
        }
    }

def recipe_unlocked(recipe: ResourceIdentifier) -> Json:
    return {
        'trigger': 'minecraft:recipe_unlocked',
        'conditions': {
            'recipe': utils.resource_location(recipe).join()
        }
    }
