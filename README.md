# Minecraft Resource Generator

This is a python module aimed to enable simple generation of the many json files that are required for Minecraft modding.

### Pack Format

Updates of this tool will track the latest pack format (`pack_format` in a resource pack) as soon as possible. In order to generate resources compliant with a specific pack format, the latest version can be found below

Pack Format | Minecraft Version Range | Latest mcresources Version
---|---|---
6 | 1.16.2 - Latest | Latest
5 | 1.15 - 1.16.1 | 1.3.3
4 | 1.13 - 1.14.4 | 0.0.2

---
### Usage

mcresources can build many common files that are required for modding, and provide utilities to manage a larger project. The following is an outline of the various methods and how to use them in the most efficient manner.

All files generated by mcresources will have a comment (`'__comment__'`) inserted to identify them. This also allows mcresources via the usage of `clean_generated_resources()` to delete all files that have been generated, allowing the user to see which ones are created manually, and/or manage updating older files to a newer configuration

A few elements are common to multiple methods:
 - `name_parts`: This represents the resource location for a specific block or item. It can be specified as a string, i.e. `'block_ruby_ore'`, or as a list or tuple if the block uses directories as separators. This means that `('ore_blocks', 'ruby')` corresponds to the resource location `modid:ore_blocks/ruby`, and the resulting file `ruby.json` would be found in `modid/blockstates/ore_blocks/`. An optional domain can also be specified (`minecraft:stone`), which will override the `ResourceManager`s domain if present.

 - `conditions`: A single condition can either be specified as a fully specified dictionary (which will be inserted into the json verbatim), or as a string, which will be expanded to `{ 'type': string_condition }`
 
 - `item stacks`: An item stack can be specified as a fully specified dictionary (which will be inserted into the json verbatim), or as a string. As a string, it must represent an item resource location, i.e. `minecraft:golden_boots` will create the json `{ 'item': 'minecraft:golden_boots' }`. Additionally, you can prefix the string with `tag!` to specify that it represents a tag, i.e. `tag!forge:rods/wooden` will create the json `{ 'tag': 'forge:rods/wooden' }`

#### Contexts

When calling various `ResourceManager` methods, they will often return a context object, one of `BlockContext`, `ItemContext`, or `RecipeContext`. This object can be used as a shortcut to add other files for a single block or item, for instance, adding a blockstate, model, item block model, and loot table with only specifying the name once:
```
rm.blockstate(...).with_item_block_model(...).with_block_model(...)
```

Contexts can also be obtained directly by calling `block(name_parts)`, or `item(name_parts)`.

In addition, this delegated behavior also applies to tags. Tags no longer create single files every time the relevant `tag` method is called. Instead, they accumulate tag entries in a buffer, allowing multiple `tag` calls to append entries to a single tag.

In order to finalize tag (and lang / translation) entries, a call to `ResourceManager#flush` is necessary, which will clear the current buffer for tags and translation entries and write all relevant files.

#### Factory Methods

For common minecraft block models (slabs, stairs, etc.), there are a number of factory methods which can be used to produce vanilla style blockstates and models for a single block. These make standard assumptions about the parent block's textures and state properties. Currently, there are the following:

All of these methods take the form of a `make_[block type]` method that can be invoked on a `BlockContext`. For instance,

```
rm.block('myblock').make_slab()
```

These create the required block state, block and item models, adhering to vanilla style naming conventions and using vanilla base models. Thus adding standard block assets for wood or stone variants can be done simply.

The following methods are available:
 - `make_slab()`
 - `make_stairs()`
 - `make_fence()`
 - `make_fence_gate()`
 - `make_wall()`
 - `make_door()`
 - `make_trapdoor()`
 - `make_button()`
 - `make_pressure_plate()`

#### Resource Generators

##### Blockstates
```
blockstate(name_parts, model = None, variants = None, use_default_model = True)
```
 - `name_parts` specifies the block resource location, as seen above
 - `model` specifies the model. If not present, it will default to `modid:block/name/parts`, meaning `blockstate('pink_grass')` will create the file `modid/blockstates/pink_grass.json`, which has a model of `modid:block/pink_grass`
 - `variants` specifies the variants as found in the json file. It should be a dictionary as per usual minecraft blockstate files. If it isn't present, it will default to an empty / single variant block: `'variants': { '': model }`. If present, each variant that does not specify a model will take the default model, unless `use_default_model` is false.

```
blockstate_multipart(name_parts, parts)
```
 - `name_parts` specifies the block resource location, as seen above
 - `parts` specifies the parts. It must be a sequence of part elements. Each part element can be a dictionary (which will be expanded as `{'apply': part}`), or a pair of a `when` and `apply` data, which will be expanded as `{'when': part[0], 'apply': part[1]}`

##### Block Models
```
block_model(name_parts, textures = None, parent = 'block/cube_all', loader = None)
```
 - `name_parts` specifies the block resource location, as seen above
 - `textures` specifies the textures for this specific model. If it is a string, it will create the json: `'textures': { 'texture': textures }`. If provided as a dictionary, it will insert `'textures': textures`
 - `parent` specifies the parent model file
 - `loader` is an optional specification for forge provided custom loaders.

