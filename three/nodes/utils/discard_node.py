from ..math.cond_node import CondNode
from ..core.expression_node import ExpressionNode

class DiscardNode(CondNode):

    discardExpression = None

    def __init__(self, condNode) -> None:
        
        DiscardNode.discardExpression = DiscardNode.discardExpression or ExpressionNode( 'discard' )

        super().__init__(condNode, DiscardNode.discardExpression)