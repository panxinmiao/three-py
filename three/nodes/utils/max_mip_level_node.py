from ..core.uniform_node import UniformNode
from ..core.constants import NodeUpdateType
import math

class MaxMipLevelNode(UniformNode):

    def __init__(self, textureNode) -> None:
        super().__init__(0)

        self.textureNode = textureNode 
        self.updateType = NodeUpdateType.Frame

    @property
    def texture(self):
        return self.textureNode.value

    def update(self, *args):

        # images = self.texture.images
        # image = (images[0].image or images[0]) if images and len(images) > 0 else self.texture.image

        texture = self.texture
        images = texture.images
        image = (images[0].image or images[0]) if images and len(images) > 0 else texture.image

        if image:
            width = image.width
            height = image.height

            self.value = math.log2( max( width, height ) ) 