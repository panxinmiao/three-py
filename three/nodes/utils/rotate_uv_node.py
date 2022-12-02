from ..core.temp_node import TempNode
from ..shadernode.shader_node_base_elements import vec2, add, sub, mul, cos, sin

class RotateUVNode(TempNode):

    def __init__(self, uvNode, rotationNode, centerNode = None) -> None:
        centerNode = centerNode or vec2( .5 )
        super().__init__('vec2')

        self.uvNode = uvNode
        self.rotationNode = rotationNode
        self.centerNode = centerNode
    
    def construct(self, *args):

        uvNode = self.uvNode
        centerNode = self.centerNode

        cosAngle = cos( self.rotationNode )
        sinAngle = sin( self.rotationNode )

        return vec2(
			add( add( mul( cosAngle, sub( uvNode.x, centerNode.x ) ), mul( sinAngle, sub( uvNode.y, centerNode.y ) ) ), centerNode.x ),
			add( sub( mul( cosAngle, sub( uvNode.y, centerNode.y ) ), mul( sinAngle, sub( uvNode.x, centerNode.x ) ) ), centerNode.y )
		)