import os
import sys
import pytest
import difflib

from mcresources import utils, atlases, advancements, loot_tables
from mcresources.resource_manager import ResourceManager


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
ACTUAL_DIR = os.path.join(ROOT_DIR, 'actual')
EXPECTED_DIR = os.path.join(ROOT_DIR, 'expected')

rm = ResourceManager(domain='modid', resource_dir=ACTUAL_DIR, indent=2, ensure_ascii=False)
os.makedirs(ACTUAL_DIR, exist_ok=True)
utils.clean_generated_resources(ACTUAL_DIR, set())


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

def test_item_model_overrides():
    rm.item_model('item_overrides', 'base_texture', overrides=[{'stuff here': 'yes'}])
    assert_file_equal('assets/modid/models/item/item_overrides.json')

def test_custom_item_model():
    rm.custom_item_model('item_custom_loader', 'test_loader', {'raw_data': {'more_raw_data': 3}})
    assert_file_equal('assets/modid/models/item/item_custom_loader.json')

def test_atlas():
    rm.atlas('custom_atlas', atlases.single('modid:chests/iron'), atlases.directory('block'))
    assert_file_equal('assets/modid/atlases/custom_atlas.json')


def test_crafting_shapeless():
    rm.crafting_shapeless('basic_shapeless', 'minecraft:foo', 'domain:my_item')
    assert_file_equal('data/modid/recipes/basic_shapeless.json')

    rm.crafting_shapeless('shapeless_multi_ingredient', ['minecraft:bar', 'modid:fizz', {'tag': 'modid:buzz'}, '#minecraft:baz', ('a:b', 'b:c')], 'domain:my_item')
    assert_file_equal('data/modid/recipes/shapeless_multi_ingredient.json')

def test_crafting_shaped():
    rm.crafting_shaped('my_block', ('XBX', 'X  ', '  B'), {'X': 'domain:my_item', 'B': 'minecraft:stone'}, 'domain:my_block').with_advancement('minecraft:dirt')
    assert_file_equal('data/modid/recipes/my_block.json')
    assert_file_equal('data/modid/advancements/my_block.json')

def test_recipe():
    pass

def test_advancements():
    category = advancements.AdvancementCategory(rm, 'my_category', 'background.png')
    root = category.advancement('root', 'domain:item', 'My Advancement Tree', 'The tree.', parent=None, criteria={'crit': advancements.first_tick()})
    root.add_child('child', 'domain:item', 'My Advancement Tree', 'The tree.', criteria={'crit1': advancements.inventory_changed('domain:sword'), 'crit2': advancements.inventory_changed('domain:axe')}, requirements='and', frame='challenge')
    assert_file_equal('data/modid/advancements/my_category/root.json')
    assert_file_equal('data/modid/advancements/my_category/root.json')

def test_item_tag():
    rm.item_tag('my_items', 'modid:item1')
    rm.flush()
    assert_file_equal('data/modid/tags/item/my_items.json')

def test_item_context_with_tag_no_domain():
    rm.item('item1').with_tag('my_items')
    rm.flush()
    assert_file_equal('data/modid/tags/item/my_items.json')

def test_item_tag_multiple_values():
    rm.item_tag(('ingots', 'iron'), 'modid:iron_ingot', 'othermod:iron_ingot', replace=True)
    rm.flush()
    assert_file_equal('data/modid/tags/item/ingots/iron.json')

def test_block_tag():
    rm.block_tag('my_blocks', 'modid:block1')
    rm.flush()
    assert_file_equal('data/modid/tags/block/my_blocks.json')

def test_block_context_with_tag_other_domain():
    rm.block('block1').with_tag('othermod:their_blocks')
    rm.flush()
    assert_file_equal('data/othermod/tags/block/their_blocks.json')

def test_block_context_with_tag_no_domain():
    rm.block('block2').with_tag('someones/block')
    rm.flush()
    assert_file_equal('data/modid/tags/block/someones/block.json')

def test_block_context_with_item_tag():
    rm.block('block3').with_item_tag('blocks_as_items')
    rm.flush()
    assert_file_equal('data/modid/tags/item/blocks_as_items.json')

