#  Part of mcresources by Alex O'Neill
#  Work under copyright. Licensed under MIT
#  For more information see the project LICENSE file

from typing import Sequence

import mcresources.resource_manager as resource_manager
import mcresources.utils as utils


class ItemContext:
    """
    Contextual information about an item, used to simplify similar json calls
    """

    def __init__(self, rm: 'resource_manager.ResourceManager', name_parts: Sequence[str]):
        self.name_parts: Sequence[str] = name_parts
        self.rm: resource_manager.ResourceManager = rm

    def with_tag(self, replace: bool = None) -> 'ItemContext':
        """
        Shortcut for ResourceManager#item_tag
        """
        self.rm.item_tag(self.name_parts, utils.resource_location(self.rm.domain, self.name_parts), replace=replace)
        return self
