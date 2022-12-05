
from ..core.temp_node import TempNode
from ..shadernode.shader_node_base_elements import vec2, vec3, negate, normalize, cross, dot, mul, add, transformedNormalView, positionViewDirection

class MatcapUVNode(TempNode):

    def __init__(self) -> None:
        super().__init__('vec2')

    def construct( self, *args ):
        x = normalize( vec3( positionViewDirection.z, 0, negate( positionViewDirection.x ) ) )
        y = cross( positionViewDirection, x )

        return add( mul( vec2( dot( x, transformedNormalView ), dot( y, transformedNormalView ) ), 0.495 ), 0.5 )