def test_block_tag_with_duplicates():
    rm.block_tag('blocks/iron', 'modid:iron_block', 'othermod:iron_block', 'othermod:iron_block', 'othermod:iron_block', replace=True)
    rm.flush()
    assert_file_equal('data/modid/tags/block/blocks/iron.json')

def test_entity_tag():
    rm.entity_tag('my_entities', 'modid:entity1')
    rm.flush()
    assert_file_equal('data/modid/tags/entity_type/my_entities.json')

def test_entity_tag_multiple_values():
    rm.entity_tag(('things', 'stuff'), 'modid:my_entity', 'minecraft:other_entity', replace=True)
    rm.flush()
    assert_file_equal('data/modid/tags/entity_type/things/stuff.json')

def test_fluid_tag():
    rm.fluid_tag('my_fluids', 'modid:fluid')
    rm.flush()
    assert_file_equal('data/modid/tags/fluid/my_fluids.json')

def test_fluid_tag_multiple_values():
    rm.fluid_tag(['special', 'lavas'], 'modid:lavathing', 'othermod:otherlava', replace=True)
    rm.flush()
    assert_file_equal('data/modid/tags/fluid/special/lavas.json')

def test_block_loot_simple():
    rm.block_loot('block1', 'modid:block1')
    assert_file_equal('data/modid/loot_table/blocks/block1.json')

def test_block_loot_set_count_implicit():
    rm.block_loot('block2', '3 modid:block3')
    assert_file_equal('data/modid/loot_table/blocks/block2.json')

def test_block_loot_set_count_uniform_implicit():
    rm.block_loot('block3', '5-7 modid:block3')
    assert_file_equal('data/modid/loot_table/blocks/block3.json')

def test_block_loot_one_entry():
    rm.block_loot('block4', {
        'name': 'modid:block4',
        'conditions': ['minecraft:mystery_condition'],
        'functions': ['minecraft:mystery_function']
    })
    assert_file_equal('data/modid/loot_table/blocks/block4.json')

def test_block_loot_one_pool():
    rm.block_loot('block5', {
        'name': 'modid:block5',
        'rolls': 3,
        'entries': '1-2 modid:block5'
    })
    assert_file_equal('data/modid/loot_table/blocks/block5.json')

def test_block_loot_multiple_entries_alternatives():
    rm.block_loot('block6', ('block6_first', 'block6_second'))
    assert_file_equal('data/modid/loot_table/blocks/block6.json')

def test_block_loot_multiple_pools():
    rm.block_loot('block7', 'block7_first', 'block7_second')
    assert_file_equal('data/modid/loot_table/blocks/block7.json')

def test_block_loot_set_count_implicit_with_entry():
    rm.block_loot('block8', {
        'name': '3 modid:block8',
        'conditions': ['minecraft:mystery_condition'],
        'functions': ['minecraft:mystery_function']
    })
    assert_file_equal('data/modid/loot_table/blocks/block8.json')

def test_block_loot_set_count_implicit_with_entry_with_no_functions():
    rm.block_loot('block9', {
        'name': '3 modid:block9',
        'conditions': ['minecraft:mystery_condition']
    })
    assert_file_equal('data/modid/loot_table/blocks/block9.json')

def test_block_loot_all_of_condition():
    rm.block_loot('block10', {
        'name': 'stone',
        'conditions': loot_tables.all_of('minecraft:killed_by_player', loot_tables.random_chance(0.123))
    })
    assert_file_equal('data/modid/loot_table/blocks/block10.json')

def test_block_loot_any_of_condition():
    rm.block_loot('block11', {
        'name': 'stone',
        'conditions': loot_tables.any_of(loot_tables.survives_explosion(), loot_tables.random_chance(0.321))
    })
    assert_file_equal('data/modid/loot_table/blocks/block11.json')

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
    rm.block('expected/slash/block').with_lang('Sample Slash Block', 'en_us2')
    rm.flush()
    assert_file_equal('assets/modid/lang/en_us2.json')

