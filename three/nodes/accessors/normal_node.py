#from three.renderer.nodes import Node, AttributeNode, VaryNode, OperatorNode, MathNode, ModelNode, CameraNode

from ..core.node import Node
from ..core.attribute_node import AttributeNode
from ..core.varying_node import VaryingNode
from ..math.math_node import MathNode
from ..math.operator_node import OperatorNode
from .model_node import ModelNode
from .camera_node import CameraNode

class NormalNode(Node):
    GEOMETRY = 'geometry'
    LOCAL = 'local'
    VIEW = 'view'
    WORLD = 'world'

    def __init__(self, scope = LOCAL ) -> None:
        super().__init__(nodeType='vec3')
        self.scope = scope

    def getHash(self, builder):
        return f'normal-{self.scope}'

    def generate( self, builder ):
        scope = self.scope
        outputNode = None

        if scope == NormalNode.GEOMETRY:
            outputNode = AttributeNode( 'normal', 'vec3' )
        elif scope == NormalNode.LOCAL:
            outputNode = VaryingNode( NormalNode( NormalNode.GEOMETRY ) )
        elif scope == NormalNode.VIEW:
            vertexNode = OperatorNode( '*', ModelNode( ModelNode.NORMAL_MATRIX ), NormalNode( NormalNode.LOCAL ) )
            outputNode = MathNode( MathNode.NORMALIZE, VaryingNode( vertexNode ) )
        elif scope == NormalNode.WORLD:
            
            #vertexNormalNode = inverseTransformDirection.call( { 'dir': NormalNode( NormalNode.VIEW ), 'matrix': CameraNode( CameraNode.VIEW_MATRIX ) } )
            # To use INVERSE_TRANSFORM_DIRECTION only inverse the param order like this: MathNode( ..., Vector, Matrix );

            vertexNode = MathNode( MathNode.TRANSFORM_DIRECTION, NormalNode( NormalNode.VIEW ), CameraNode( CameraNode.VIEW_MATRIX ) )
            outputNode = MathNode( MathNode.NORMALIZE, VaryingNode( vertexNode ) )

        return outputNode.build( builder, self.getNodeType( builder ) )

