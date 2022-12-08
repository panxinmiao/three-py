import math
from ..core.node import Node
from ..shadernode.shader_node_base_elements import add, mul, div, log2, clamp, maxMipLevel

class SpecularMipLevelNode(Node):

    def __init__(self, textureNode, roughnessNode=None) -> None:
        super().__init__('float')

        self.textureNode = textureNode
        self.roughnessNode = roughnessNode

    def construct(self, *args):

        # http://casual-effects.blogspot.ca/2011/08/plausible-environment-lighting-in-two.html
        maxMipLevelScalar = maxMipLevel(self.textureNode)

        sigma = div(mul(math.pi, mul(self.roughnessNode, self.roughnessNode)), add(1.0, self.roughnessNode))
        desiredMipLevel = add(maxMipLevelScalar, log2(sigma))

        return clamp(desiredMipLevel, 0.0, maxMipLevelScalar)
