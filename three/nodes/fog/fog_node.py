from ..core.node import Node
from ..math.math_node import MathNode

class FogNode(Node):

    isFogNode = True

    def __init__(self, colorNode, factorNode = None) -> None:
        super().__init__('float')

        self.colorNode = colorNode
        self.factorNode = factorNode

    def mix( self, outputNode ):
        return MathNode( MathNode.MIX, outputNode, self.colorNode, self )


    def generate( self, builder ):
        return self.factorNode.build( builder, 'float' )