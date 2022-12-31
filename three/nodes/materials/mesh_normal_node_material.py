from .node_material import NodeMaterial
from three.materials import MeshNormalMaterial

from ..shadernode.shader_node_elements import (
    float, mul, add, normalize, cross, dFdx, dFdy, vec4, diffuseColor, discard,
    positionView, normalView, materialAlphaTest, materialOpacity)

defaultValues = MeshNormalMaterial()

class MeshNormalNodeMaterial(NodeMaterial):

    isMeshNormalNodeMaterial = True

    def __init__(self, parameters = None) -> None:
        super().__init__()

        # self.colorNode = add(mul(NormalNode( NormalNode.VIEW ), 0.5), 0.5)
        self.opacityNode = None
        self.alphaTestNode = None
        self.lightsNode = None
        self.positionNode = None

        self.fog = False

        self.setDefaultValues( defaultValues )
        self.setValues( parameters )

    def copy( self, source ):
        self.colorNode = source.colorNode
        self.opacityNode = source.opacityNode
        self.alphaTestNode = source.alphaTestNode
        self.positionNode = source.positionNode
        return super().copy( source )

    
    def constructDiffuseColor(self, builder, stack):

        normalNode = normalize(cross(dFdx(positionView), dFdy(positionView))) if self.flatShading else normalView
        colorNode = vec4(add(mul(normalNode, 0.5), 0.5))
        opacityNode = float( self.opacityNode ) if self.opacityNode else materialOpacity

        # COLOR
        stack.assign( diffuseColor, colorNode )

        # OPACITY
        stack.assign( diffuseColor.a, diffuseColor.a * opacityNode )

        # ALPHA TEST
        if self.alphaTestNode or self.alphaTest > 0:
            alphaTestNode = float( self.alphaTestNode ) if self.alphaTestNode else materialAlphaTest
            stack.add( discard( diffuseColor.a <= alphaTestNode ) )
