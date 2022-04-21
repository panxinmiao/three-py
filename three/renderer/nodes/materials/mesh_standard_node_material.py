from .node_material import NodeMaterial
from ....materials import MeshStandardMaterial
from ..functions import PhysicalLightingModel, getRoughness
from ..shader.shader_node_elements import float, vec3, vec4, assign, label, mul, invert, mix, normalView, materialRoughness, materialMetalness

defaultValues = MeshStandardMaterial()

class MeshStandardNodeMaterial(NodeMaterial):
    
    def __init__(self, parameters) -> None:

        super().__init__()

        self.colorNode = None
        self.opacityNode = None

        self.alphaTestNode = None

        self.normalNode = None

        self.emissiveNode = None

        self.metalnessNode = None
        self.roughnessNode = None

        self.clearcoatNode = None
        self.clearcoatRoughnessNode = None

        self.envNode = None

        self.lightNode = None

        self.positionNode = None

        self.setDefaultValues( defaultValues )
        self.setValues( parameters )

    def build( self, builder ):
        lightNode = self.lightNode or builder.lightNode  # use scene lights
        main = self.generateMain( builder )

        colorNode = main['colorNode']
        diffuseColorNode = main['diffuseColorNode']

        diffuseColorNode = self.generateStandardMaterial( builder, { 'colorNode': colorNode, 'diffuseColorNode': diffuseColorNode } )

        outgoingLightNode = self.generateLight( builder, { 'diffuseColorNode': diffuseColorNode, 'lightNode': lightNode } )

        self.generateOutput( builder, { 'diffuseColorNode': diffuseColorNode, 'outgoingLightNode': outgoingLightNode } )

    def generateLight( self, builder, parameters ):

        diffuseColorNode = parameters['diffuseColorNode']
        lightNode = parameters['lightNode']

        outgoingLightNode = super().generateLight( builder, { 'diffuseColorNode': diffuseColorNode, 'lightNode': lightNode, 'lightingModelNode': PhysicalLightingModel } )

        # @TODO: add IBL code here

        return outgoingLightNode

    def generateStandardMaterial( self, builder, parameters ):

        colorNode = parameters['colorNode']
        diffuseColorNode = parameters['diffuseColorNode']

        # METALNESS

        metalnessNode = float( self.metalnessNode ) if self.metalnessNode else materialMetalness

        metalnessNode = builder.addFlow( 'fragment', label( metalnessNode, 'Metalness' ) )
        builder.addFlow( 'fragment', assign( diffuseColorNode, vec4( mul( diffuseColorNode.rgb, invert( metalnessNode ) ), diffuseColorNode.a ) ) )

        # ROUGHNESS

        roughnessNode = float( self.roughnessNode ) if self.roughnessNode else materialRoughness
        roughnessNode = getRoughness( { 'roughness': roughnessNode } )

        builder.addFlow( 'fragment', label( roughnessNode, 'Roughness' ) )

        # SPECULAR COLOR

        specularColorNode = mix( vec3( 0.04 ), colorNode.rgb, metalnessNode )

        builder.addFlow( 'fragment', label( specularColorNode, 'SpecularColor' ) )

        # NORMAL VIEW

        normalNode = vec3( self.normalNode ) if self.normalNode else normalView

        builder.addFlow( 'fragment', label( normalNode, 'TransformedNormalView' ) )

        return diffuseColorNode


    def copy( self, source: 'MeshStandardNodeMaterial' ):

        self.colorNode = source.colorNode
        self.opacityNode = source.opacityNode

        self.alphaTestNode = source.alphaTestNode

        self.normalNode = source.normalNode

        self.emissiveNode = source.emissiveNode

        self.metalnessNode = source.metalnessNode
        self.roughnessNode = source.roughnessNode

        self.clearcoatNode = source.clearcoatNode
        self.clearcoatRoughnessNode = source.clearcoatRoughnessNode

        self.envNode = source.envNode

        self.lightNode = source.lightNode

        self.positionNode = source.positionNode

        return super().copy( source )
