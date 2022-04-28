from ..core.uniform_node import UniformNode
from ..core.constants import NodeUpdateType
import math

Log2E = math.log2(math.e)

class MaxMipLevelNode(UniformNode):

    def __init__(self, texture) -> None:
        super().__init__(0)

        self.texture = texture
        self.updateType = NodeUpdateType.Frame

    
    def update(self):

        image = self.texture.images[0] if self.texture.images else self.texture.image

        width = image.width
        height = image.height

        self.value = math.log( max( width, height ) ) * Log2E

        if self.value > 0:
            self.updateType = NodeUpdateType.NONE