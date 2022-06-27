#from three.renderer.nodes import Node

from ..core.node import Node

class PointUVNode(Node):

    isPointUVNode = True

    def __init__(self) -> None:
        super().__init__('vec2')

    def generate( self, *args ):
        return 'vec2( gl_PointCoord.x, 1.0 - gl_PointCoord.y )'
