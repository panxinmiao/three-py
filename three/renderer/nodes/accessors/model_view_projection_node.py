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
        self._mvpMatrix = OperatorNode( '*', CameraNode( CameraNode.PROJECTION_MATRIX ), ModelNode( ModelNode.VIEW_MATRIX ) )

    # def generate(self, builder ):
    #     mvpSnipped = self._mvpMatrix.build( builder )
    #     positionSnipped = self.position.build( builder, 'vec3' )

    #     return f'( {mvpSnipped} * vec4( {positionSnipped}, 1.0 ) )'

    def generate(self, builder ):
        position = self.position

        mvpMatrix = OperatorNode( '*', CameraNode( CameraNode.PROJECTION_MATRIX ), ModelNode( ModelNode.VIEW_MATRIX ) )
        mvpNode = OperatorNode( '*', mvpMatrix, position )
        
        return mvpNode.build( builder )


