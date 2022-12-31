#from three.renderer.nodes import Node, NodeUpdateType, Matrix3Node, Matrix4Node, Vector3Node

from ..core.node import Node
from ..core.uniform_node import UniformNode
from ..core.constants import NodeUpdateType
import three

class Object3DNode(Node):

    VIEW_MATRIX = 'viewMatrix'
    NORMAL_MATRIX = 'normalMatrix'
    WORLD_MATRIX = 'worldMatrix'
    POSITION = 'position'
    VIEW_POSITION = 'viewPosition'
    DIRECTION = 'direction'

    def __init__(self, scope = VIEW_MATRIX, object3d = None) -> None:
        super().__init__()
        self.scope = scope
        self.object3d = object3d

        self.updateType = NodeUpdateType.Object

        self._uniformNode = UniformNode( None )

    
    def getNodeType(self, *args):
        scope = self.scope

        if scope == Object3DNode.WORLD_MATRIX or scope == Object3DNode.VIEW_MATRIX:
            return 'mat4'

        elif scope == Object3DNode.NORMAL_MATRIX:
            return 'mat3'

        elif scope == Object3DNode.POSITION or scope == Object3DNode.VIEW_POSITION or scope == Object3DNode.DIRECTION:
            return 'vec3'


    def update(self, frame ):
        object:'three.Object3D' = self.object3d
        uniformNode = self._uniformNode
        scope = self.scope

        if scope == Object3DNode.VIEW_MATRIX:
            uniformNode.value = object.modelViewMatrix

        elif scope == Object3DNode.NORMAL_MATRIX:
            uniformNode.value = object.normalMatrix

        elif scope == Object3DNode.WORLD_MATRIX:
            uniformNode.value = object.matrixWorld

        elif scope == Object3DNode.POSITION:
            # uniformNode.value = uniformNode.value or three.Vector3()
            uniformNode.value.setFromMatrixPosition( object.matrixWorld )
        
        elif scope == Object3DNode.DIRECTION:
            uniformNode.value = uniformNode.value or three.Vector3()
            object.getWorldDirection( uniformNode.value )

        elif scope == Object3DNode.VIEW_POSITION:
            camera = frame.camera
            uniformNode.value = uniformNode.value or three.Vector3()
            uniformNode.value.setFromMatrixPosition( object.matrixWorld )
            uniformNode.value.applyMatrix4( camera.matrixWorldInverse )


    def generate( self, builder ):

        scope = self.scope

        if scope == Object3DNode.WORLD_MATRIX or scope == Object3DNode.VIEW_MATRIX :
            self._uniformNode.nodeType = 'mat4'

        elif scope == Object3DNode.NORMAL_MATRIX :
            self._uniformNode.nodeType = 'mat3'

        elif scope == Object3DNode.POSITION or scope == Object3DNode.VIEW_POSITION or scope == Object3DNode.DIRECTION:
            self._uniformNode.nodeType = 'vec3'

        return self._uniformNode.build( builder )
    
