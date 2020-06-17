#  Part of mcresources by Alex O'Neill
#  Work under copyright. Licensed under MIT
#  For more information see the project LICENSE file

from os import chdir
from os.path import isfile
from unittest import TestCase, main

import mcresources.loot_tables as loot_tables
import mcresources.utils as utils
from mcresources.resource_manager import ResourceManager
from mcresources.utils import clean_generated_resources


class ResourceManagerTests(TestCase):

    def test_blockstate(self):
        self.rm.blockstate('test_block')
        self.assertFileEqual('assets/modid/blockstates/test_block.json')

        self.rm.blockstate('test_block_variants', variants=dict((str(v), {}) for v in range(10)))
        self.assertFileEqual('assets/modid/blockstates/test_block_variants.json')

        self.rm.block('test_block').with_blockstate()
        self.assertFileEqual('assets/modid/blockstates/test_block.json')

        self.rm.block('test_block_variants').with_blockstate(variants=dict((str(v), {}) for v in range(10)))
        self.assertFileEqual('assets/modid/blockstates/test_block_variants.json')

    def test_blockstate_multipart(self):
        self.rm.blockstate_multipart('test_block_multipart', [{'model': 'stuff'}, ({'prop': True}, {'model': 'extra_stuff'})])
        self.assertFileEqual('assets/modid/blockstates/test_block_multipart.json')

        self.rm.block('test_block_multipart').with_blockstate_multipart([{'model': 'stuff'}, ({'prop': True}, {'model': 'extra_stuff'})])
        self.assertFileEqual('assets/modid/blockstates/test_block_multipart.json')

    def test_block_model(self):
        self.rm.block_model('test_block')
        self.assertFileEqual('assets/modid/models/block/test_block.json')

        self.rm.block('test_block').with_block_model()
        self.assertFileEqual('assets/modid/models/block/test_block.json')

    def test_block_item_model(self):
        self.rm.block('test_block').with_item_model()
        self.assertFileEqual('assets/modid/models/item/test_block.json')

    def test_item_model(self):
        self.rm.item_model('test_item')
        self.assertFileEqual('assets/modid/models/item/test_item.json')

        self.rm.item('test_item').with_item_model()
        self.assertFileEqual('assets/modid/models/item/test_item.json')

    def test_crafting_shapeless(self):
        pass

    def test_crafting_shaped(self):
        self.rm.crafting_shaped('my_block', ('XBX', 'X  ', '  B'), {'X': 'domain:my_item', 'B': 'minecraft:stone'}, 'domain:my_block').with_advancement('minecraft:dirt')
        self.assertFileEqual('data/modid/recipes/my_block.json')
        self.assertFileEqual('data/modid/advancements/my_block.json')

    def test_recipe(self):
        pass

    def test_item_tag(self):
        self.rm.item_tag('my_items', 'modid:item1')
        self.rm.flush()
        self.assertFileEqual('data/modid/tags/items/my_items.json')

        self.rm.item('item1').with_tag('my_items')
        self.rm.flush()
        self.assertFileEqual('data/modid/tags/items/my_items.json')

        self.rm.item_tag(('ingots', 'iron'), 'modid:iron_ingot', 'othermod:iron_ingot', replace=True)
        self.rm.flush()
        self.assertFileEqual('data/modid/tags/items/ingots/iron.json')

    def test_block_tag(self):
        self.rm.block_tag('my_blocks', 'modid:block1')
        self.rm.flush()
        self.assertFileEqual('data/modid/tags/blocks/my_blocks.json')

        self.rm.block('block1').with_tag('othermod:their_blocks')
        self.rm.flush()
        self.assertFileEqual('data/othermod/tags/blocks/their_blocks.json')

        self.rm.block('block2').with_tag('someones/block')
        self.rm.flush()
        self.assertFileEqual('data/modid/tags/blocks/someones/block.json')

        self.rm.block_tag('blocks/iron', 'modid:iron_block', 'othermod:iron_block', replace=True)
        self.rm.flush()
        self.assertFileEqual('data/modid/tags/blocks/blocks/iron.json')

    def test_entity_tag(self):
        self.rm.entity_tag('my_entities', 'modid:entity1')
        self.rm.flush()
        self.assertFileEqual('data/modid/tags/entity_types/my_entities.json')

        self.rm.entity_tag(('things', 'stuff'), 'modid:my_entity', 'minecraft:other_entity', replace=True)
        self.rm.flush()
        self.assertFileEqual('data/modid/tags/entity_types/things/stuff.json')

    def test_fluid_tag(self):
        self.rm.fluid_tag('my_fluids', 'modid:fluid')
        self.rm.flush()
        self.assertFileEqual('data/modid/tags/fluids/my_fluids.json')

        self.rm.fluid_tag(['special', 'lavas'], 'modid:lavathing', 'othermod:otherlava', replace=True)
        self.rm.flush()
        self.assertFileEqual('data/modid/tags/fluids/special/lavas.json')

    def test_block_loot(self):
        self.rm.block_loot('my_block', 'modid:my_item')
        self.assertFileEqual('data/modid/loot_tables/blocks/my_block.json')

        self.rm.block_loot('my_block2', ['modid:my_item', 'modid:my_other_item'])
        self.assertFileEqual('data/modid/loot_tables/blocks/my_block2.json')

        self.rm.block_loot('my_block3', [{'rolls': 3, 'entries': 'modid:my_item'}])
        self.assertFileEqual('data/modid/loot_tables/blocks/my_block3.json')

        self.rm.block_loot('my_block4',
                           [{'rolls': 5, 'entries': [{'type': 'modid:other', 'data': 3}]}, 'modid:my_item'])
        self.assertFileEqual('data/modid/loot_tables/blocks/my_block4.json')

        self.rm.block_loot('burningtorch', [
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
        self.assertFileEqual('data/modid/loot_tables/blocks/burningtorch.json')

        self.rm.block_loot('grass', [{'entries': {
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
        self.assertFileEqual('data/modid/loot_tables/blocks/grass.json')

    def test_lang(self):
        self.rm.lang('key', 'value')
        self.rm.lang('key', 'VALUE', language='not_en_us')
        self.rm.lang({'k': 'v'})

        self.rm.flush()
        self.assertFileEqual('assets/modid/lang/en_us.json')
        self.assertFileEqual('assets/modid/lang/not_en_us.json')

    def test_block_lang(self):
        self.rm.block('sample_block').with_lang('Sample Block', 'en_us2')
        self.rm.block('othermod:stuff_block').with_lang('Other Block', 'en_us2')
        self.rm.block('sample/slash/block').with_lang('Sample Slash Block', 'en_us2')
        self.rm.flush()
        self.assertFileEqual('assets/modid/lang/en_us2.json')

    def test_item_lang(self):
        self.rm.item('sample_item').with_lang('Sample Item', 'en_us3')
        self.rm.item('othermod:stuff_item').with_lang('Other Item', 'en_us3')
        self.rm.item('sample/slash/item').with_lang('Sample Slash Item', 'en_us3')
        self.rm.flush()
        self.assertFileEqual('assets/modid/lang/en_us3.json')

    def test_block_slab(self):
        self.rm.block('wood').make_slab()
        self.assertFileEqual('assets/modid/blockstates/wood_slab.json')
        self.assertFileEqual('assets/modid/models/block/wood_slab.json')
        self.assertFileEqual('assets/modid/models/block/wood_slab_top.json')
        self.assertFileEqual('assets/modid/models/item/wood_slab.json')

    def test_block_stairs(self):
        self.rm.block('wood').make_stairs()
        self.assertFileEqual('assets/modid/blockstates/wood_stairs.json')
        self.assertFileEqual('assets/modid/models/block/wood_stairs.json')
        self.assertFileEqual('assets/modid/models/block/wood_stairs_inner.json')
        self.assertFileEqual('assets/modid/models/block/wood_stairs_outer.json')
        self.assertFileEqual('assets/modid/models/item/wood_stairs.json')

    def test_block_fence(self):
        self.rm.block('wood').make_fence()
        self.assertFileEqual('assets/modid/blockstates/wood_fence.json')
        self.assertFileEqual('assets/modid/models/block/wood_fence_post.json')
        self.assertFileEqual('assets/modid/models/block/wood_fence_side.json')
        self.assertFileEqual('assets/modid/models/block/wood_fence_inventory.json')
        self.assertFileEqual('assets/modid/models/item/wood_fence.json')

    def test_block_fence_gate(self):
        self.rm.block('wood').make_fence_gate()
        self.assertFileEqual('assets/modid/blockstates/wood_fence_gate.json')
        self.assertFileEqual('assets/modid/models/block/wood_fence_gate.json')
        self.assertFileEqual('assets/modid/models/block/wood_fence_gate_open.json')
        self.assertFileEqual('assets/modid/models/block/wood_fence_gate_wall.json')
        self.assertFileEqual('assets/modid/models/block/wood_fence_gate_wall_open.json')
        self.assertFileEqual('assets/modid/models/item/wood_fence_gate.json')

    def test_block_wall(self):
        self.rm.block('stone').make_wall()
        self.assertFileEqual('assets/modid/blockstates/stone_wall.json')
        self.assertFileEqual('assets/modid/models/block/stone_wall_post.json')
        self.assertFileEqual('assets/modid/models/block/stone_wall_side.json')
        self.assertFileEqual('assets/modid/models/block/stone_wall_inventory.json')
        self.assertFileEqual('assets/modid/models/item/stone_wall.json')

    def test_block_door(self):
        self.rm.block('wood').make_door()
        self.assertFileEqual('assets/modid/blockstates/wood_door.json')
        self.assertFileEqual('assets/modid/models/block/wood_door_bottom.json')
        self.assertFileEqual('assets/modid/models/block/wood_door_bottom_hinge.json')
        self.assertFileEqual('assets/modid/models/block/wood_door_top.json')
        self.assertFileEqual('assets/modid/models/block/wood_door_top_hinge.json')

    def test_block_trapdoor(self):
        self.rm.block('wood').make_trapdoor()
        self.assertFileEqual('assets/modid/blockstates/wood_trapdoor.json')
        self.assertFileEqual('assets/modid/models/block/wood_trapdoor_bottom.json')
        self.assertFileEqual('assets/modid/models/block/wood_trapdoor_top.json')
        self.assertFileEqual('assets/modid/models/block/wood_trapdoor_open.json')
        self.assertFileEqual('assets/modid/models/item/wood_trapdoor.json')

    def test_block_button(self):
        self.rm.block('wood').make_button()
        self.assertFileEqual('assets/modid/blockstates/wood_button.json')
        self.assertFileEqual('assets/modid/models/block/wood_button.json')
        self.assertFileEqual('assets/modid/models/block/wood_button_pressed.json')
        self.assertFileEqual('assets/modid/models/block/wood_button_inventory.json')
        self.assertFileEqual('assets/modid/models/item/wood_button.json')

    def test_block_pressure_plate(self):
        self.rm.block('wood').make_pressure_plate()
        self.assertFileEqual('assets/modid/blockstates/wood_pressure_plate.json')
        self.assertFileEqual('assets/modid/models/block/wood_pressure_plate.json')
        self.assertFileEqual('assets/modid/models/block/wood_pressure_plate_down.json')
        self.assertFileEqual('assets/modid/models/item/wood_pressure_plate.json')

    @classmethod
    def setUpClass(cls):
        cls.rm = ResourceManager(domain='modid', resource_dir='generated', indent=2)
        chdir('../../sample')

    @classmethod
    def tearDownClass(cls):
        clean_generated_resources('generated')

    def assertFileEqual(self, path: str):
        if isfile('test/' + path):
            with open('test/' + path) as expected_file:
                expected = expected_file.read()
            if not isfile('generated/' + path):
                self.fail('File: ' + path + ' not found')
            with open('generated/' + path) as actual:
                self.assertEqual(actual.read(), expected)
        else:
            self.fail('Test ' + path + ' had no matching json')


if __name__ == '__main__':
    main()
