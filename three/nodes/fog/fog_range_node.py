from .fog_node import FogNode
from ..shadernode.shader_node_base_elements import smoothstep, negate, positionView

class FogRangeNode(FogNode):

    isFogRangeNode = True

    def __init__(self, colorNode, nearNode, farNode) -> None:
        super().__init__(colorNode)
        self.nearNode = nearNode
        self.farNode = farNode

    def construct( self, *args ):
        self.factorNode = smoothstep(self.nearNode, self.farNode, negate( positionView.z ) )
