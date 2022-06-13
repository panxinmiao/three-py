# from three.renderer.nodes import Node
from ..core.temp_node import TempNode

class JoinNode(TempNode):

    def __init__(self, nodes = []) -> None:
        super().__init__()
        self.nodes = nodes

    def getNodeType( self, builder, *args ):
        count = 0
        for node in self.nodes:
            count += builder.getTypeLength( node.getNodeType( builder ) )

        return builder.getTypeFromLength( count )

    def generate( self, builder, output ):
        type = self.getNodeType( builder )
        snippetValues = []
        for input in self.nodes:
            inputSnippet = input.build( builder)
            snippetValues.append( inputSnippet )

        snippet = f"{ builder.getType( type ) }( { ', '.join( snippetValues ) } )"

        return builder.format(snippet, type, output)

