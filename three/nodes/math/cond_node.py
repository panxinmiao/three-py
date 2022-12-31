
# from three.renderer.nodes import Node, ContextNode, PropertyNode

from ..core.node import Node
from ..core.context_node import ContextNode
from ..core.property_node import PropertyNode

class CondNode(Node):
    def __init__(self, condNode, ifNode, elseNode=None ) -> None:
        super().__init__()

        self.condNode = condNode
        self.ifNode = ifNode
        self.elseNode = elseNode

    def getNodeType( self, builder, *args ):
        
        ifType = self.ifNode.getNodeType( builder )

        if self.elseNode is not None:
            elseType = self.elseNode.getNodeType( builder )
            if ( builder.getTypeLength( elseType ) > builder.getTypeLength( ifType ) ):
                return elseType

        return ifType

    def generate( self, builder ):

        type = self.getNodeType( builder )

        context = {'tempWrite': False}

        needsProperty = self.ifNode.getNodeType( builder ) != 'void' or ( self.elseNode and self.elseNode.getNodeType( builder ) != 'void' )
        
        nodeProperty = PropertyNode( type ).build( builder ) if needsProperty else ''
        nodeSnippet = ContextNode( self.condNode ).build( builder, 'bool' )

        builder.addFlowCode( f'''if ( {nodeSnippet} ) {{\n\n\t\t''', False )

        ifSnippet = ContextNode( self.ifNode, context ).build( builder, type )
        ifSnippet = nodeProperty + ' = ' + ifSnippet + ';' if needsProperty else ifSnippet

        builder.addFlowCode( ifSnippet + '\n\n\t}', False )

        elseSnippet = ContextNode( self.elseNode, context ).build( builder, type ) if self.elseNode else None

        if elseSnippet is not None:
            elseSnippet = nodeProperty + ' = ' + elseSnippet + ';' if nodeProperty else elseSnippet
            builder.addFlowCode( f''' else {{\n\n\t\t{elseSnippet}\n\n\t}}\n''', False )

#         builder.addFlowCode(
# f'''
# if ( {nodeSnippet} ) {{
#     {nodeProperty} = {ifSnippet};
# }} else {{
#     {nodeProperty} = {elseSnippet};
# }}
# ''')
        return nodeProperty
