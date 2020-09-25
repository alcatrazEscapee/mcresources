#  Part of mcresources by Alex O'Neill
#  Work under copyright. Licensed under MIT
#  For more information see the project LICENSE file

from typing import Dict, List, Any


def slab_variants(block: str, block_slab: str, block_slab_top: str):
    return {
        'type=bottom': {'model': block_slab},
        'type=top': {'model': block_slab_top},
        'type=double': {'model': block}
    }


def stairs_variants(stairs: str, stairs_inner: str, stairs_outer: str) -> Dict[str, Any]:
    return {
        'facing=east,half=bottom,shape=straight': {'model': stairs},
        'facing=west,half=bottom,shape=straight': {'model': stairs, 'y': 180, 'uvlock': True},
        'facing=south,half=bottom,shape=straight': {'model': stairs, 'y': 90, 'uvlock': True},
        'facing=north,half=bottom,shape=straight': {'model': stairs, 'y': 270, 'uvlock': True},
        'facing=east,half=bottom,shape=outer_right': {'model': stairs_outer},
        'facing=west,half=bottom,shape=outer_right': {'model': stairs_outer, 'y': 180, 'uvlock': True},
        'facing=south,half=bottom,shape=outer_right': {'model': stairs_outer, 'y': 90, 'uvlock': True},
        'facing=north,half=bottom,shape=outer_right': {'model': stairs_outer, 'y': 270, 'uvlock': True},
        'facing=east,half=bottom,shape=outer_left': {'model': stairs_outer, 'y': 270, 'uvlock': True},
        'facing=west,half=bottom,shape=outer_left': {'model': stairs_outer, 'y': 90, 'uvlock': True},
        'facing=south,half=bottom,shape=outer_left': {'model': stairs_outer},
        'facing=north,half=bottom,shape=outer_left': {'model': stairs_outer, 'y': 180, 'uvlock': True},
        'facing=east,half=bottom,shape=inner_right': {'model': stairs_inner},
        'facing=west,half=bottom,shape=inner_right': {'model': stairs_inner, 'y': 180, 'uvlock': True},
        'facing=south,half=bottom,shape=inner_right': {'model': stairs_inner, 'y': 90, 'uvlock': True},
        'facing=north,half=bottom,shape=inner_right': {'model': stairs_inner, 'y': 270, 'uvlock': True},
        'facing=east,half=bottom,shape=inner_left': {'model': stairs_inner, 'y': 270, 'uvlock': True},
        'facing=west,half=bottom,shape=inner_left': {'model': stairs_inner, 'y': 90, 'uvlock': True},
        'facing=south,half=bottom,shape=inner_left': {'model': stairs_inner},
        'facing=north,half=bottom,shape=inner_left': {'model': stairs_inner, 'y': 180, 'uvlock': True},
        'facing=east,half=top,shape=straight': {'model': stairs, 'x': 180, 'uvlock': True},
        'facing=west,half=top,shape=straight': {'model': stairs, 'x': 180, 'y': 180, 'uvlock': True},
        'facing=south,half=top,shape=straight': {'model': stairs, 'x': 180, 'y': 90, 'uvlock': True},
        'facing=north,half=top,shape=straight': {'model': stairs, 'x': 180, 'y': 270, 'uvlock': True},
        'facing=east,half=top,shape=outer_right': {'model': stairs_outer, 'x': 180, 'y': 90, 'uvlock': True},
        'facing=west,half=top,shape=outer_right': {'model': stairs_outer, 'x': 180, 'y': 270, 'uvlock': True},
        'facing=south,half=top,shape=outer_right': {'model': stairs_outer, 'x': 180, 'y': 180, 'uvlock': True},
        'facing=north,half=top,shape=outer_right': {'model': stairs_outer, 'x': 180, 'uvlock': True},
        'facing=east,half=top,shape=outer_left': {'model': stairs_outer, 'x': 180, 'uvlock': True},
        'facing=west,half=top,shape=outer_left': {'model': stairs_outer, 'x': 180, 'y': 180, 'uvlock': True},
        'facing=south,half=top,shape=outer_left': {'model': stairs_outer, 'x': 180, 'y': 90, 'uvlock': True},
        'facing=north,half=top,shape=outer_left': {'model': stairs_outer, 'x': 180, 'y': 270, 'uvlock': True},
        'facing=east,half=top,shape=inner_right': {'model': stairs_inner, 'x': 180, 'y': 90, 'uvlock': True},
        'facing=west,half=top,shape=inner_right': {'model': stairs_inner, 'x': 180, 'y': 270, 'uvlock': True},
        'facing=south,half=top,shape=inner_right': {'model': stairs_inner, 'x': 180, 'y': 180, 'uvlock': True},
        'facing=north,half=top,shape=inner_right': {'model': stairs_inner, 'x': 180, 'uvlock': True},
        'facing=east,half=top,shape=inner_left': {'model': stairs_inner, 'x': 180, 'uvlock': True},
        'facing=west,half=top,shape=inner_left': {'model': stairs_inner, 'x': 180, 'y': 180, 'uvlock': True},
        'facing=south,half=top,shape=inner_left': {'model': stairs_inner, 'x': 180, 'y': 90, 'uvlock': True},
        'facing=north,half=top,shape=inner_left': {'model': stairs_inner, 'x': 180, 'y': 270, 'uvlock': True}
    }


