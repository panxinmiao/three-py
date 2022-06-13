from ..core.uniform_node import UniformNode
from ..core.constants import NodeUpdateType
import math


class MaxMipLevelNode(UniformNode):

    def __init__(self, texture) -> None:
        super().__init__(0)

        self.texture = texture
        self.updateType = NodeUpdateType.Frame

    
    def update(self, *args):

        image = (self.texture.images[0].image or self.texture.images[0]) if self.texture.images and len(
            self.texture.images) > 0 else self.texture.image

        if image:
            width = image.width
            height = image.height

            self.value = math.log2( max( width, height ) ) 