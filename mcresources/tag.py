#  Part of mcresources by Alex O'Neill
#  Work under copyright. Licensed under MIT
#  For more information see the project LICENSE file

from typing import Sequence, List


class Tag:
    """
    Wrapper around a tag entry
    """

    def __init__(self, name_parts: Sequence[str], replace: bool, values: List[str]):
        self.name_parts: Sequence[str] = name_parts
        self.replace: bool = replace
        self.values: List[str] = values
