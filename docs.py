from mcresources import *
from mcresources.type_definitions import *

from github_wiki_pydoc import makedoc, page, typedef

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
        typedef(Json, 'Json'),
        typedef(JsonObject, 'JsonObject'),
        typedef(ResourceIdentifier, 'ResourceIdentifier'),
    ),
    link_root='https://github.com/alcatrazEscapee/mcresources/blob/main',
    content_root='../mcresources.wiki/'
)
