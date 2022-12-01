from ..core.node import Node
from ..core.attribute_node import AttributeNode
from ..core.varying_node import VaryingNode
from ..math.math_node import MathNode
from ..math.operator_node import OperatorNode
from .model_node import ModelNode
from .camera_node import CameraNode
from ..utils.split_node import SplitNode

class TangentNode(Node):
    GEOMETRY = 'geometry'
    LOCAL = 'local'
    VIEW = 'view'
    WORLD = 'world'

    def __init__(self, scope = LOCAL ) -> None:
        super().__init__()
        self.scope = scope

    def getHash(self, builder):
        return f'tangent-{self.scope}'

    def getNodeType(self, *args):
        scope = self.scope
        if scope == TangentNode.GEOMETRY:
            return 'vec4'
        
        return 'vec3'
    
    def generate( self, builder ):
        scope = self.scope
        outputNode = None

        if scope == TangentNode.GEOMETRY:
            outputNode = AttributeNode( 'tangent', 'vec4' )

        elif scope == TangentNode.LOCAL:

            outputNode = VaryingNode( SplitNode( TangentNode( TangentNode.GEOMETRY ), 'xyz' ) )

        elif scope == TangentNode.VIEW:

            vertexNode = SplitNode( OperatorNode( '*', ModelNode( ModelNode.VIEW_MATRIX ), TangentNode( TangentNode.LOCAL ) ), 'xyz' )
            outputNode = MathNode( MathNode.NORMALIZE, VaryingNode( vertexNode ) )

        elif scope == TangentNode.WORLD:

            vertexNode = MathNode( MathNode.TRANSFORM_DIRECTION, TangentNode( TangentNode.VIEW ), CameraNode( CameraNode.VIEW_MATRIX ) )
            outputNode = MathNode( MathNode.NORMALIZE, VaryingNode( vertexNode ) )

        return outputNode.build( builder, self.getNodeType( builder ) )