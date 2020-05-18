#  Part of mcresources by Alex O'Neill
#  Work under copyright. Licensed under MIT
#  For more information see the project LICENSE file

from typing import Dict, Any


class BlockModel:

    @staticmethod
    def slab_model(texture: str) -> Dict[str, Any]:
        return {
            'bottom': texture,
            'top': texture,
            'side': texture
        }
