#  Part of mcresources by Alex O'Neill
#  Work under copyright. Licensed under MIT
#  For more information see the project LICENSE file

from typing import Sequence, Dict, Union

import mcresources.resource_manager as resource_manager
import mcresources.utils as utils


class BlockContext:
    """
    Contextual information about a block, used to simplify similar json calls
    """

    def __init__(self, rm: 'resource_manager.ResourceManager', name_parts: Sequence[str]):
        self.rm = rm
        self.name_parts = name_parts

    def with_blockstate(self, model: str = None, variants: Dict[str, utils.Json] = None, use_default_model: bool = True) -> 'BlockContext':
        """
        Shortcut for ResourceManager#blockstate
        """
        self.rm.blockstate(self.name_parts, model, variants, use_default_model)
        return self

    def with_blockstate_multipart(self, parts: Sequence[utils.Json]) -> 'BlockContext':
        """
        Shortcut for ResourceManager#blockstate_multipart
        """
        self.rm.blockstate_multipart(self.name_parts, parts)
        return self

    def with_block_model(self, textures: Union[Dict[str, str], str] = None, parent: Union[str, None] = 'block/cube_all', elements: utils.Json = None) -> 'BlockContext':
        """
        Shortcut for ResourceManager#block_model
        """
        self.rm.block_model(textures, parent, elements)
        return self

    def with_block_loot(self, loot_pools: utils.Json) -> 'BlockContext':
        """
        Shortcut for ResourceManager#block_loot
        """
        self.rm.block_loot(self.name_parts, loot_pools)
        return self

    def with_item_model(self) -> 'BlockContext':
        """
        Shortcut for a block item model, which generates a model with a single parent reference to the block model of the same name
        """
        self.rm.item_model(self.name_parts, parent=utils.resource_location(self.rm.domain, ('block', *utils.str_path(self.name_parts))), no_textures=True)
        return self

    def with_tag(self, replace: bool = None) -> 'BlockContext':
        """
        Shortcut for ResourceManager#block_tag
        """
        self.rm.block_tag(self.name_parts, utils.resource_location(self.rm.domain, self.name_parts), replace=replace)
        return self
