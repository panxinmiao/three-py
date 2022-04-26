#from three.renderer.nodes import Node, NodeBuilder
from .node import Node
from ..math.operator_node import OperatorNode
from .node_builder import NodeBuilder

class VarNode(Node):

    def __init__(self, node, name=None, nodeType=None) -> None:
        super().__init__(nodeType=nodeType)
        self.node = node
        self.name = name

    def op( self, op, *params ):
        self.node = OperatorNode( op, self.node, *params )
        return self


    def assign( self, *params ):
        return self.op( '=', *params )

    def add( self, *params ):
        return self.op( '+', *params )

    def sub( self, *params ):
        return self.op( '-', *params )

    def mul( self, *params ):
        return self.op( '*', *params )
    
    def div( self, *params ):
        return self.op( '/', *params )
        

    def getHash( self, builder ):
        if self.name:
            return self.name
        else:
            return super().getHash( builder )

    def getNodeType( self, builder:'NodeBuilder' , *args ):
        type = super().getNodeType( builder )
        if type is not None :
            return type
        else:
            return self.node.getNodeType( builder )

    def generate( self, builder:'NodeBuilder' ):
        node = self.node
        if node.isTempNode:
            return node.build( builder )

        name = self.name
        type = builder.getVectorType( self.getNodeType( builder ) )
        
        nodeVar = builder.getVarFromNode( self, type )
        snippet = node.build( builder, type )

        if name is not None:
            nodeVar.name = name

        propertyName = builder.getPropertyName( nodeVar )

        builder.addFlowCode( f'{propertyName} = {snippet}' )

        return propertyName

