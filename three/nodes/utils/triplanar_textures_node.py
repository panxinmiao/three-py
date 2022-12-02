from ..core.node import Node
from ..shadernode.shader_node_base_elements import float, vec3, add, mul, div, dot, normalize, abs, texture, positionWorld, normalWorld

class TriplanarTexturesNode(Node):

    def __init__(self, textureXNode, textureYNode = None, textureZNode = None, scaleNode = None, positionNode = None, normalNode = None) -> None:
        super().__init__('vec4')

        self.textureXNode = textureXNode
        self.textureYNode = textureYNode
        self.textureZNode = textureZNode

        self.scaleNode = scaleNode or float( 1 )
        self.positionNode = positionNode or positionWorld
        self.normalNode = normalNode or normalWorld

    def construct(self, *args):
        
        # Blending factor of triplanar mapping
        bf = normalize( abs( self.normalNode ) )
        bf = div( bf, dot( bf, vec3( 1.0 ) ) )

        # Triplanar mapping
        tx = mul( self.positionNode.yz, self.scaleNode )
        ty = mul( self.positionNode.zx, self.scaleNode )
        tz = mul( self.positionNode.xy, self.scaleNode )

        # Base color
        textureX = self.textureXNode.value
        textureY = self.textureYNode.value if self.textureYNode else textureX
        textureZ = self.textureZNode.value if self.textureZNode else textureX

        cx = mul( texture( textureX, tx ), bf.x )
        cy = mul( texture( textureY, ty ), bf.y )
        cz = mul( texture( textureZ, tz ), bf.z )

        return add( cx, cy, cz )