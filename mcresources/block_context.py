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
        tag_res = utils.resource_location(self.rm.domain, tag_name_parts)
        self.rm.block_tag(tag_res, self.res, replace=replace)
        return self

    def with_lang(self, block_name: str, language: Optional[str] = None) -> 'BlockContext':
        """
        Shortcut for ResourceManager#lang using the block name
        """
        self.rm.lang(('block.%s.%s' % self.res).replace('/', '.'), block_name, language=language)
        return self

    def make_slab(self) -> 'BlockContext':
        """
        Generates all blockstates and models required for a standard slab block
        """
        block = utils.simple_resource_location('%s:block/%s' % self.res)
        block_slab = utils.simple_resource_location('%s:block/%s_slab' % self.res)
        block_slab_top = utils.simple_resource_location('%s:block/%s_slab_top' % self.res)
        self.rm.blockstate('%s:%s_slab' % self.res, variants=utils.slab_variants(block, block_slab, block_slab_top))
        self.rm.block_model('%s:%s_slab' % self.res, {'bottom': block, 'top': block, 'side': block}, parent='block/slab')
        self.rm.block_model('%s:%s_slab_top' % self.res, {'bottom': block, 'top': block, 'side': block}, parent='block/slab_top')
        self.rm.item_model('%s:%s_slab' % self.res, parent=block_slab, no_textures=True)
        return self

    def make_stairs(self) -> 'BlockContext':
        """
        Generates all blockstates and models required for a standard stair block
        """
        block = utils.simple_resource_location('%s:block/%s' % self.res)
        stairs = utils.simple_resource_location('%s:block/%s_stairs' % self.res)
        stairs_inner = utils.simple_resource_location('%s:block/%s_stairs_inner' % self.res)
        stairs_outer = utils.simple_resource_location('%s:block/%s_stairs_outer' % self.res)
        self.rm.blockstate('%s:%s_stairs' % self.res, variants=utils.stairs_variants(stairs, stairs_inner, stairs_outer))
        self.rm.block_model('%s:%s_stairs' % self.res, textures={'bottom': block, 'top': block, 'side': block}, parent='block/stairs')
        self.rm.block_model('%s:%s_stairs_inner' % self.res, textures={'bottom': block, 'top': block, 'side': block}, parent='block/inner_stairs')
        self.rm.block_model('%s:%s_stairs_outer' % self.res, textures={'bottom': block, 'top': block, 'side': block}, parent='block/outer_stairs')
        self.rm.item_model('%s:%s_stairs' % self.res, parent=stairs, no_textures=True)
        return self

    def make_fence(self) -> 'BlockContext':
        """
        Generates all blockstates and models required for a standard (wooden) fence
        """
        block = utils.simple_resource_location('%s:block/%s' % self.res)
        fence_post = utils.simple_resource_location('%s:block/%s_fence_post' % self.res)
        fence_side = utils.simple_resource_location('%s:block/%s_fence_side' % self.res)
        fence_inv = utils.simple_resource_location('%s:block/%s_fence_inventory' % self.res)
        self.rm.blockstate_multipart('%s:%s_fence' % self.res, parts=utils.fence_multipart(fence_post, fence_side))
        self.rm.block_model('%s:%s_fence_post' % self.res, textures={'texture': block}, parent='block/fence_post')
        self.rm.block_model('%s:%s_fence_side' % self.res, textures={'texture': block}, parent='block/fence_side')
        self.rm.block_model('%s:%s_fence_inventory' % self.res, textures={'texture': block}, parent='block/fence_inventory')
        self.rm.item_model('%s:%s_fence' % self.res, parent=fence_inv, no_textures=True)
        return self

    def make_fence_gate(self):
        """
        Generates all blockstates and models required for a standard (wooden) fence gate
        """
        block = utils.simple_resource_location('%s:block/%s' % self.res)
        gate = utils.simple_resource_location('%s:block/%s_fence_gate' % self.res)
        gate_open = utils.simple_resource_location('%s:block/%s_fence_gate_open' % self.res)
        gate_wall = utils.simple_resource_location('%s:block/%s_fence_gate_wall' % self.res)
        gate_wall_open = utils.simple_resource_location('%s:block/%s_fence_gate_wall_open' % self.res)
        self.rm.blockstate('%s:%s_fence_gate' % self.res, variants=utils.fence_gate_variants(gate, gate_open, gate_wall, gate_wall_open))
        self.rm.block_model('%s:%s_fence_gate' % self.res, textures={'texture': block}, parent='block/template_fence_gate')
        self.rm.block_model('%s:%s_fence_gate_open' % self.res, textures={'texture': block}, parent='block/template_fence_gate_open')
        self.rm.block_model('%s:%s_fence_gate_wall' % self.res, textures={'texture': block}, parent='block/template_fence_gate_wall')
        self.rm.block_model('%s:%s_fence_gate_wall_open' % self.res, textures={'texture': block}, parent='block/template_fence_gate_wall_open')
        self.rm.item_model('%s:%s_fence_gate' % self.res, parent=gate, no_textures=True)
        return self

    def make_wall(self):
        """
        Generates all blockstates and models required for a standard (stone) wall
        """
        block = utils.simple_resource_location('%s:block/%s' % self.res)
        wall_post = utils.simple_resource_location('%s:block/%s_wall_post' % self.res)
        wall_side = utils.simple_resource_location('%s:block/%s_wall_side' % self.res)
        wall_inv = utils.simple_resource_location('%s:block/%s_wall_inventory' % self.res)
        self.rm.blockstate_multipart('%s:%s_wall' % self.res, utils.wall_multipart(wall_post, wall_side))
        self.rm.block_model('%s:%s_wall_post' % self.res, textures={'wall': block}, parent='block/template_wall_post')
        self.rm.block_model('%s:%s_wall_side' % self.res, textures={'wall': block}, parent='block/template_wall_side')
        self.rm.block_model('%s:%s_wall_side' % self.res, textures={'wall': block}, parent='block/template_wall_side')
        self.rm.block_model('%s:%s_wall_inventory' % self.res, textures={'wall': block}, parent='block/wall_inventory')
        self.rm.item_model('%s:%s_wall_inventory' % self.res, parent=wall_inv, no_textures=True)

    def make_door(self):
        """
        Generates all blockstates and models required for a standard door
        """
        raise NotImplementedError('todo')

    def make_trapdoor(self):
        """
        Generates all blockstates and models required for a standard trapdoor
        """
        raise NotImplementedError('todo')

    def make_button(self):
        """
        Generates all blockstates and models required for a standard button
        """
        raise NotImplementedError('todo')

    def make_pressure_plate(self):
        """
        Generates all blockstates and models required for a standard pressure plate
        """
        raise NotImplementedError('todo')
