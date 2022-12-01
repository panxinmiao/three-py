from warnings import warn
from .node import Node
from .varying_node import VaryingNode
from .node_builder import NodeBuilder

class AttributeNode(Node):
    def __init__(self, attributeName, nodeType=None) -> None:
        super().__init__(nodeType=nodeType)
        self._attributeName = attributeName

    def getHash(self, builder ):
        return self.getAttributeName( builder )

    def getNodeType(self, builder:'NodeBuilder'):
        nodeType = super().getNodeType(builder)
        if nodeType is None:
            attributeName = self.getAttributeName(builder)
            if builder.hasGeometryAttribute(attributeName):
                attribute = builder.geometry.getAttribute( attributeName )
                nodeType = builder.getTypeFromLength(attribute.itemSize)
            else:
                nodeType = 'float'
 
        return nodeType

    def setAttributeName(self, attributeName ):
        self._attributeName = attributeName
        return self

    def getAttributeName(self, *args):
        '''/*builder*/'''
        return self._attributeName

    def generate( self, builder:'NodeBuilder'):
        attributeName = self.getAttributeName( builder )
        nodeType = self.getNodeType( builder )

        if builder.hasGeometryAttribute( attributeName ):
            nodeAttribute = builder.getAttribute( attributeName, nodeType )

            if builder.isShaderStage( 'vertex' ):
                return nodeAttribute.name
            else:
                nodeVarying = VaryingNode( self )
                return nodeVarying.build( builder, nodeAttribute.type )
        else:
            warn( f'Attribute {attributeName} is not found' )
            return builder.getConst( nodeType )

    

