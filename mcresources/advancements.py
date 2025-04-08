"""
A collection of helper functions for creating common vanilla advancement JSONs.

Usage:
```python
from mcresources import advancements
```
"""

from mcresources.type_definitions import Json, ResourceIdentifier
from mcresources import utils

from typing import Optional


class AdvancementCategory:
    def __init__(self, rm, category: str, background: str):
        self.rm = rm
        self.category = category
        self.background = background

    def advancement(self, name: str, icon: Json, title: str, description: str, parent: Optional[str], criteria: Json, requirements: Json = None, frame: str = 'task', toast: bool = True, chat: bool = True, hidden: bool = False) -> 'AdvancementContext':
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
        return AdvancementContext(self, name, parent)


class AdvancementContext:
    def __init__(self, category: AdvancementCategory, name: str, parent: Optional[str]) -> None:
        self.category = category
        self.name = name
        self.parent = parent
    
    def add_child(self, name: str, icon: Json, title: str, description: str, criteria: Json, requirements: Json = None, frame: str = 'task', toast: bool = True, chat: bool = True, hidden: bool = False) -> 'AdvancementContext':
        return self.category.advancement(name, icon, title, description, self.name, criteria, requirements, frame, toast, chat, hidden)


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

def enter_biome(biome: ResourceIdentifier) -> Json:
    return {
        'trigger': 'minecraft:location',
        'conditions': {
            'biome': utils.resource_location(biome).join()
        }
    }

def first_tick() -> Json:
    """
    Granted when the player begins ticking in the world. Used for 'root' advancements.
    """
    return {'trigger': 'minecraft:tick'}

def consume_item(item: str) -> Json:
    return {
        'trigger': 'minecraft:consume_item',
        'conditions': {
            'item': utils.item_predicate(item)
        }
    }