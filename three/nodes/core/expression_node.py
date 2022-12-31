from .node import Node
from .node_builder import NodeBuilder

class ExpressionNode(Node):
    def __init__(self, snipped = '', nodeType = 'void') -> None:
        super().__init__(nodeType)
        self.snipped = snipped

    def generate( self, builder: 'NodeBuilder', output):
        type = self.getNodeType( builder )
        snipped = self.snipped
        if type == 'void':
            builder.addFlowCode( snipped )
        else:
            return builder.format( f'( { snipped } )', type, output )
