#  Part of mcresources by Alex O'Neill
#  Work under copyright. Licensed under MIT
#  For more information see the project LICENSE file

from typing import List

import mcresources.utils as utils


class Tag:
    """
    Wrapper around a tag entry
    """

    def __init__(self, replace: bool):
        self.replace: bool = replace
        self.values: List[utils.ResourceLocation] = []

    def add_all(self, values: List[utils.ResourceLocation]):
        """ Adds a list of new tag entries, but ignoring duplicates while preserving insertion order. Sadly, this means it's slower """
        for v in values:
            if v not in self.values:
                self.values.append(v)
