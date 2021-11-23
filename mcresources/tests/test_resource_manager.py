#  Part of mcresources by Alex O'Neill
#  Work under copyright. Licensed under MIT
#  For more information see the project LICENSE file

import os
import difflib

import loot_tables
import utils

from resource_manager import ResourceManager

rm = ResourceManager(domain='modid', resource_dir='generated', indent=2)
os.chdir('../../sample')

def test_blockstate():
    rm.blockstate('test_block')
    assert_file_equal('assets/modid/blockstates/test_block.json')

    rm.blockstate('test_block_variants', variants=dict((str(v), {}) for v in range(10)))
    assert_file_equal('assets/modid/blockstates/test_block_variants.json')

    rm.block('test_block').with_blockstate()
    assert_file_equal('assets/modid/blockstates/test_block.json')

    rm.block('test_block_variants').with_blockstate(variants=dict((str(v), {}) for v in range(10)))
    assert_file_equal('assets/modid/blockstates/test_block_variants.json')

def test_blockstate_multipart():
    rm.blockstate_multipart('test_block_multipart', {'model': 'stuff'}, ({'prop': True}, {'model': 'extra_stuff'}))
    assert_file_equal('assets/modid/blockstates/test_block_multipart.json')

    rm.block('test_block_multipart').with_blockstate_multipart({'model': 'stuff'}, ({'prop': True}, {'model': 'extra_stuff'}))
    assert_file_equal('assets/modid/blockstates/test_block_multipart.json')

def test_block_model():
    rm.block_model('test_block')
    assert_file_equal('assets/modid/models/block/test_block.json')

    rm.block('test_block').with_block_model()
    assert_file_equal('assets/modid/models/block/test_block.json')

def test_block_item_model():
    rm.block('test_block').with_item_model()
    assert_file_equal('assets/modid/models/item/test_block.json')

def test_custom_block_model():
    rm.custom_block_model('block_custom_loader', 'test_loader', {'raw_data': {'more_raw_data': 3}})
    assert_file_equal('assets/modid/models/block/block_custom_loader.json')

def test_item_model():
    rm.item_model('test_item')
    assert_file_equal('assets/modid/models/item/test_item.json')

    rm.item('test_item').with_item_model()
    assert_file_equal('assets/modid/models/item/test_item.json')

def test_item_model_no_textures():
    rm.item_model('item_no_textures', no_textures=True)
    assert_file_equal('assets/modid/models/item/item_no_textures.json')

def test_item_model_custom_textures():
    rm.item_model('item_custom_textures', {'first': 'a', 'second': 'b'})
    assert_file_equal('assets/modid/models/item/item_custom_textures.json')

def test_item_model_multiple_layers():
    rm.item_model('item_multiple_layers', 'layer_texture', 'layer2_texture')
    assert_file_equal('assets/modid/models/item/item_multiple_layers.json')

def test_custom_item_model():
    rm.custom_item_model('item_custom_loader', 'test_loader', {'raw_data': {'more_raw_data': 3}})
    assert_file_equal('assets/modid/models/item/item_custom_loader.json')

def test_crafting_shapeless():
    pass

def test_crafting_shaped():
    rm.crafting_shaped('my_block', ('XBX', 'X  ', '  B'), {'X': 'domain:my_item', 'B': 'minecraft:stone'}, 'domain:my_block').with_advancement('minecraft:dirt')
    assert_file_equal('data/modid/recipes/my_block.json')
    assert_file_equal('data/modid/advancements/my_block.json')

def test_recipe():
    pass

def test_item_tag():
    rm.item_tag('my_items', 'modid:item1')
    rm.flush()
    assert_file_equal('data/modid/tags/items/my_items.json')

    rm.item('item1').with_tag('my_items')
    rm.flush()
    assert_file_equal('data/modid/tags/items/my_items.json')

    rm.item_tag(('ingots', 'iron'), 'modid:iron_ingot', 'othermod:iron_ingot', replace=True)
    rm.flush()
    assert_file_equal('data/modid/tags/items/ingots/iron.json')

def test_block_tag():
    rm.block_tag('my_blocks', 'modid:block1')
    rm.flush()
    assert_file_equal('data/modid/tags/blocks/my_blocks.json')

    rm.block('block1').with_tag('othermod:their_blocks')
    rm.flush()
    assert_file_equal('data/othermod/tags/blocks/their_blocks.json')

    rm.block('block2').with_tag('someones/block')
    rm.flush()
    assert_file_equal('data/modid/tags/blocks/someones/block.json')

    # Check duplicates
    rm.block_tag('blocks/iron', 'modid:iron_block', 'othermod:iron_block', 'othermod:iron_block', 'othermod:iron_block', replace=True)
    rm.flush()
    assert_file_equal('data/modid/tags/blocks/blocks/iron.json')

