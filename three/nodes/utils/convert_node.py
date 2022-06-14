#from three.renderer.nodes import Node

from ..core.node import Node

class ConvertNode(Node):
    def __init__(self, node, convertTo ) -> None:
        super().__init__()
        self.node = node
        self.convertTo = convertTo

    def getNodeType( self, *args):
        return self.convertTo

    def generate( self, builder, output ):
        convertTo = self.convertTo
        node = self.node
        type = self.getNodeType(builder)

        # convertToSnippet = builder.getType( convertTo )
        # nodeSnippet = self.node.build( builder, convertTo )
        snippet = None

        if builder.isReference( convertTo ) == False:
            # convertToSnippet = builder.getType( convertTo )
            nodeSnippet = node.build( builder, convertTo )

            #return f'{ builder.getVectorType( convertToSnippet ) }( { nodeSnippet } )'
            snippet = builder.format(nodeSnippet, type, convertTo)
        else:
            snippet = node.build(builder, convertTo)

        return builder.format(snippet, type, output)

