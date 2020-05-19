#  Part of mcresources by Alex O'Neill
#  Work under copyright. Licensed under MIT
#  For more information see the project LICENSE file

from typing import List

import mcresources.utils as utils


class Tag:
    """
    Wrapper around a tag entry
    """

    def __init__(self, replace: bool, values: List[utils.ResourceLocation]):
        self.replace: bool = replace
        self.values: List[utils.ResourceLocation] = values
