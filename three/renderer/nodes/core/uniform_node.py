from .input_node import InputNode
from .node_builder import NodeBuilder

class UniformNode(InputNode):
    def getUniformHash( self, builder:'NodeBuilder' ):
        return self.getHash( builder )

    def generate( self, builder:'NodeBuilder', output ):
        type = self.getNodeType( builder )
        hash = self.getUniformHash( builder )
        sharedNode = builder.getNodeFromHash( hash )

        if sharedNode is None:
            builder.setHashNode( self, hash )
            sharedNode = self

        sharedNodeType = sharedNode.getInputType( builder )

        nodeUniform = builder.getUniformFromNode( sharedNode, builder.shaderStage, sharedNodeType )
        propertyName = builder.getPropertyName( nodeUniform )

        return builder.format( propertyName, type, output )