def test_entity_tag():
    rm.entity_tag('my_entities', 'modid:entity1')
    rm.flush()
    assert_file_equal('data/modid/tags/entity_types/my_entities.json')

    rm.entity_tag(('things', 'stuff'), 'modid:my_entity', 'minecraft:other_entity', replace=True)
    rm.flush()
    assert_file_equal('data/modid/tags/entity_types/things/stuff.json')

def test_fluid_tag():
    rm.fluid_tag('my_fluids', 'modid:fluid')
    rm.flush()
    assert_file_equal('data/modid/tags/fluids/my_fluids.json')

    rm.fluid_tag(['special', 'lavas'], 'modid:lavathing', 'othermod:otherlava', replace=True)
    rm.flush()
    assert_file_equal('data/modid/tags/fluids/special/lavas.json')

def test_block_loot():
    rm.block_loot('my_block', 'modid:my_item')
    assert_file_equal('data/modid/loot_tables/blocks/my_block.json')

    rm.block_loot('my_block2', ['modid:my_item', 'modid:my_other_item'])
    assert_file_equal('data/modid/loot_tables/blocks/my_block2.json')

    rm.block_loot('my_block3', [{'rolls': 3, 'entries': 'modid:my_item'}])
    assert_file_equal('data/modid/loot_tables/blocks/my_block3.json')

    rm.block_loot('my_block4',
                       [{'rolls': 5, 'entries': [{'type': 'modid:other', 'data': 3}]}, 'modid:my_item'])
    assert_file_equal('data/modid/loot_tables/blocks/my_block4.json')

    rm.block_loot('burningtorch', [
        {
            'entries': 'burningtorch:charredtorchremains',
            'conditions': [
                'minecraft:survives_explosion',
                {
                    'condition': 'minecraft:block_state_property',
                    'block': 'burningtorch:burningtorch',
                    'properties': {'decay': decay}
                }
            ],
            'functions': {
                'function': 'minecraft:set_count',
                'count': amount
            }
        } for (decay, amount) in (('5', 8), ('4', 7), ('3', 5), ('2', 3), ('1', 1))
    ])
    assert_file_equal('data/modid/loot_tables/blocks/burningtorch.json')

    rm.block_loot('grass', [{'entries': {
        'type': 'minecraft:alternatives',
        'children': utils.loot_entry_list([{
            'name': 'minecraft:grass',
            'conditions': loot_tables.match_tool('minecraft:shears')
        }, {
            'name': 'notreepunching:plant_fiber',
            'conditions': [
                loot_tables.match_tool('tag!notreepunching:knives'),
                loot_tables.random_chance(0.25)
            ]
        }, {
            'conditions': loot_tables.random_chance(0.125),
            'functions': [
                loot_tables.fortune_bonus(2),
                'minecraft:explosion_decay'
            ],
            'name': 'minecraft:wheat_seeds'
        }])
    }, 'conditions': None}])
    assert_file_equal('data/modid/loot_tables/blocks/grass.json')

def test_lang():
    rm.lang('key', 'value')
    rm.lang('key', 'VALUE', language='not_en_us')
    rm.lang({'k': 'v'})

    rm.flush()
    assert_file_equal('assets/modid/lang/en_us.json')
    assert_file_equal('assets/modid/lang/not_en_us.json')

def test_block_lang():
    rm.block('sample_block').with_lang('Sample Block', 'en_us2')
    rm.block('othermod:stuff_block').with_lang('Other Block', 'en_us2')
    rm.block('sample/slash/block').with_lang('Sample Slash Block', 'en_us2')
    rm.flush()
    assert_file_equal('assets/modid/lang/en_us2.json')

def test_item_lang():
    rm.item('sample_item').with_lang('Sample Item', 'en_us3')
    rm.item('othermod:stuff_item').with_lang('Other Item', 'en_us3')
    rm.item('sample/slash/item').with_lang('Sample Slash Item', 'en_us3')
    rm.flush()
    assert_file_equal('assets/modid/lang/en_us3.json')

