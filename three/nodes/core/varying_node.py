#from three.renderer.nodes import Node, NodeBuilder, NodeShaderStage

from .node import Node
from .node_builder import NodeBuilder
from .constants import NodeShaderStage

class VaryingNode(Node):
    def __init__(self, node, name = None) -> None:
        super().__init__()
        self.node = node
        self.name = name

    def getHash( self, builder ):
        if self.name:
            return self.name
        else:
            return super().getHash( builder )

    def getNodeType( self, builder:'NodeBuilder' , *args ):

        # VaryingNode is auto type
        return self.node.getNodeType( builder )

    def generate( self, builder:'NodeBuilder' ):
        type = self.getNodeType( builder )
        node = self.node
        name = self.name
        
        nodeVarying = builder.getVaryingFromNode( self, type )

        if name is not None :
            nodeVarying.name = name

        propertyName = builder.getPropertyName( nodeVarying, NodeShaderStage.Vertex)

        # force nodeVary.snippet work in vertex stage
        builder.flowNodeFromShaderStage( NodeShaderStage.Vertex, node, type, propertyName )

        return builder.getPropertyName( nodeVarying )

