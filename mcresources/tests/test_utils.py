#  Part of mcresources by Alex O'Neill
#  Work under copyright. Licensed under MIT
#  For more information see the project LICENSE file

from unittest import TestCase, main

import mcresources.utils as utils


class UtilsTests(TestCase):
    def test_del_none(self):
        self.assertEqual({2: {4: 5}}, utils.del_none({1: None, 2: {3: None, 4: 5}}))

    def test_str_path(self):
        self.assertEqual(['a', 'b', 'c', 'd'], utils.str_path(['a', 'b/c', 'd']))
        self.assertEqual(['a', 'b', 'c', 'd'], utils.str_path('a/b/c/d'))
        self.assertEqual(['a', 'b', 'c', 'd'], utils.str_path(['a', ['b', 'c/d']]))

    def test_str_list(self):
        self.assertEqual(['a', 'b/c', 'd'], utils.str_list(['a', 'b/c', 'd']))
        self.assertEqual(['a/b/c/d'], utils.str_list('a/b/c/d'))
        self.assertEqual(['a', 'b', 'c/d'], utils.str_list(['a', ['b', 'c/d']]))

    def test_domain_path_parts(self):
        self.assertEqual(('modid', ['block', 'dirt']), utils.domain_path_parts('block/dirt', 'modid'))
        self.assertEqual(('modid', ['block', 'dirt']), utils.domain_path_parts(('block', 'dirt'), 'modid'))
        self.assertEqual(('minecraft', ['block', 'dirt']), utils.domain_path_parts('minecraft:block/dirt', 'modid'))
        self.assertEqual(('minecraft', ['block', 'dirt']), utils.domain_path_parts(('minecraft:block', 'dirt'), 'modid'))

    def test_flatten_list(self):
        self.assertEqual([1, 2, 3, 4, 5], [*utils.flatten_list([1, [2, 3, [4, 5]]])])

    def test_dict_get(self):
        d = {'a': 1, 'b': 2, 'c': 3, 1: 'A', 2: 'B', 3: 'C'}
        self.assertEqual(1, utils.dict_get(d, 'a', 26))
        self.assertEqual(26, utils.dict_get(d, 'z', 26))
        self.assertEqual('B', utils.dict_get(d, 'b', 25, lambda k: d[k]))

    def test_is_sequence(self):
        self.assertTrue(utils.is_sequence((1, 2)))
        self.assertTrue(utils.is_sequence([1, 2]))
        self.assertFalse(utils.is_sequence('12'))

    def test_resource_location(self):
        self.assertEqual(utils.ResourceLocation('minecraft', 'stone'), utils.resource_location('stone'))
        self.assertEqual(utils.ResourceLocation('minecraft', 'stone/special'), utils.resource_location(('stone', 'special')))
        self.assertEqual(utils.ResourceLocation('mymod', 'stone'), utils.resource_location('mymod', 'stone'))
        self.assertEqual(utils.ResourceLocation('mymod', 'stone/special'), utils.resource_location('mymod', ('stone', 'special')))
        self.assertEqual(utils.ResourceLocation('mymod', 'stone/special'), utils.resource_location('mymod', 'stone/special'))
        self.assertEqual(utils.ResourceLocation('mymod', 'stone/special'), utils.resource_location('mymod:stone/special'))
        self.assertEqual(utils.ResourceLocation('mymod', 'stone/special'), utils.resource_location('mymod:stone/special'), 'myothermod')

    def test_recipe_condition(self):
        self.assertEqual([{'type': 'stuff'}], utils.recipe_condition('stuff'))
        self.assertEqual([{'type': 'stuff'}], utils.recipe_condition({'type': 'stuff'}))
        self.assertEqual([{'type': 'one'}, {1: 'two'}], utils.recipe_condition(['one', {1: 'two'}]))

    def test_item_stack(self):
        self.assertEqual({'item': 'a'}, utils.item_stack('a'))
        self.assertEqual({'tag': 'b'}, utils.item_stack('tag!b'))
        self.assertEqual({1: 2}, utils.item_stack({1: 2}))
        self.assertEqual({'item': 'c', 'count': 3}, utils.item_stack([3, 'c']))

    def test_item_stack_list(self):
        self.assertEqual([{'item': 'stuff'}], utils.item_stack_list('stuff'))
        self.assertEqual([{'item': 'stuff'}, {'tag': 'thing'}], utils.item_stack_list(['stuff', 'tag!thing']))

    def test_lang_parts(self):
        self.assertEqual({'a': 'b'}, utils.lang_parts(['a', 'b']))
        self.assertEqual({'a': 'b', 'c': 'd'}, utils.lang_parts([{'a': 'b'}, 'c', 'd']))
        self.assertEqual({'a': 'b', 'c': 'd'}, utils.lang_parts([{'a': 'b'}, ('c', 'd')]))


if __name__ == '__main__':
    main()
