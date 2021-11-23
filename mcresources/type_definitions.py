
from typing import Dict, Any, Union, Sequence, Tuple, NamedTuple

# Json
JsonObject = Dict[str, Any]
Json = Union[JsonObject, Sequence[Any], str]

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