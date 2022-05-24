from .node import Node
from three.structure import Dict

class ContextNode(Node):
    def __init__(self, node, context=None) -> None:
        super().__init__()
        self.node = node
        self.context = Dict(context) if context else Dict()

    def getNodeType( self, builder , *args ):
        return self.node.getNodeType( builder )

    def generate( self, builder, output ):

        previousContext = builder.getContext()

        builder.setContext( {**builder.context, **self.context} )

        snippet = self.node.build( builder, output )
        builder.setContext( previousContext )
        
        return snippet

