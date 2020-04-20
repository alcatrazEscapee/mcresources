#  Part of mcresources by Alex O'Neill
#  Work under copyright. Licensed under MIT
#  For more information see the project LICENSE file

from typing import Sequence, Union

import mcresources.resource_manager as resource_manager
import mcresources.utils as utils


class ItemContext:
    """
    Contextual information about an item, used to simplify similar json calls
    """

    def __init__(self, rm: 'resource_manager.ResourceManager', name_parts: Sequence[str]):
        self.name_parts: Sequence[str] = name_parts
        self.rm: resource_manager.ResourceManager = rm

    def with_item_model(self, *textures: Union[utils.Json, str], parent: str = 'item/generated', no_textures: bool = False) -> 'ItemContext':
        """
        Shortcut for ResourceManager#item_model
        """
        self.rm.item_model(self.name_parts, *textures, parent=parent, no_textures=no_textures)
        return self

    def with_tag(self, tag_name_parts: Sequence[str] = None, replace: bool = None) -> 'ItemContext':
        """
        Shortcut for ResourceManager#item_tag
        """
        if tag_name_parts is None:
            tag_name_parts = self.name_parts
        self.rm.item_tag(tag_name_parts, utils.resource_location(self.rm.domain, self.name_parts), replace=replace)
        return self
