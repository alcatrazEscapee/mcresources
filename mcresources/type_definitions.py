
from typing import Dict, Union, Sequence, Tuple, NamedTuple, Literal, TypeVar

# Generics
T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')
DefaultValue = TypeVar('DefaultValue')
MapValue = TypeVar('MapValue')

# Json
JsonObject = Dict[str, 'Json']
Json = Union[JsonObject, Sequence['Json'], str, int, bool, None]

# Util

class ResourceLocation(NamedTuple('ResourceLocation', domain=str, path=str)):

    def join(self, prefix: str = '', simple: bool = False) -> str:
        if simple and self.domain == 'minecraft':
            return prefix + self.path
        else:
            return self.domain + ':' + prefix + self.path


ResourceIdentifier = Union[ResourceLocation, Sequence[str], str]


# Minecraft
TypeWithOptionalConfig = Union[ResourceIdentifier, Tuple[ResourceIdentifier, Json]]

VerticalAnchorType = Literal['absolute', 'above_bottom', 'below_top']
VerticalAnchor = Union[Tuple[VerticalAnchorType, int], Tuple[VerticalAnchorType, int], Dict[str, int], int]
