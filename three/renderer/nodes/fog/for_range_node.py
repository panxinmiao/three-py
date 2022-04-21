from .fog_node import FogNode
from ..shader.shader_node_elements import smoothstep, negate, positionView

class FogRangeNode(FogNode):

    def __init__(self, colorNode, nearNode, farNode) -> None:
        super().__init__(colorNode)
        self.nearNode = nearNode
        self.farNode = farNode

    def generate( self, builder ):
        self.factorNode = smoothstep(self.nearNode, self.farNode, negate( positionView.z ) )
        return super().generate( builder )

    