# from three.renderer.nodes import Node
from ..core.node import Node

class SplitNode(Node):

    def __init__(self, node, components = 'x') -> None:
        super().__init__()

        self.node = node
        self.components = components

    
    def getNodeType( self, builder, *args ):

        return builder.getTypeFromLength( len(self.components) )


    def generate( self, builder ):
        node = self.node
        nodeTypeLength = builder.getTypeLength( node.getNodeType( builder ) )
        
        if nodeTypeLength > 1:
            components = self.components
            type = None

            if len(components) >= nodeTypeLength:
                # need expand the input node
                type = self.getNodeType( builder )

            nodeSnippet = node.build( builder, type )
            return f'{nodeSnippet}.{self.components}'

        else:
            # ignore components if node is a float
            return node.build( builder )
