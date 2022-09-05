from .node_material import NodeMaterial
from three.materials import MeshNormalMaterial
from ..core.expression_node import ExpressionNode

from ..shadernode.shader_node_elements import (
    float, assign, label, mul, add, normalize, cross, dFdx, dFdy, vec4, 
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

    
    def generateDiffuseColor(self, builder):

        # < FRAGMENT STAGE >

        normalNode = normalize(cross(dFdx(positionView), dFdy(positionView))) if self.flatShading else normalView

        colorNode = vec4(add(mul(normalNode, 0.5), 0.5))

        opacityNode = float( self.opacityNode ) if self.opacityNode else materialOpacity

        # COLOR
        colorNode = builder.addFlow( 'fragment', label( colorNode, 'Color' ) )
        diffuseColorNode = builder.addFlow( 'fragment', label( colorNode, 'DiffuseColor' ) )

        # OPACITY
        opacityNode = builder.addFlow( 'fragment', label( opacityNode, 'OPACITY' ) )
        builder.addFlow( 'fragment', assign( diffuseColorNode.a, mul( diffuseColorNode.a, opacityNode ) ) )

        # ALPHA TEST
        if self.alphaTestNode or self.alphaTest > 0:

            alphaTestNode = float( self.alphaTestNode ) if self.alphaTestNode else materialAlphaTest

            builder.addFlow( 'fragment', label( alphaTestNode, 'AlphaTest' ) )

            # @TODO: remove ExpressionNode here and then possibly remove it completely
            builder.addFlow( 'fragment', ExpressionNode( 'if ( DiffuseColor.a <= AlphaTest ) { discard; }' ) )

        return { 'colorNode': colorNode, 'diffuseColorNode': diffuseColorNode }