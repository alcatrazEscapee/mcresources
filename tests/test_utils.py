from mcresources.type_definitions import ResourceLocation
from mcresources import utils


def test_del_none():
    assert {2: {4: 5}} == utils.del_none({1: None, 2: {3: None, 4: 5}})

def test_str_path():
    assert ['a', 'b', 'c', 'd'] == utils.str_path(['a', 'b/c', 'd'])
    assert ['a', 'b', 'c', 'd'] == utils.str_path('a/b/c/d')
    assert ['a', 'b', 'c', 'd'] == utils.str_path(['a', ['b', 'c/d']])

def test_domain_path_parts():
    assert ('modid', ['block', 'dirt']) == utils.domain_path_parts('block/dirt', 'modid')
    assert ('modid', ['block', 'dirt']) == utils.domain_path_parts(('block', 'dirt'), 'modid')
    assert ('minecraft', ['block', 'dirt']) == utils.domain_path_parts('minecraft:block/dirt', 'modid')
    assert ('minecraft', ['block', 'dirt']) == utils.domain_path_parts(('minecraft:block', 'dirt'), 'modid')

def test_flatten_list():
    assert [1, 2, 3, 4, 5] == [*utils.flatten_list([1, [2, 3, [4, 5]]])]

def test_dict_get():
    d = {'a': 1, 'b': 2, 'c': 3, 1: 'A', 2: 'B', 3: 'C'}
    assert 1 == utils.dict_get(d, 'a', 26)
    assert 26 == utils.dict_get(d, 'z', 26)
    assert 'B' == utils.dict_get(d, 'b', 25, lambda k: d[k])

def test_is_sequence():
    assert utils.is_sequence((1, 2))
    assert utils.is_sequence([1, 2])
    assert not utils.is_sequence('12')

def test_resource_location():
    assert ResourceLocation('minecraft', 'stone') == utils.resource_location('stone')
    assert ResourceLocation('minecraft', 'stone/special') == utils.resource_location(('stone', 'special'))
    assert ResourceLocation('mymod', 'stone') == utils.resource_location('mymod', 'stone')
    assert ResourceLocation('mymod', 'stone/special') == utils.resource_location('mymod', ('stone', 'special'))
    assert ResourceLocation('mymod', 'stone/special') == utils.resource_location('mymod', 'stone/special')
    assert ResourceLocation('mymod', 'stone/special') == utils.resource_location('mymod:stone/special')
    assert ResourceLocation('mymod', 'stone/special') == utils.resource_location('mymod:stone/special')

def test_recipe_condition():
    assert [{'type': 'stuff'}] == utils.recipe_condition('stuff')
    assert [{'type': 'stuff'}] == utils.recipe_condition({'type': 'stuff'})
    assert [{'type': 'one'}, {1: 'two'}] == utils.recipe_condition(['one', {1: 'two'}])

def test_item_stack():
    assert {'item': 'a'} == utils.item_stack('a')
    assert {'tag': 'b'} == utils.item_stack('#b')
    assert {1: 2} == utils.item_stack({1: 2})
    assert {'tag': 'a'} == utils.item_stack('#a')
    assert {'item': 'foo', 'count': 1} == utils.item_stack((1, 'foo'))
    assert {'item': 'foo', 'count': 2} == utils.item_stack(('foo', 2))
    assert {'item': 'foo', 'count': 3} == utils.item_stack('3 foo')

def test_item_stack_list():
    assert [{'item': 'stuff'}] == utils.item_stack_list('stuff')
    assert [{'item': 'stuff'}, {'tag': 'thing'}] == utils.item_stack_list(['stuff', '#thing'])
    assert [{'tag': 'thing'}] == utils.item_stack_list(['#thing'])

def test_parse_item_stack():
    assert ('a', False, None, None) == utils.parse_item_stack('a')
    assert ('b', True, None, None) == utils.parse_item_stack('#b')
    assert ('c', False, 1, 1) == utils.parse_item_stack('1 c')
    assert ('d', True, 2, 2) == utils.parse_item_stack('2 #d')
    assert ('e', False, 3, 4) == utils.parse_item_stack('3-4 e')
    assert ('f', True, 5, 6) == utils.parse_item_stack('5-6 #f')

def test_tag_entry():
    assert 'minecraft:foo' == utils.tag_entry('foo', 'minecraft')
    assert 'domain:foo' == utils.tag_entry('domain:foo', 'minecraft')
    assert {'id': 'foo:bar', 'required': False} == utils.tag_entry({'id': 'foo:bar', 'required': False}, 'minecraft')
    assert {'id': 'minecraft:buzz', 'required': False} == utils.tag_entry('buzz?', 'minecraft')
    assert {'id': 'fizz:buzz', 'required': False} == utils.tag_entry('fizz:buzz?', 'minecraft')

def test_lang_parts():
    assert {'a': 'b'} == utils.lang_parts(['a', 'b'])
    assert {'a': 'b', 'c': 'd'} == utils.lang_parts([{'a': 'b'}, 'c', 'd'])
    assert {'a': 'b', 'c': 'd'} == utils.lang_parts([{'a': 'b'}, ('c', 'd')])
