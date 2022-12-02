from ..core.node import Node
from ..shadernode.shader_node_base_elements import add, sub, div, mul, clamp

class RemapNode(Node):

    def __init__(self, node, inLowNode, inHighNode, outLowNode, outHighNode) -> None:
        super().__init__()

        self.node = node
        self.inLowNode = inLowNode
        self.inHighNode = inHighNode
        self.outLowNode = outLowNode
        self.outHighNode = outHighNode

        self.doClamp = True

    def construct( self, *args ):
        t = div( sub( self.node, self.inLowNode ), sub( self.inHighNode, self.inLowNode ) )

        if self.doClamp:
            t = clamp( t )
        
        return add( mul( sub( self.outHighNode, self.outLowNode ), t ), self.outLowNode )