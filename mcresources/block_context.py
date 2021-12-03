#  Part of mcresources by Alex O'Neill
#  Work under copyright. Licensed under MIT
#  For more information see the project LICENSE file

from mcresources.type_definitions import Json, JsonObject, ResourceLocation
from mcresources import utils, block_states

from typing import Optional, Union, Dict, Sequence


class BlockContext:
    """
    Contextual information about a block, used to simplify similar json calls
    """

    def __init__(self, rm, res: ResourceLocation):
        self.rm = rm
        self.res: ResourceLocation = res

    def with_blockstate(self, model: str = None, variants: JsonObject = None, use_default_model: bool = True) -> 'BlockContext':
        """
        Shortcut for ResourceManager#blockstate
        """
        self.rm.blockstate(self.res, model, variants, use_default_model)
        return self

    def with_blockstate_multipart(self, *parts: Json) -> 'BlockContext':
        """
        Shortcut for ResourceManager#blockstate_multipart
        """
        self.rm.blockstate_multipart(self.res, *parts)
        return self

    def with_block_model(self, textures: Union[Dict[str, str], str] = None, parent: Optional[str] = 'block/cube_all', elements: Json = None) -> 'BlockContext':
        """
        Shortcut for ResourceManager#block_model
        """
        self.rm.block_model(self.res, textures, parent, elements)
        return self

    def with_block_loot(self, *loot_pools: Json) -> 'BlockContext':
        """
        Shortcut for ResourceManager#block_loot
        """
        self.rm.block_loot(self.res, *loot_pools)
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

    def make_slab(self, slab_suffix: str = '_slab', bottom_texture: Optional[str] = None, side_texture: Optional[str] = None, top_texture: Optional[str] = None) -> 'BlockContext':
        """
        Generates all blockstates and models required for a standard slab block
        """
        block = '%s:block/%s' % self.res
        slab = self.res.join() + slab_suffix
        block_slab = block + slab_suffix
        block_slab_top = block + slab_suffix + '_top'

        if bottom_texture is None:
            bottom_texture = block
        if side_texture is None:
            side_texture = block
        if top_texture is None:
            top_texture = block

        self.rm.blockstate(slab, variants=block_states.slab_variants(block, block_slab, block_slab_top))
        self.rm.block_model(slab, {'bottom': bottom_texture, 'top': top_texture, 'side': side_texture}, parent='block/slab')
        self.rm.block_model(slab + '_top', {'bottom': bottom_texture, 'top': top_texture, 'side': side_texture}, parent='block/slab_top')
        self.rm.item_model(slab, parent=block_slab, no_textures=True)
        return self

    def make_stairs(self, stair_suffix: str = '_stairs', bottom_texture: Optional[str] = None, side_texture: Optional[str] = None, top_texture: Optional[str] = None) -> 'BlockContext':
        """
        Generates all blockstates and models required for a standard stair block
        """
        block = self.res.join('block/')
        stairs = self.res.join() + stair_suffix
        block_stairs = block + stair_suffix
        block_stairs_inner = block + stair_suffix + '_inner'
        block_stairs_outer = block + stair_suffix + '_outer'

        if bottom_texture is None:
            bottom_texture = block
        if side_texture is None:
            side_texture = block
        if top_texture is None:
            top_texture = block

        self.rm.blockstate(stairs, variants=block_states.stairs_variants(block_stairs, block_stairs_inner, block_stairs_outer))
        self.rm.block_model(stairs, textures={'bottom': bottom_texture, 'top': top_texture, 'side': side_texture}, parent='block/stairs')
        self.rm.block_model(stairs + '_inner', textures={'bottom': bottom_texture, 'top': top_texture, 'side': side_texture}, parent='block/inner_stairs')
        self.rm.block_model(stairs + '_outer', textures={'bottom': bottom_texture, 'top': top_texture, 'side': side_texture}, parent='block/outer_stairs')
        self.rm.item_model(stairs, parent=block_stairs, no_textures=True)
        return self

    def make_fence(self, fence_suffix: str = '_fence', texture: Optional[str] = None) -> 'BlockContext':
        """
        Generates all blockstates and models required for a standard (wooden) fence
        """
        block = self.res.join('block/')
        fence = self.res.join() + fence_suffix
        fence_post = block + fence_suffix + '_post'
        fence_side = block + fence_suffix + '_side'
        fence_inv = block + fence_suffix + '_inventory'

        if texture is None:
            texture = block

        self.rm.blockstate_multipart(fence, *block_states.fence_multipart(fence_post, fence_side))
        self.rm.block_model(fence + '_post', textures={'texture': texture}, parent='block/fence_post')
        self.rm.block_model(fence + '_side', textures={'texture': texture}, parent='block/fence_side')
        self.rm.block_model(fence + '_inventory', textures={'texture': texture}, parent='block/fence_inventory')
        self.rm.item_model(fence, parent=fence_inv, no_textures=True)
        return self

    def make_fence_gate(self, gate_suffix: str = '_fence_gate', texture: Optional[str] = None) -> 'BlockContext':
        """
        Generates all blockstates and models required for a standard (wooden) fence gate
        """
        block = self.res.join('block/')
        gate = self.res.join() + gate_suffix
        block_gate = block + gate_suffix
        block_gate_open = block + gate_suffix + '_open'
        block_gate_wall = block + gate_suffix + '_wall'
        block_gate_wall_open = block + gate_suffix + '_wall_open'

        if texture is None:
            texture = block

        self.rm.blockstate(gate, variants=block_states.fence_gate_variants(block_gate, block_gate_open, block_gate_wall, block_gate_wall_open))
        self.rm.block_model(gate, textures={'texture': texture}, parent='block/template_fence_gate')
        self.rm.block_model(gate + '_open', textures={'texture': texture}, parent='block/template_fence_gate_open')
        self.rm.block_model(gate + '_wall', textures={'texture': texture}, parent='block/template_fence_gate_wall')
        self.rm.block_model(gate + '_wall_open', textures={'texture': texture}, parent='block/template_fence_gate_wall_open')
        self.rm.item_model(gate, parent=block_gate, no_textures=True)
        return self

    def make_wall(self, wall_suffix: str = '_wall', texture: Optional[str] = None) -> 'BlockContext':
        """
        Generates all blockstates and models required for a standard (stone) wall
        """
        block = self.res.join('block/')
        wall = self.res.join() + wall_suffix
        wall_post = block + wall_suffix + '_post'
        wall_side = block + wall_suffix + '_side'
        wall_side_tall = block + wall_suffix + '_side_tall'
        wall_inv = block + wall_suffix + '_inventory'

        if texture is None:
            texture = block

        self.rm.blockstate_multipart(wall, *block_states.wall_multipart(wall_post, wall_side, wall_side_tall))
        self.rm.block_model(wall + '_post', textures={'wall': texture}, parent='block/template_wall_post')
        self.rm.block_model(wall + '_side', textures={'wall': texture}, parent='block/template_wall_side')
        self.rm.block_model(wall + '_side_tall', textures={'wall': texture}, parent='block/template_wall_side_tall')
        self.rm.block_model(wall + '_inventory', textures={'wall': texture}, parent='block/wall_inventory')
        self.rm.item_model(wall, parent=wall_inv, no_textures=True)
        return self

    def make_door(self, door_suffix: str = '_door', top_texture: Optional[str] = None, bottom_texture: Optional[str] = None) -> 'BlockContext':
        """
        Generates all blockstates and models required for a standard door
        """
        door = self.res.join() + door_suffix
        block = self.res.join('block/') + door_suffix
        bottom = block + '_bottom'
        bottom_hinge = block + '_bottom_hinge'
        top = block + '_top'
        top_hinge = block + '_top_hinge'

        if top_texture is None:
            top_texture = top
        if bottom_texture is None:
            bottom_texture = bottom

        self.rm.blockstate(door, variants=block_states.door_blockstate(bottom, bottom_hinge, top, top_hinge))
        self.rm.block_model(door + '_bottom', {'top': top_texture, 'bottom': bottom_texture}, parent='block/door_bottom')
        self.rm.block_model(door + '_bottom_hinge', {'top': top_texture, 'bottom': bottom_texture}, parent='block/door_bottom_rh')
        self.rm.block_model(door + '_top', {'top': top_texture, 'bottom': bottom_texture}, parent='block/door_top')
        self.rm.block_model(door + '_top_hinge', {'top': top_texture, 'bottom': bottom_texture}, parent='block/door_top_rh')
        self.rm.item_model(door)
        return self

    def make_trapdoor(self, trapdoor_suffix: str = '_trapdoor', texture: Optional[str] = None) -> 'BlockContext':
        """
        Generates all blockstates and models required for a standard trapdoor
        """
        block = self.res.join() + trapdoor_suffix
        trapdoor = self.res.join('block/') + trapdoor_suffix
        bottom = trapdoor + '_bottom'
        top = trapdoor + '_top'
        side = trapdoor + '_open'

        if texture is None:
            texture = trapdoor

        self.rm.blockstate(block, variants=block_states.trapdoor_blockstate(bottom, top, side))
        self.rm.block_model(block + '_bottom', {'texture': texture}, parent='block/template_orientable_trapdoor_bottom')
        self.rm.block_model(block + '_top', {'texture': texture}, parent='block/template_orientable_trapdoor_top')
        self.rm.block_model(block + '_open', {'texture': texture}, parent='block/template_orientable_trapdoor_open')
        self.rm.item_model(block, parent=bottom, no_textures=True)
        return self

    def make_button(self, button_suffix: str = '_button', texture: Optional[str] = None) -> 'BlockContext':
        """
        Generates all blockstates and models required for a standard button
        """
        button = self.res.join() + button_suffix
        block = self.res.join('block/')
        block_button = block + button_suffix
        block_pressed = block + button_suffix + '_pressed'

        if texture is None:
            texture = block

        self.rm.blockstate(button, variants=block_states.button_blockstate(block_button, block_pressed))
        self.rm.block_model(button, {'texture': texture}, parent='block/button')
        self.rm.block_model(button + '_pressed', {'texture': texture}, parent='block/button_pressed')
        self.rm.block_model(button + '_inventory', {'texture': texture}, parent='block/button_inventory')
        self.rm.item_model(button, parent=block_button + '_inventory', no_textures=True)
        return self

    def make_pressure_plate(self, pressure_plate_suffix: str = '_pressure_plate', texture: Optional[str] = None) -> 'BlockContext':
        """
        Generates all blockstates and models required for a standard pressure plate
        """
        pressure_plate = self.res.join() + pressure_plate_suffix
        block = self.res.join('block/')
        normal = block + pressure_plate_suffix
        down = block + pressure_plate_suffix + '_down'

        if texture is None:
            texture = block

        self.rm.blockstate(pressure_plate, variants=block_states.pressure_plate_variants(normal, down))
        self.rm.block_model(pressure_plate, {'texture': texture}, parent='block/pressure_plate_up')
        self.rm.block_model(pressure_plate + '_down', {'texture': texture}, parent='block/pressure_plate_down')
        self.rm.item_model(pressure_plate, parent=normal, no_textures=True)
        return self
