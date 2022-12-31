#from three.renderer.nodes import Node
from .node import Node

class PropertyNode(Node):
    def __init__(self, nodeType, name=None) -> None:
        super().__init__(nodeType)
        self.name = name

    def getHash( self, builder ):
        return self.name or super().getHash( builder )

    def isGlobal(self, *args):
        return True

    def generate( self, builder ):
        nodeVary = builder.getVarFromNode( self, self.getNodeType( builder ) )
        name = self.name

        if name:
            nodeVary.name = name
        return builder.getPropertyName( nodeVary )