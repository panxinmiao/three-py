#from three.renderer.nodes import TempNode, NodeBuilder
from .temp_node import TempNode
from .node_builder import NodeBuilder


class ExpressionNode(TempNode):
    def __init__(self, snipped = '', nodeType = 'void') -> None:
        super().__init__(nodeType)
        self.snipped = snipped

    def generate( self, builder: 'NodeBuilder'):
        type = self.getNodeType( builder )
        snipped = self.snipped
        if type == 'void':
            builder.addFlowCode( snipped )
        else:
            return f'( { snipped } )'
