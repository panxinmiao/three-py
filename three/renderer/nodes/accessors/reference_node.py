#from three.renderer.nodes import Node, NodeUpdateType, FloatNode, Vector2Node, Vector3Node, Vector4Node, ColorNode, TextureNode

from ..core.node import Node
from ..core.uniform_node import UniformNode
from ..core.constants import NodeUpdateType

class ReferenceNode(Node):

    def __init__(self, property, uniformType, object = None) -> None:
        super().__init__()

        self.property = property
        self.uniformType = uniformType

        self.object = object

        self.node = None
        self.updateType = NodeUpdateType.Object
        self.setNodeType( uniformType )

    
    def setNodeType( self, uniformType ):
        self.node = UniformNode( None, uniformType )
        self.nodeType = uniformType

        if uniformType == 'color':
            self.nodeType = 'vec3'

        elif uniformType == 'texture':
            self.nodeType = 'vec4'


    def getNodeType( self, *args ):
        return self.uniformType

    def update( self, frame ):
        object = self.object if self.object else frame.object
        # value = object[ self.property ]
        value = getattr(object, self.property)
        self.node.value = value

    def generate( self, builder ):
        return self.node.build( builder, self.getNodeType( builder ) )
