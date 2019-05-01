# Minecraft Resource Generator

This is a python module aimed to enable simple generation of the many json files that are required for forge modding.

Some examples from No Tree Punching 1.13 by AlcatrazEscapee:

```python
from mcresources import ResourceManager
rm = ResourceManager('notreepunching')

for stone in ['stone', 'sandstone', 'andesite', 'granite', 'diorite']:
    # Block States
    rm.blockstate(('loose_rock', stone))
    # Block Models
    rm.block_model(('loose_rock', stone), 'minecraft:block/%s' % stone, 'notreepunching:block/loose_rock')
    # Item Models
    rm.item_model(('rock', stone))
    # Crafting Recipes
    result = ('cobblestone' if stone == 'stone' else stone)
    rm.crafting_shaped('%s_from_rocks' % result, ['##', '##'], 'notreepunching:rock/%s' % stone, 'minecraft:%s' % result)

# Item Models
for tool in ['pickaxe', 'shovel', 'axe', 'hoe', 'knife']:
    rm.item_model('flint_%s' % tool, parent='item/handheld')
    
# Shaped Crafting
for metal in ['iron', 'gold', 'diamond']:
    tool_metal = 'tag!forge:' + ('gems' if metal == 'diamond' else 'ingots') + '/' + metal
    metal_prefix = metal if metal != 'gold' else 'golden'
    rm.crafting_shaped('%s_knife' % metal, ['I', 'S'], {'I': tool_metal, 'S': 'tag!forge:rods/wooden'}, 'notreepunching:%s_knife' % metal_prefix)

# More Crafting Recipes
rm.crafting_shapeless('plant_string', ['notreepunching:plant_fiber'] * 3, 'notreepunching:plant_string')
```