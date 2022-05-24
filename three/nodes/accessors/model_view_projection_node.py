#from three.renderer.nodes import Node, OperatorNode, CameraNode, ModelNode, PositionNode
from ..core.node import Node
from .camera_node import CameraNode
from .model_node import ModelNode
from .position_node import PositionNode
from ..math.operator_node import OperatorNode

class ModelViewProjectionNode(Node):

    def __init__(self, position = None) -> None:
        super().__init__(nodeType = 'vec4')
        self.position = position or PositionNode()

    def generate(self, builder ):
        position = self.position

        mvpMatrix = OperatorNode( '*', CameraNode( CameraNode.PROJECTION_MATRIX ), ModelNode( ModelNode.VIEW_MATRIX ) )
        mvpNode = OperatorNode( '*', mvpMatrix, position )
        
        return mvpNode.build( builder )


