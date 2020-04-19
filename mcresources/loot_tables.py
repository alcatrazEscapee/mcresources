#  Part of mcresources by Alex O'Neill
#  Work under copyright. Licensed under MIT
#  For more information see the project LICENSE file

from typing import Dict, Any


class LootTables:

    @staticmethod
    def set_count(min_count: int = 1, max_count: int = -1, dist_type: str = 'minecraft:uniform') -> Dict[str, Any]:
        """ `minecraft:set_count` function
        :param min_count: the min count for a distribution, or the count if a single value is used
        :param max_count: the max count for a distribution
        :param dist_type: the distribution type
        """
        if max_count == -1:
            count = min_count
        else:
            count = {'min': min_count, 'max': max_count, 'type': dist_type}
        return {
            'function': 'minecraft:set_count',
            'count': count
        }

    @staticmethod
    def fortune_bonus(multiplier: int = 1) -> Dict[str, Any]:
        """ `minecraft:apply_bonus` function with the fortune enchantment, with a uniform bonus count
        :param multiplier: the bonusMultiplier
        """
        return {
            'function': 'minecraft:apply_bonus',
            'enchantment': 'minecraft:fortune',
            'formula': 'minecraft:uniform_bonus_count',
            'parameters': {
                'bonusMultiplier': multiplier
            }
        }
