from .node import Node
from .varying_node import VaryingNode
from .node_builder import NodeBuilder

class AttributeNode(Node):
    def __init__(self, attributeName, nodeType=None) -> None:
        super().__init__(nodeType=nodeType)
        self._attributeName = attributeName

    def getHash(self, builder ):
        return self.getAttributeName( builder )

    def getNodeType(self, builder):
        nodeType = super().getNodeType(builder)
        if nodeType is None:
            attributeName = self.getAttributeName(builder)
            attribute = builder.geometry.getAttribute(attributeName)
            nodeType = builder.getTypeFromLength(attribute.itemSize)
 
        return nodeType

    def setAttributeName(self, attributeName ):
        self._attributeName = attributeName
        return self

    def getAttributeName(self, *args):
        '''/*builder*/'''
        return self._attributeName

    def generate( self, builder:'NodeBuilder'):
        attribute = builder.getAttribute( self.getAttributeName( builder ), self.getNodeType( builder ) )
        if builder.isShaderStage( 'vertex' ):
            return attribute.name
        else:
            nodeVarying = VaryingNode( self )
            return nodeVarying.build( builder, attribute.type )

    

