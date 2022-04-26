# from three.renderer.nodes import Node
from ..core.node import Node

class JoinNode(Node):

    def __init__(self, nodes = []) -> None:
        super().__init__()
        self.nodes = nodes

    def getNodeType( self, builder, *args ):
        count = 0
        for node in self.nodes:
            count += builder.getTypeLength( node.getNodeType( builder ) )

        return builder.getTypeFromLength( count )

    def generate( self, builder ):
        type = self.getNodeType( builder )
        snippetValues = []
        for input in self.nodes:
            inputSnippet = input.build( builder)
            snippetValues.append( inputSnippet )

        return f"{ builder.getType( type ) }( { ', '.join( snippetValues ) } )"

