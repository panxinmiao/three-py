#from three.renderer.nodes import Node

from ..core.node import Node

class ConvertNode(Node):
    def __init__(self, node, convertTo ) -> None:
        super().__init__()
        self.node = node
        self.convertTo = convertTo

    def getNodeType( self, *args):
        return self.convertTo

    def generate( self, builder ):
        convertTo = self.convertTo
        node = self.node

        # convertToSnippet = builder.getType( convertTo )
        # nodeSnippet = self.node.build( builder, convertTo )

        if builder.isReference( convertTo ) == False:
            # convertToSnippet = builder.getType( convertTo )
            nodeSnippet = node.build( builder, convertTo )

            #return f'{ builder.getVectorType( convertToSnippet ) }( { nodeSnippet } )'
            return builder.format( nodeSnippet, self.getNodeType( builder ), convertTo )
        else:
            return node.build( builder, convertTo )

