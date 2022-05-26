from mcresources import surface_rules


def test_block_rule():
    assert surface_rules.block('minecraft:dirt') == {
        'type': 'minecraft:block',
        'result_state': {
            'Name': 'minecraft:dirt',
            'Properties': {}
        }
    }


def test_sequence_rule():
    assert surface_rules.sequence(
        surface_rules.block('minecraft:dirt'),
        surface_rules.block('minecraft:stone')
    ) == {
        'type': 'minecraft:sequence',
        'sequence': [
            {
                'type': 'minecraft:block',
                'result_state': {'Name': 'minecraft:dirt', 'Properties': {}}
            },
            {
                'type': 'minecraft:block',
                'result_state': {'Name': 'minecraft:stone', 'Properties': {}}
            }
        ]
    }


def test_condition_rule():
    assert surface_rules.condition({'test': 'thing'}, {'rule': 'next'}) == {
        'type': 'minecraft:condition',
        'if_true': {
            'test': 'thing'
        },
        'then_run': {
            'rule': 'next'
        }
    }