def fence_multipart(fence_post: str, fence_side) -> List[Any]:
    return [
        {'model': fence_post},
        ({'north': 'true'}, {'model': fence_side, 'uvlock': True}),
        ({'east': 'true'}, {'model': fence_side, 'y': 90, 'uvlock': True}),
        ({'south': 'true'}, {'model': fence_side, 'y': 180, 'uvlock': True}),
        ({'west': 'true'}, {'model': fence_side, 'y': 270, 'uvlock': True})
    ]


def fence_gate_variants(fence_gate: str, fence_gate_open: str, fence_gate_wall: str, fence_gate_wall_open: str) -> Dict[str, Any]:
    return {
        'facing=south,in_wall=false,open=false': {'model': fence_gate, 'uvlock': True},
        'facing=west,in_wall=false,open=false': {'model': fence_gate, 'uvlock': True, 'y': 90},
        'facing=north,in_wall=false,open=false': {'model': fence_gate, 'uvlock': True, 'y': 180},
        'facing=east,in_wall=false,open=false': {'model': fence_gate, 'uvlock': True, 'y': 270},
        'facing=south,in_wall=false,open=true': {'model': fence_gate_open, 'uvlock': True},
        'facing=west,in_wall=false,open=true': {'model': fence_gate_open, 'uvlock': True, 'y': 90},
        'facing=north,in_wall=false,open=true': {'model': fence_gate_open, 'uvlock': True, 'y': 180},
        'facing=east,in_wall=false,open=true': {'model': fence_gate_open, 'uvlock': True, 'y': 270},
        'facing=south,in_wall=true,open=false': {'model': fence_gate_wall, 'uvlock': True},
        'facing=west,in_wall=true,open=false': {'model': fence_gate_wall, 'uvlock': True, 'y': 90},
        'facing=north,in_wall=true,open=false': {'model': fence_gate_wall, 'uvlock': True, 'y': 180},
        'facing=east,in_wall=true,open=false': {'model': fence_gate_wall, 'uvlock': True, 'y': 270},
        'facing=south,in_wall=true,open=true': {'model': fence_gate_wall_open, 'uvlock': True},
        'facing=west,in_wall=true,open=true': {'model': fence_gate_wall_open, 'uvlock': True, 'y': 90},
        'facing=north,in_wall=true,open=true': {'model': fence_gate_wall_open, 'uvlock': True, 'y': 180},
        'facing=east,in_wall=true,open=true': {'model': fence_gate_wall_open, 'uvlock': True, 'y': 270}
    }


