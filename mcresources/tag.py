from mcresources.type_definitions import JsonObject
from typing import List, Union


class Tag:
    """
    Wrapper around a tag entry
    """

    def __init__(self, replace: bool):
        self.replace: bool = replace
        self.values: List[Union[str, JsonObject]] = []

    def add_all(self, values: List[Union[str, JsonObject]]):
        """ Adds a list of new tag entries, but ignoring duplicates while preserving insertion order. Sadly, this means it's slower """
        for v in values:
            if v not in self.values:
                self.values.append(v)
