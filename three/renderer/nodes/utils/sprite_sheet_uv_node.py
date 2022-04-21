# from three.renderer.nodes import Node, UVNode, FloatNode, OperatorNode, MathNode, SplitNode, JoinNode

from ..core.node import Node
from ..core.const_node import ConstNode
from ..accessors.uv_node import UVNode
from .split_node import SplitNode
from .join_node import JoinNode

class SpriteSheetUVNode(Node):

    def __init__(self, countNode, uvNode = None, frameNode = None ) -> None:
        super().__init__( 'vec2' )

        self.countNode = countNode
        self.uvNode = uvNode or UVNode()
        self.frameNode = frameNode or ConstNode( 0 )

    def generate( self, builder ):
        from ..math.operator_node import OperatorNode
        from ..math.math_node import MathNode

        count = self.countNode
        uv = self.uvNode
        frame = self.frameNode

        one = ConstNode( 1 )

        width = SplitNode( count, 'x' )
        height = SplitNode( count, 'y' )

        total = OperatorNode( '*', width, height )

        roundFrame = MathNode( MathNode.FLOOR, MathNode( MathNode.MOD, frame, total ) )

        frameNum = OperatorNode( '+', roundFrame, one )

        cell = MathNode( MathNode.MOD, roundFrame, width )
        row = MathNode( MathNode.CEIL, OperatorNode( '/', frameNum, width ) )
        rowInv = OperatorNode( '-', height, row )

        scale = OperatorNode( '/', one, count )

        uvFrameOffset = JoinNode( [
            OperatorNode( '*', cell, SplitNode( scale, 'x' ) ) , 
            OperatorNode( '*', rowInv, SplitNode( scale, 'y' ) )
		] )

        uvScale = OperatorNode( '*', uv, scale )
        uvFrame = OperatorNode( '+', uvScale, uvFrameOffset )
        
        return uvFrame.build( builder, self.getNodeType( builder ) )
