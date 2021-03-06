from .node import Node
from three.structure import Dict

class ContextNode(Node):

    isContextNode = True

    def __init__(self, node, context=None) -> None:
        super().__init__()
        self.node = node
        self.context = Dict(context) if context else Dict()

    def getNodeType( self, builder , *args ):
        return self.node.getNodeType( builder )

    def construct(self, builder):
        previousContext = builder.getContext()
        builder.setContext({**builder.context, **self.context})
        node = self.node.build(builder)

        builder.setContext(previousContext)

        return node

    def generate( self, builder, output ):

        previousContext = builder.getContext()
        builder.setContext( {**builder.context, **self.context} )
        snippet = self.node.build( builder, output )
        builder.setContext( previousContext )
        
        return snippet

