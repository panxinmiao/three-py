#from three.renderer.nodes import Node, AttributeNode, VaryNode, ModelNode, MathNode, OperatorNode
from ..core.node import Node
from ..core.attribute_node import AttributeNode
from ..core.varying_node import VaryingNode
from .model_node import ModelNode
from ..math.operator_node import OperatorNode
from ..math.math_node import MathNode

class PositionNode(Node):
    GEOMETRY = 'geometry'
    LOCAL = 'local'
    WORLD = 'world'
    WORLD_DIRECTION = 'worldDirection'
    VIEW = 'view'
    VIEW_DIRECTION = 'viewDirection'

    def __init__(self, scope = LOCAL ) -> None:
        super().__init__('vec3')
        self.scope = scope

    def getHash(self, builder):
        return f'position-{self.scope}'

    def generate(self, builder ):
        scope = self.scope
        outputNode = None
        
        if scope == PositionNode.GEOMETRY:
            outputNode = AttributeNode( 'position', 'vec3' )

        elif scope == PositionNode.LOCAL:
            outputNode = VaryingNode( PositionNode( PositionNode.GEOMETRY ) )

        elif scope == PositionNode.WORLD:
            #vertexPositionNode = transformDirection.call( { 'dir': PositionNode( PositionNode.LOCAL ), 'matrix': ModelNode( ModelNode.WORLD_MATRIX ) } )
            vertexPositionNode = MathNode( MathNode.TRANSFORM_DIRECTION, ModelNode( ModelNode.WORLD_MATRIX ), PositionNode( PositionNode.LOCAL ) )
            outputNode = VaryingNode( vertexPositionNode )

        elif scope == PositionNode.VIEW:
            vertexPositionNode = OperatorNode( '*', ModelNode( ModelNode.VIEW_MATRIX ), PositionNode( PositionNode.LOCAL ) )
            outputNode = VaryingNode( vertexPositionNode )

        elif scope == PositionNode.VIEW_DIRECTION:
            vertexPositionNode = MathNode( MathNode.NEGATE, PositionNode( PositionNode.VIEW ) )
            outputNode = MathNode( MathNode.NORMALIZE, VaryingNode( vertexPositionNode ) )
        
        elif scope == PositionNode.WORLD_DIRECTION:
            vertexPositionNode = MathNode( MathNode.NEGATE, PositionNode( PositionNode.WORLD ) )
            outputNode = MathNode( MathNode.NORMALIZE, VaryingNode( vertexPositionNode ) )

        return outputNode.build( builder, self.getNodeType( builder ) )
