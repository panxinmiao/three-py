from ..core.node import Node
from ..core.varying_node import VaryingNode
from ..math.math_node import MathNode
from ..math.operator_node import OperatorNode
from ..utils.split_node import SplitNode
from .normal_node import NormalNode
from .tangent_node import TangentNode

class BitangentNode(Node):
    GEOMETRY = 'geometry'
    LOCAL = 'local'
    VIEW = 'view'
    WORLD = 'world'

    def __init__(self, scope = LOCAL ) -> None:
        super().__init__('vec3')
        self.scope = scope

    def getHash(self, builder):
        return f'bitangent-{self.scope}'
    
    def generate( self, builder ):
        scope = self.scope

        crossNormalTangent = MathNode( MathNode.CROSS, NormalNode( scope ), TangentNode( scope ) )
        tangentW = SplitNode( TangentNode( TangentNode.GEOMETRY ), 'w' )
        vertexNode = SplitNode( OperatorNode( '*', crossNormalTangent, tangentW ), 'xyz' )
        outputNode = MathNode( MathNode.NORMALIZE, VaryingNode( vertexNode ) )

        return outputNode.build( builder, self.getNodeType( builder ) )