#  Part of mcresources by Alex O'Neill
#  Work under copyright. Licensed under MIT
#  For more information see the project LICENSE file


from unittest import TestCase, main

import mcresources.world_gen as wg


class UtilsTests(TestCase):

    def test_configure(self):
        self.assertEqual({'type': 'minecraft:name', 'config': {}}, wg.configure('name'))
        self.assertEqual({'type': 'minecraft:name', 'config': {'stuff': 'things'}}, wg.configure('name', {'stuff': 'things'}))

    def test_configure_decorated(self):
        self.assertEqual({'type': 'minecraft:name', 'config': {}}, wg.configure_decorated(wg.configure('name')))
        self.assertEqual({
            'type': 'minecraft:decorated',
            'config': {
                'feature': {},
                'decorator': {'type': 'minecraft:step1', 'config': {}}
            }
        }, wg.configure_decorated({}, 'step1'))
        self.assertEqual({
            'type': 'minecraft:decorated',
            'config': {
                'feature': {
                    'type': 'minecraft:decorated',
                    'config': {
                        'feature': {},
                        'decorator': {'type': 'minecraft:step2', 'config': {}}
                    }
                },
                'decorator': {'type': 'minecraft:step1', 'config': {}}
            }
        }, wg.configure_decorated({}, 'step1', 'step2'))
        self.assertEqual({
            'type': 'minecraft:decorated',
            'config': {
                'feature': {},
                'decorator': {'type': 'minecraft:step1', 'config': {'step1': '1'}}
            }
        }, wg.configure_decorated({}, ('step1', {'step1': '1'})))
        self.assertEqual({
            'type': 'minecraft:decorated',
            'config': {
                'feature': {
                    'type': 'minecraft:decorated',
                    'config': {
                        'feature': {},
                        'decorator': {'type': 'minecraft:step2', 'config': {}}
                    }
                },
                'decorator': {'type': 'minecraft:step1', 'config': {'step1': '1'}}
            }
        }, wg.configure_decorated({}, ('step1', {'step1': '1'}), 'step2'))

    def test_decorated(self):
        self.assertEqual({
            'type': 'minecraft:decorated',
            'config': {
                'feature': {},
                'decorator': {
                    'type': 'minecraft:d',
                    'config': {}
                }
            }
        }, wg.decorated({}, 'd'))
        self.assertEqual({
            'type': 'minecraft:decorated',
            'config': {
                'feature': {},
                'decorator': {
                    'type': 'minecraft:d',
                    'config': {'d': 'd'}
                }
            }
        }, wg.decorated({}, 'd', {'d': 'd'}))

    def test_surface_builder_config(self):
        self.assertEqual({
            'top_material': {'Name': 'block', 'Properties': {}},
            'under_material': {'Name': 'block2', 'Properties': {}},
            'underwater_material': {'Name': 'block3', 'Properties': {'p1': 'p2'}}
        }, wg.surface_builder_config('block', 'block2', 'block3[p1=p2]'))

    def test_expand_type_config(self):
        self.assertEqual({'type': 'name', 'config': {}}, wg.expand_type_config('name'))
        self.assertEqual({'type': 'name', 'config': {'a': 1}}, wg.expand_type_config(['name', {'a': 1}]))
        self.assertEqual({'type': 'name', 'config': {}}, wg.expand_type_config({'type': 'name'}))

        self.assertRaises(RuntimeError, lambda: wg.expand_type_config({}))
        self.assertRaises(RuntimeError, lambda: wg.expand_type_config(['name']))
        self.assertRaises(RuntimeError, lambda: wg.expand_type_config(['name', {}, 'extra']))

    def test_block_state(self):
        self.assertEqual({'Name': 'block', 'Properties': {}}, wg.block_state('block'))
        self.assertEqual({'Name': 'block', 'Properties': {'prop1': '1'}}, wg.block_state('block[prop1=1]'))
        self.assertEqual({'Name': 'block', 'Properties': {'prop1': '1', 'prop2': '2'}}, wg.block_state('block[prop1=1,prop2=2]'))
        self.assertEqual({'Name': 'block', 'Properties': {}}, wg.block_state({'Name': 'block'}))

        self.assertRaises(RuntimeError, lambda: wg.block_state({}))


if __name__ == '__main__':
    main()
