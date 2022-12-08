from .node import Node
from .node_builder import NodeBuilder
from .constants import NodeShaderStage

class VaryingNode(Node):
    def __init__(self, node, name = None) -> None:
        super().__init__()
        self.node = node
        self.name = name
    
    def isGlobal(self, *args):
        return True

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

        # this property can be used to check if the varying can be optimized for a var
        nodeVarying.needsInterpolation = nodeVarying.needsInterpolation or builder.shaderStage == 'fragment'

        if name is not None :
            nodeVarying.name = name

        propertyName = builder.getPropertyName( nodeVarying, NodeShaderStage.Vertex)

        # force nodeVary.snippet work in vertex stage
        builder.flowNodeFromShaderStage( NodeShaderStage.Vertex, node, type, propertyName )

        return builder.getPropertyName( nodeVarying )

