from .lighting_node import LightingNode
from ..shader.shader_node_base_elements import float, add, mul, sub

class AONode(LightingNode):

    def __init__(self, aoNode=None) -> None:
        super().__init__()
        self.aoNode = aoNode

    def generate(self, builder):
        aoIntensity = 1
        aoNode = add( mul( sub( float( self.aoNode ), 1.0 ), aoIntensity ), 1.0 )

        builder.context.ambientOcclusion.mul( aoNode )