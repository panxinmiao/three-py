
# from three.renderer.nodes import Node, ContextNode, PropertyNode

from ..core.node import Node
from ..core.context_node import ContextNode
from ..core.property_node import PropertyNode

class CondNode(Node):
    def __init__(self, condNode, ifNode, elseNode ) -> None:
        super().__init__()

        self.condNode = condNode
        self.ifNode = ifNode
        self.elseNode = elseNode

    def getNodeType( self, builder, *args ):
        
        ifType = self.ifNode.getNodeType( builder )
        elseType = self.elseNode.getNodeType( builder )

        if ( builder.getTypeLength( elseType ) > builder.getTypeLength( ifType ) ):
            return elseType

        return ifType

    def generate( self, builder ):

        type = self.getNodeType( builder )

        context = {'tempWrite': False}
        nodeProperty = PropertyNode( None, type ).build( builder )

        nodeSnippet = ContextNode( self.condNode ).build( builder, 'bool' )
        ifSnippet = ContextNode( self.ifNode, context ).build( builder, type )
        elseSnippet = ContextNode( self.elseNode, context ).build( builder, type )

        builder.addFlowCode(
f'''
if ( {nodeSnippet} ) {{
    {nodeProperty} = {ifSnippet};
}} else {{
    {nodeProperty} = {elseSnippet};
}}
''')
        return nodeProperty