def wall_multipart(wall_post: str, wall_side: str, wall_side_tall: str) -> List[Any]:
    return [
        ({'up': 'true'}, {'model': wall_post}),
        ({'north': 'low'}, {'model': wall_side, 'uvlock': True}),
        ({'east': 'low'}, {'model': wall_side, 'y': 90, 'uvlock': True}),
        ({'south': 'low'}, {'model': wall_side, 'y': 180, 'uvlock': True}),
        ({'west': 'low'}, {'model': wall_side, 'y': 270, 'uvlock': True}),
        ({'north': 'tall'}, {'model': wall_side_tall, 'uvlock': True}),
        ({'east': 'tall'}, {'model': wall_side_tall, 'y': 90, 'uvlock': True}),
        ({'south': 'tall'}, {'model': wall_side_tall, 'y': 180, 'uvlock': True}),
        ({'west': 'tall'}, {'model': wall_side_tall, 'y': 270, 'uvlock': True})
    ]


def door_blockstate(door_bottom: str, door_bottom_hinge: str, door_top: str, door_top_hinge: str):
    return {
        'facing=east,half=lower,hinge=left,open=false': {'model': door_bottom},
        'facing=south,half=lower,hinge=left,open=false': {'model': door_bottom, 'y': 90},
        'facing=west,half=lower,hinge=left,open=false': {'model': door_bottom, 'y': 180},
        'facing=north,half=lower,hinge=left,open=false': {'model': door_bottom, 'y': 270},
        'facing=east,half=lower,hinge=right,open=false': {'model': door_bottom_hinge},
        'facing=south,half=lower,hinge=right,open=false': {'model': door_bottom_hinge, 'y': 90},
        'facing=west,half=lower,hinge=right,open=false': {'model': door_bottom_hinge, 'y': 180},
        'facing=north,half=lower,hinge=right,open=false': {'model': door_bottom_hinge, 'y': 270},
        'facing=east,half=lower,hinge=left,open=true': {'model': door_bottom_hinge, 'y': 90},
        'facing=south,half=lower,hinge=left,open=true': {'model': door_bottom_hinge, 'y': 180},
        'facing=west,half=lower,hinge=left,open=true': {'model': door_bottom_hinge, 'y': 270},
        'facing=north,half=lower,hinge=left,open=true': {'model': door_bottom_hinge},
        'facing=east,half=lower,hinge=right,open=true': {'model': door_bottom, 'y': 270},
        'facing=south,half=lower,hinge=right,open=true': {'model': door_bottom},
        'facing=west,half=lower,hinge=right,open=true': {'model': door_bottom, 'y': 90},
        'facing=north,half=lower,hinge=right,open=true': {'model': door_bottom, 'y': 180},
        'facing=east,half=upper,hinge=left,open=false': {'model': door_top},
        'facing=south,half=upper,hinge=left,open=false': {'model': door_top, 'y': 90},
        'facing=west,half=upper,hinge=left,open=false': {'model': door_top, 'y': 180},
        'facing=north,half=upper,hinge=left,open=false': {'model': door_top, 'y': 270},
        'facing=east,half=upper,hinge=right,open=false': {'model': door_top_hinge},
        'facing=south,half=upper,hinge=right,open=false': {'model': door_top_hinge, 'y': 90},
        'facing=west,half=upper,hinge=right,open=false': {'model': door_top_hinge, 'y': 180},
        'facing=north,half=upper,hinge=right,open=false': {'model': door_top_hinge, 'y': 270},
        'facing=east,half=upper,hinge=left,open=true': {'model': door_top_hinge, 'y': 90},
        'facing=south,half=upper,hinge=left,open=true': {'model': door_top_hinge, 'y': 180},
        'facing=west,half=upper,hinge=left,open=true': {'model': door_top_hinge, 'y': 270},
        'facing=north,half=upper,hinge=left,open=true': {'model': door_top_hinge},
        'facing=east,half=upper,hinge=right,open=true': {'model': door_top, 'y': 270},
        'facing=south,half=upper,hinge=right,open=true': {'model': door_top},
        'facing=west,half=upper,hinge=right,open=true': {'model': door_top, 'y': 90},
        'facing=north,half=upper,hinge=right,open=true': {'model': door_top, 'y': 180}
    }


