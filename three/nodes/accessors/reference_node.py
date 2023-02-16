from ..core.node import Node
from ..core.uniform_node import UniformNode
from ..accessors.texture_node import TextureNode
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

        if uniformType == 'texture':
            node = TextureNode( None )
        else:
            node = UniformNode( None, uniformType )

        self.node = node


    def getNodeType( self, builder ):
        return self.node.getNodeType( builder )

    def update( self, frame ):
        object = self.object if self.object else frame.object
        # value = object[ self.property ]
        value = getattr(object, self.property)
        self.node.value = value

        # print('ReferenceNode.update()', self, self.property, self.uniformType, self.object, self.node.value)

    def generate( self, builder ):
        # return self.node
        return self.node.build( builder, self.getNodeType( builder ) )
    
    def construct( self, *args ):
        return self.node
