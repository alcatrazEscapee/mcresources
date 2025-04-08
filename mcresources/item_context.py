from mcresources.type_definitions import Json, ResourceLocation
from mcresources import utils

from typing import Optional, Sequence


class ItemContext:
    """
    Contextual information about an item, used to simplify similar json calls
    """

    def __init__(self, rm, res: ResourceLocation):
        self.rm = rm
        self.res: ResourceLocation = res

    def with_item_model(self, *textures: Json, parent: str = 'item/generated', no_textures: bool = False, overrides: list[Json] = None) -> 'ItemContext':
        """
        Shortcut for {@link ResourceManager#item_model}
        :param textures: the textures for the model. Defaults to 'domain:item/name/parts'
        :param parent: the parent model.
        :param no_textures: if the textures element should be ignored
        :param overrides: overrides to add to the item model if present
        """
        self.rm.item_model(self.res, *textures, parent=parent, no_textures=no_textures, overrides=overrides)
        return self

    def with_tag(self, tag_name_parts: Sequence[str] = None, replace: bool = None) -> 'ItemContext':
        """
        Shortcut for {@link ResourceManager#item_tag}
        :param tag_name_parts: The resource location for the tag
        :param replace: If the tag should replace previous values
        """
        if tag_name_parts is None:
            tag_name_parts = self.res
        tag_res = utils.resource_location(self.rm.domain, tag_name_parts)
        self.rm.item_tag(tag_res, self.res, replace=replace)
        return self

    def with_lang(self, item_name: str, language: Optional[str] = None) -> 'ItemContext':
        """
        Shortcut for {@link ResourceManager#lang} with the item name
        """
        self.rm.lang(('item.%s.%s' % self.res).replace('/', '.'), item_name, language=language)
        return self
