#  Part of mcresources by Alex O'Neill
#  Work under copyright. Licensed under MIT
#  For more information see the project LICENSE file

from typing import Sequence, Dict, Union, Optional

import mcresources.resource_manager as resource_manager
import mcresources.utils as utils


class BlockContext:
    """
    Contextual information about a block, used to simplify similar json calls
    """

    def __init__(self, rm: 'resource_manager.ResourceManager', res: utils.ResourceLocation):
        self.rm: resource_manager.ResourceManager = rm
        self.res: utils.ResourceLocation = res

    def with_blockstate(self, model: str = None, variants: Dict[str, utils.Json] = None, use_default_model: bool = True) -> 'BlockContext':
        """
        Shortcut for ResourceManager#blockstate
        """
        self.rm.blockstate(self.res, model, variants, use_default_model)
        return self

    def with_blockstate_multipart(self, parts: Sequence[utils.Json]) -> 'BlockContext':
        """
        Shortcut for ResourceManager#blockstate_multipart
        """
        self.rm.blockstate_multipart(self.res, parts)
        return self

    def with_block_model(self, textures: Union[Dict[str, str], str] = None, parent: Union[str, None] = 'block/cube_all', elements: utils.Json = None) -> 'BlockContext':
        """
        Shortcut for ResourceManager#block_model
        """
        self.rm.block_model(self.res, textures, parent, elements)
        return self

    def with_block_loot(self, loot_pools: utils.Json) -> 'BlockContext':
        """
        Shortcut for ResourceManager#block_loot
        """
        self.rm.block_loot(self.res, loot_pools)
        return self

    def with_item_model(self) -> 'BlockContext':
        """
        Shortcut for a block item model, which generates a model with a single parent reference to the block model of the same name
        """
        self.rm.item_model(self.res, parent=utils.resource_location(self.rm.domain, 'block/' + self.res.path), no_textures=True)
        return self

    def with_tag(self, tag_name_parts: Sequence[str] = None, replace: bool = None) -> 'BlockContext':
        """
        Shortcut for ResourceManager#block_tag
        """
        if tag_name_parts is None:
            tag_name_parts = self.res
        self.rm.block_tag(tag_name_parts, utils.resource_location(self.res, self.rm.domain), replace=replace)
        return self

    def with_lang(self, block_name: str, language: Optional[str] = None) -> 'BlockContext':
        """
        Shortcut for ResourceManager#lang using the block name
        """
        self.rm.lang(('block.%s.%s' % self.res).replace('/', '.'), block_name, language=language)
        return self