def trapdoor_blockstate(trapdoor_bottom: str, trapdoor_top: str, trapdoor_open: str) -> Dict[str, Any]:
    return {
        'facing=north,half=bottom,open=false': {'model': trapdoor_bottom},
        'facing=south,half=bottom,open=false': {'model': trapdoor_bottom, 'y': 180},
        'facing=east,half=bottom,open=false': {'model': trapdoor_bottom, 'y': 90},
        'facing=west,half=bottom,open=false': {'model': trapdoor_bottom, 'y': 270},
        'facing=north,half=top,open=false': {'model': trapdoor_top},
        'facing=south,half=top,open=false': {'model': trapdoor_top, 'y': 180},
        'facing=east,half=top,open=false': {'model': trapdoor_top, 'y': 90},
        'facing=west,half=top,open=false': {'model': trapdoor_top, 'y': 270},
        'facing=north,half=bottom,open=true': {'model': trapdoor_open},
        'facing=south,half=bottom,open=true': {'model': trapdoor_open, 'y': 180},
        'facing=east,half=bottom,open=true': {'model': trapdoor_open, 'y': 90},
        'facing=west,half=bottom,open=true': {'model': trapdoor_open, 'y': 270},
        'facing=north,half=top,open=true': {'model': trapdoor_open, 'x': 180, 'y': 180},
        'facing=south,half=top,open=true': {'model': trapdoor_open, 'x': 180, 'y': 0},
        'facing=east,half=top,open=true': {'model': trapdoor_open, 'x': 180, 'y': 270},
        'facing=west,half=top,open=true': {'model': trapdoor_open, 'x': 180, 'y': 90}
    }


def button_blockstate(button: str, pressed: str) -> Dict[str, Any]:
    return {
        'face=floor,facing=east,powered=false': {'model': button, 'y': 90},
        'face=floor,facing=west,powered=false': {'model': button, 'y': 270},
        'face=floor,facing=south,powered=false': {'model': button, 'y': 180},
        'face=floor,facing=north,powered=false': {'model': button},
        'face=wall,facing=east,powered=false': {'model': button, 'uvlock': True, 'x': 90, 'y': 90},
        'face=wall,facing=west,powered=false': {'model': button, 'uvlock': True, 'x': 90, 'y': 270},
        'face=wall,facing=south,powered=false': {'model': button, 'uvlock': True, 'x': 90, 'y': 180},
        'face=wall,facing=north,powered=false': {'model': button, 'uvlock': True, 'x': 90},
        'face=ceiling,facing=east,powered=false': {'model': button, 'x': 180, 'y': 270},
        'face=ceiling,facing=west,powered=false': {'model': button, 'x': 180, 'y': 90},
        'face=ceiling,facing=south,powered=false': {'model': button, 'x': 180},
        'face=ceiling,facing=north,powered=false': {'model': button, 'x': 180, 'y': 180},
        'face=floor,facing=east,powered=true': {'model': pressed, 'y': 90},
        'face=floor,facing=west,powered=true': {'model': pressed, 'y': 270},
        'face=floor,facing=south,powered=true': {'model': pressed, 'y': 180},
        'face=floor,facing=north,powered=true': {'model': pressed},
        'face=wall,facing=east,powered=true': {'model': pressed, 'uvlock': True, 'x': 90, 'y': 90},
        'face=wall,facing=west,powered=true': {'model': pressed, 'uvlock': True, 'x': 90, 'y': 270},
        'face=wall,facing=south,powered=true': {'model': pressed, 'uvlock': True, 'x': 90, 'y': 180},
        'face=wall,facing=north,powered=true': {'model': pressed, 'uvlock': True, 'x': 90},
        'face=ceiling,facing=east,powered=true': {'model': pressed, 'x': 180, 'y': 270},
        'face=ceiling,facing=west,powered=true': {'model': pressed, 'x': 180, 'y': 90},
        'face=ceiling,facing=south,powered=true': {'model': pressed, 'x': 180},
        'face=ceiling,facing=north,powered=true': {'model': pressed, 'x': 180, 'y': 180}
    }


def pressure_plate_variants(pressure_plate: str, pressure_plate_down: str) -> Dict[str, Any]:
    return {
        'powered=false': {'model': pressure_plate},
        'powered=true': {'model': pressure_plate_down}
    }
