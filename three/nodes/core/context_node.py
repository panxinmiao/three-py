#from three.renderer.nodes import Node
from .node import Node
from three.structure import Dict

class ContextNode(Node):
    def __init__(self, node, context=None) -> None:
        super().__init__()
        self.node = node
        self.context = context or Dict()

    # def setContextValue(self, name, value ):
    #     self.context[ name ] = value
    #     return self

    # def getContextValue( self, name ):
    #     return self.context[ name ]

    def getNodeType( self, builder , *args ):
        return self.node.getNodeType( builder )

    def generate( self, builder, output ):

        previousContext = builder.getContext()

        builder.setContext( {**builder.context, **self.context} )

        snippet = self.node.build( builder, output )
        builder.setContext( previousContext )
        
        return snippet