##### Item Models
```
item_model(name_parts, textures, parent = 'item/generated', no_textures = False, loader = None)
```
 - `name_parts` specifies the item resource location, as seen above
 - `textures` specifies the textures. If textures are supplied as strings, i.e. `'base_layer', 'middle_layer' ...`, it will assign them sequentially to layers, i.e. `{ 'layer0': 'base_layer', 'layer1': 'middle_layer' ... }`. If a dictionary is provided, it will insert those in the same way as the block model
 - `parent` specifies the parent model file
 - `no_textures`, if true, will cause the model to have no textures element
 - `loader` is an optional specification for forge provided custom loaders.


##### Loot Tables
```
block_loot(name_parts, loot_pools):
```
 - `name_parts` specifies the block resource location, as seen above.
 - `loot_pools` specifies the contents of the loot table. 
 - If `loot_pools` is passed in as a list or tuple, it will attempt to create a pool for each entry in the tuple. 
 - It can also be passed in as a string or dict, in which case it will create one pool from that input.
 - The simplest loot pool is a string, i.e. `'minecraft:dirt'`, which will create a pool with one entry of type item
        with the value of `'minecraft:dirt'`, with one roll, and the default condition (`'minecraft:survives_explosion'`)
 - If a loot pool is a dict, it will look for each possible element of a pool entry, and try to populate them
        accordingly.
   - `entries` can be a dict or a string. A string will expand to `'type': 'minecraft:item'`
   - `conditions` can be a list, tuple, dict, or string. A string will expand to `{'condition': value}`. A dict will be inserted as raw json.
   - `functions` can be a list, tuple, dict, or string. A string will expand to `{'function': value}` A dict will be inserted as raw json.
   `rolls` will be inserted as raw json. If not present, it will default to `'rolls': 1`
   `children`, `name`, `bonus_rolls`, `weight`, and `quality` will be inserted as raw json if present

In addition, the `loot_tables` module has several helper methods for common loot table related functions. For example:

 - `loot_tables.set_count(min, max, distribution)` generates an instance of the `minecraft:set_count` function.
 - `loot_tables.fortune_bonus(multiplier)` generates an instance of the `minecraft:apply_bonus`, with a standard fortune modifier.


##### Shapeless Crafting Recipes
```
crafting_shapeless(name_parts, ingredients, result, group = None, conditions = None)
```
 - `name_parts` specifies the recipe resource location. Note crafting recipes are automatically added to `modid/data/recipes`
 - `inredients` specifies the ingredients. It must be either a list / tuple of item stacks, or a string or dictionary representing an item stack. See above for valid item stack specifications.
 - `result` specifies the recipe result or output. It must be a single item stack
 - `group` specifies the group the recipe belongs to
 - `conditions` specifies any conditions on the recipe being enabled. It must be a list / tuple of valid condition identifiers, or a string or dictionary representing an item stack

##### Shaped Crafting Recipes
```
crafting_shaped(name_parts, pattern, ingredients, result, group = None, conditions = None)
```
 - `name_parts` specifies the recipe resource location. Note crafting recipes are automatically added to `modid/data/recipes`
 - `pattern` specifies the pattern. It must be a list of strings, i.e. `['XXX', ' S ', ' S ']` for a pickaxe pattern. The keys must be the same as used in the ingredients field.
 - `inredients` specifies the ingredients. It can be a dictionary of single character keys to item stacks, or it can be a single item stack (which will default to the first key found, and as such should only be used if there is only one unique input)
 - `result` specifies the recipe result or output. It must be a single item stack
 - `group` is as above
 - `conditions` is as above

##### Other Recipes or Data
```
recipe(name_parts, type_in, data_in, group, conditions = None)
data(name_parts, data_in)
```
This is used to create modded recipes that are loaded via custom deserializers. As such, `name_parts` needs to include a subdirectory for the recipe type
 - `name_parts` specifies the recipe resource location.
 - `type_in` specifies the recipe type
 - `data_in` specifies the json data to be inserted into the recipe
 - `group` is as above
 - `conditions` is as above

##### Tags
```
item_tag(name_parts, *values, replace = False)
block_tag(name_parts, *values, replace = False)
fluid_tag(name_parts, *values, replace = False)
entity_tag(name_parts, *values, replace = False)
```
These are used to create item and block tags respectively
 - `name_parts` specifies the tag resource location, as seen above
 - `values` specifies the values. It can be a single string for one value, or a list / tuple of strings for multiple values
 - `replace` specifies the replace field in the json, i.e. if the tag should replace a previous identical entry

#### World Generation

New in Minecraft 1.16.2 is the ability to specify all manner of world generation objects. These follow very similar "type-and-config" patterns, and have quite nested structures meaning the data generation for them is a bit different.

In general, builders for the data inside world gen objects can be found in `world_gen`. These can be nested for any purpose, and the result can be fed to `rm.carver`, `rm.feature`, or `rm.surface_builder` to create configured carvers, configured features, or configured surface builders respectively.

Biomes are possible with `rm.biome`, which takes *a lot* of default arguments, and will populate any missing fields to the required ones for a biome. This also does no interpolation, so anything passed in must be specfied as it should appear in the final result json.