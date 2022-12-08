from .fog_node import FogNode
from ..shadernode.shader_node_base_elements import sub, exp, mul, negate, positionView

class FogExp2Node(FogNode):

    isFogExp2Node = True

    def __init__(self, colorNode, densityNode) -> None:
        super().__init__(colorNode)

        self.densityNode = densityNode

    def construct(self, builder):
        depthNode = negate( positionView.z )
        densityNode = self.densityNode

        self.factorNode = sub( 1.0, exp( mul( negate( densityNode ), densityNode, depthNode, depthNode ) ) )