def test_item_lang():
    rm.item('sample_item').with_lang('Sample Item', 'en_us3')
    rm.item('othermod:stuff_item').with_lang('Other Item', 'en_us3')
    rm.item('expected/slash/item').with_lang('Sample Slash Item', 'en_us3')
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


# === World Generation ===

def test_dimension():
    rm.dimension('pink', 'pink_type', {
        'type': 'pink:pink',
        'seed': 1234
    })
    assert_file_equal('data/modid/dimension/pink.json')

def test_dimension_type():
    rm.dimension_type('pink_type', 0, True, False, True, False, 1, True, False, False, False, -32, 128, 128, 'overworld', 'the_nether', 0.125)
    assert_file_equal('data/modid/dimension_type/pink_type.json')

def test_biome():
    rm.biome('ocean')
    assert_file_equal('data/modid/worldgen/biome/ocean.json')

def test_configured_carver():
    rm.configured_carver('cave', 'minecraft:cave', {'probability': 1})
    assert_file_equal('data/modid/worldgen/configured_carver/cave.json')

def test_configured_feature():
    rm.configured_feature('lava_lake', 'minecraft:lake', {'block': 'minecraft:lava'})
    assert_file_equal('data/modid/worldgen/configured_feature/lava_lake.json')

def test_configured_structure_feature():
    rm.configured_structure_feature('big_house', 'minecraft:house')
    assert_file_equal('data/modid/worldgen/configured_structure_feature/big_house.json')

def test_placed_feature():
    rm.placed_feature('copper_ore', 'minecraft:copper_ore', 'in_square', 'modid:special_placement', ('not_in_square', {'amount': 3}), ('modid:super_special_placement', {'value': 123}))
    assert_file_equal('data/modid/worldgen/placed_feature/copper_ore.json')

def test_noise():
    rm.noise('calcite', -9, 1.0, 1.0, 1.0, 1.0)
    assert_file_equal('data/modid/worldgen/noise/calcite.json')

def test_noise_settings():
    rm.noise_settings('overworld', True, True, False, False, True, True, 'minecraft:stone', 'minecraft:water[level=0]', 63, {'complicated': True}, {'very_complicated': True}, {'superbly_complicated': True})
    assert_file_equal('data/modid/worldgen/noise_settings/overworld.json')

def test_ensure_ascii():
    try:
        rm.ensure_ascii = True
        rm.block_tag('ensure_ascii_true', '𝓝𝓸𝓷 𝓐𝓢𝓒𝓘𝓘 𝓣𝓮𝔁𝓽')
        rm.flush()
        assert_file_equal('data/modid/tags/block/ensure_ascii_true.json')

        rm.ensure_ascii = False
        rm.block_tag('ensure_ascii_false', '𝓝𝓸𝓷 𝓐𝓢𝓒𝓘𝓘 𝓣𝓮𝔁𝓽')
        rm.flush()
        assert_file_equal('data/modid/tags/block/ensure_ascii_false.json')
    finally:
        rm.ensure_ascii = True


def assert_file_equal(path: str):
    expected_path = os.path.join(EXPECTED_DIR, path)
    actual_path = os.path.join(ACTUAL_DIR, path)

    if not os.path.isfile(expected_path):
        with open(expected_path, 'w', encoding='utf-8') as new_file:
            new_file.write('{}\n')
        pytest.fail('No expected resource at %s, creating blank file' % path)

    with open(expected_path, 'r', encoding='utf-8') as expected_file:
        expected = expected_file.read()

    if not os.path.isfile(actual_path):
        pytest.fail('No generated resource at %s' % path)

    with open(actual_path, 'r', encoding='utf-8') as actual_file:
        actual = actual_file.read()

    if expected != actual:
        diff = '\n'.join(difflib.unified_diff(expected.split('\n'), actual.split('\n'), 'actual', 'expected', n=3))
        print('\nAssertion Failed: File Content Not Equal\n=== Expected ===\n%s\n=== Actual ===\n%s\n=== Diff ===\n%s' % (expected, actual, diff), file=sys.stderr)
        pytest.fail('File Content Not Equal')
