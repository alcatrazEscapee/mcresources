# Imports used by the end-user package
# I still don't quite understand python packaging, and how they interact with
# package installations, but this seems to work.
#
# Don't remove these, even if they seem unused
from mcresources.resource_manager import ResourceManager

from mcresources.block_context import BlockContext
from mcresources.item_context import ItemContext
from mcresources.recipe_context import RecipeContext

from mcresources import loot_tables
from mcresources import block_states
from mcresources import advancements
from mcresources import utils
from mcresources import atlases
