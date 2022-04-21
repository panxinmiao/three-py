#from three.renderer.nodes import Node
from .node import Node

class BypassNode(Node):

    def __init__(self, returnNode, callNode) -> None:
        super().__init__()

        self.outputNode = returnNode
        self.callNode = callNode

    
    def getNodeType( self, builder ):
        return self.outputNode.getNodeType( builder )


    def generate( self, builder, output ):
        snippet = self.callNode.build( builder, 'void' )
        
        if snippet:
            builder.addFlowCode( snippet )

        return self.outputNode.build( builder, output )
