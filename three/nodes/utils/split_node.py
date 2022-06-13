# from three.renderer.nodes import Node
from ..core.node import Node
from ..core.node_builder import vector

vectorComponents = 'xyzw'

class SplitNode(Node):

    def __init__(self, node, components = 'x') -> None:
        super().__init__()

        self.node = node
        self.components = components

    def getVectorLength(self):
        vectorLength = len(self.components)
        for c in self.components:
            index = vector.index(c) if c in vector else -1
            vectorLength = max(index + 1, vectorLength)
            
        return vectorLength
    
    def getNodeType( self, builder, *args ):

        return builder.getTypeFromLength( len(self.components) )


    def generate( self, builder, output ):
        node = self.node
        nodeTypeLength = builder.getTypeLength( node.getNodeType( builder ) )
        
        snippet = None

        if nodeTypeLength > 1:
            components = self.components
            type = None

            if len(components) >= nodeTypeLength:
                # needed expand the input node
                type = builder.getTypeFromLength(self.getVectorLength())

            nodeSnippet = node.build( builder, type )
            # return f'{nodeSnippet}.{self.components}'
            if len(self.components) == nodeTypeLength and self.components == vectorComponents[:len(self.components)]:
                # unecessary swizzle
                snippet = builder.format(nodeSnippet, type, output)
            else:
                snippet = builder.format(f'{nodeSnippet}.{self.components}', self.getNodeType(builder), output)


        else:
            # ignore components if node is a float
            snippet = node.build(builder)

        return snippet