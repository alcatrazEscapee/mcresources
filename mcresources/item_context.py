#  Part of mcresources by Alex O'Neill
#  Work under copyright. Licensed under MIT
#  For more information see the project LICENSE file

from typing import Sequence, Union, Optional

import mcresources.resource_manager as resource_manager
import mcresources.utils as utils


class ItemContext:
    """
    Contextual information about an item, used to simplify similar json calls
    """

    def __init__(self, rm: 'resource_manager.ResourceManager', res: utils.ResourceLocation):
        self.rm: resource_manager.ResourceManager = rm
        self.res: utils.ResourceLocation = res

    def with_item_model(self, *textures: Union[utils.Json, str], parent: str = 'item/generated', no_textures: bool = False) -> 'ItemContext':
        """
        Shortcut for ResourceManager#item_model
        """
        self.rm.item_model(self.res, *textures, parent=parent, no_textures=no_textures)
        return self

    def with_tag(self, tag_name_parts: Sequence[str] = None, replace: bool = None) -> 'ItemContext':
        """
        Shortcut for ResourceManager#item_tag
        """
        if tag_name_parts is None:
            tag_name_parts = self.res
        tag_res = utils.resource_location(self.rm.domain, tag_name_parts)
        self.rm.item_tag(tag_res, self.res, replace=replace)
        return self

    def with_lang(self, item_name: str, language: Optional[str] = None) -> 'ItemContext':
        """
        Shortcut for ResourceManager#lang with the item name
        """
        self.rm.lang(('item.%s.%s' % self.res).replace('/', '.'), item_name, language=language)
        return self
