from ..core.temp_node import TempNode

class PackingNode(TempNode):

    DIRECTION_TO_COLOR = 'directionToColor'
    COLOR_TO_DIRECTION = 'colorToDirection'

    def __init__(self, scope, node) -> None:
        super().__init__()
        self.scope = scope
        self.node = node

    def getNodeType( self, builder, *args ):
        return self.node.getNodeType( builder )
    
    def construct( self, *args ):
        scope = self.scope
        node = self.node
        result = None
        if scope == PackingNode.DIRECTION_TO_COLOR:
            result = node * 0.5 + 0.5
        elif scope == PackingNode.COLOR_TO_DIRECTION :
            result = node * 2.0 - 1.0
        return result