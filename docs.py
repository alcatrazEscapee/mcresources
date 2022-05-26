from mcresources import *
from mcresources.type_definitions import *

from github_wiki_pydoc import makedoc, page, typedef

import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(levelname)s : %(message)s')


makedoc(
    pages=(
        page('ResourceManager.md', ResourceManager),
        page('BlockContext.md', BlockContext),
        page('ItemContext.md', ItemContext),
        page('RecipeContext.md', RecipeContext),
        page('loot_tables.md', loot_tables),
        page('block_states.md', block_states),
        page('advancements.md', advancements),
        page('utils.md', utils),
    ),
    types=(
        typedef('Json', Json),
        typedef('JsonObject', JsonObject),
        typedef('ResourceIdentifier', ResourceIdentifier),
        typedef('T', T),
        typedef('K', K),
        typedef('V', V),
        typedef('DefaultValue', DefaultValue),
        typedef('MapValue', MapValue)
    ),
    link_root='https://github.com/alcatrazEscapee/mcresources/blob/main',
    content_root='../mcresources.wiki/',
    home_doc="""
Wiki for `mcresources`, a resource generation library for Minecraft modding. This wiki is generated from the documentation in the mcresources repository
""".strip()
)
