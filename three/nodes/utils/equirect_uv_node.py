import math
from ..core.temp_node import TempNode
from ..shadernode.shader_node_base_elements import nodeObject, vec2, add, mul, atan2, asin, clamp, positionWorldDirection

class EquirectUVNode(TempNode):

    def __init__(self, dirNode = None) -> None:
        super().__init__('vec2')
        self.dirNode = dirNode or positionWorldDirection

    
    def construct( self, *args ):
        dir = nodeObject( self.dirNode )

        u = add( mul( atan2( dir.z, dir.x ), 1 / ( math.pi * 2 ) ), 0.5 )
        v = add( mul( asin( clamp( dir.y, - 1.0, 1.0 ) ), 1 / math.pi ), 0.5 )

        return vec2(u, v)