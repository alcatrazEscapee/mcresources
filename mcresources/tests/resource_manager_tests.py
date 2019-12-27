#  Part of mcresources by Alex O'Neill
#  Work under copyright. Licensed under MIT
#  For more information see the project LICENSE file

from os import chdir
from os.path import isfile
from unittest import TestCase, main

from mcresources.resource_manager import ResourceManager, clean_generated_resources


class TestResourceManager(TestCase):

    def test_blockstate(self):
        self.rm.blockstate('test_block')
        self.assertFileEqual('assets/modid/blockstates/test_block.json')

        self.rm.blockstate('test_block_variants', variants=dict((str(v), {}) for v in range(10)))
        self.assertFileEqual('assets/modid/blockstates/test_block_variants.json')

    def test_block_model(self):
        self.rm.block_model('test_block')
        self.assertFileEqual('assets/modid/models/block/test_block.json')

    def test_block_item_model(self):
        self.rm.block_item_model('test_block')
        self.assertFileEqual('assets/modid/models/item/test_block.json')

    def test_item_model(self):
        self.rm.item_model('test_item')
        self.assertFileEqual('assets/modid/models/item/test_item.json')

    def test_crafting_shapeless(self):
        pass

    def test_crafting_shaped(self):
        pass

    def test_recipe(self):
        pass

    def test_item_tag(self):
        self.rm.item_tag('my_items', 'modid:item1')
        self.assertFileEqual('data/modid/tags/items/my_items.json')

        self.rm.item_tag(('ingots', 'iron'), 'modid:iron_ingot', 'othermod:iron_ingot', replace=True)
        self.assertFileEqual('data/modid/tags/items/ingots/iron.json')

    def test_block_tag(self):
        self.rm.block_tag('my_blocks', 'modid:block1')
        self.assertFileEqual('data/modid/tags/blocks/my_blocks.json')

        self.rm.block_tag('blocks/iron', ('modid:iron_block', 'othermod:iron_block'), replace=True)
        self.assertFileEqual('data/modid/tags/blocks/blocks/iron.json')

    def test_entity_tag(self):
        self.rm.entity_tag('my_entities', 'modid:entity1')
        self.assertFileEqual('data/modid/tags/entity_types/my_entities.json')

        self.rm.entity_tag(('things', 'stuff'), ['modid:my_entity', 'minecraft:other_entity'], replace=True)
        self.assertFileEqual('data/modid/tags/entity_types/things/stuff.json')

    def test_fluid_tag(self):
        self.rm.fluid_tag('my_fluids', 'modid:fluid')
        self.assertFileEqual('data/modid/tags/fluids/my_fluids.json')

        self.rm.fluid_tag(['special', 'lavas'], ('modid:lavathing', 'othermod:otherlava'), replace=True)
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