def test_block_slab():
    rm.block('wood').make_slab()
    assert_file_equal('assets/modid/blockstates/wood_slab.json')
    assert_file_equal('assets/modid/models/block/wood_slab.json')
    assert_file_equal('assets/modid/models/block/wood_slab_top.json')
    assert_file_equal('assets/modid/models/item/wood_slab.json')

def test_block_stairs():
    rm.block('wood').make_stairs()
    assert_file_equal('assets/modid/blockstates/wood_stairs.json')
    assert_file_equal('assets/modid/models/block/wood_stairs.json')
    assert_file_equal('assets/modid/models/block/wood_stairs_inner.json')
    assert_file_equal('assets/modid/models/block/wood_stairs_outer.json')
    assert_file_equal('assets/modid/models/item/wood_stairs.json')

def test_block_fence():
    rm.block('wood').make_fence()
    assert_file_equal('assets/modid/blockstates/wood_fence.json')
    assert_file_equal('assets/modid/models/block/wood_fence_post.json')
    assert_file_equal('assets/modid/models/block/wood_fence_side.json')
    assert_file_equal('assets/modid/models/block/wood_fence_inventory.json')
    assert_file_equal('assets/modid/models/item/wood_fence.json')

def test_block_fence_gate():
    rm.block('wood').make_fence_gate()
    assert_file_equal('assets/modid/blockstates/wood_fence_gate.json')
    assert_file_equal('assets/modid/models/block/wood_fence_gate.json')
    assert_file_equal('assets/modid/models/block/wood_fence_gate_open.json')
    assert_file_equal('assets/modid/models/block/wood_fence_gate_wall.json')
    assert_file_equal('assets/modid/models/block/wood_fence_gate_wall_open.json')
    assert_file_equal('assets/modid/models/item/wood_fence_gate.json')

def test_block_wall():
    rm.block('stone').make_wall()
    assert_file_equal('assets/modid/blockstates/stone_wall.json')
    assert_file_equal('assets/modid/models/block/stone_wall_post.json')
    assert_file_equal('assets/modid/models/block/stone_wall_side.json')
    assert_file_equal('assets/modid/models/block/stone_wall_side_tall.json')
    assert_file_equal('assets/modid/models/block/stone_wall_inventory.json')
    assert_file_equal('assets/modid/models/item/stone_wall.json')

def test_block_door():
    rm.block('wood').make_door()
    assert_file_equal('assets/modid/blockstates/wood_door.json')
    assert_file_equal('assets/modid/models/block/wood_door_bottom.json')
    assert_file_equal('assets/modid/models/block/wood_door_bottom_hinge.json')
    assert_file_equal('assets/modid/models/block/wood_door_top.json')
    assert_file_equal('assets/modid/models/block/wood_door_top_hinge.json')

def test_block_trapdoor():
    rm.block('wood').make_trapdoor()
    assert_file_equal('assets/modid/blockstates/wood_trapdoor.json')
    assert_file_equal('assets/modid/models/block/wood_trapdoor_bottom.json')
    assert_file_equal('assets/modid/models/block/wood_trapdoor_top.json')
    assert_file_equal('assets/modid/models/block/wood_trapdoor_open.json')
    assert_file_equal('assets/modid/models/item/wood_trapdoor.json')

def test_block_button():
    rm.block('wood').make_button()
    assert_file_equal('assets/modid/blockstates/wood_button.json')
    assert_file_equal('assets/modid/models/block/wood_button.json')
    assert_file_equal('assets/modid/models/block/wood_button_pressed.json')
    assert_file_equal('assets/modid/models/block/wood_button_inventory.json')
    assert_file_equal('assets/modid/models/item/wood_button.json')

def test_block_pressure_plate():
    rm.block('wood').make_pressure_plate()
    assert_file_equal('assets/modid/blockstates/wood_pressure_plate.json')
    assert_file_equal('assets/modid/models/block/wood_pressure_plate.json')
    assert_file_equal('assets/modid/models/block/wood_pressure_plate_down.json')
    assert_file_equal('assets/modid/models/item/wood_pressure_plate.json')


def assert_file_equal(path: str):
    assert os.path.isfile('test/' + path), 'No expected resource at %s' % path
    with open('test/' + path) as expected_file:
        expected = expected_file.read().split('\n')

    assert os.path.isfile('generated/' + path), 'No generated resource at %s' % path
    with open('generated/' + path) as actual_file:
        actual = actual_file.read().split('\n')
        assert expected == actual, 'Diff: %s' % '\n'.join(difflib.unified_diff(expected, actual, 'actual', 'expected', n=3))
