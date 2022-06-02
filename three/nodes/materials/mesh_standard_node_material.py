from .node_material import NodeMaterial
from three.materials import MeshStandardMaterial

from ..lighting.lights_node import LightsNode
from ..lighting.environment_node import EnvironmentNode
from ..lighting.ao_node import AONode
from ..functions.material.getRoughness import getRoughness
from ..functions.physical_lighting_model import PhysicalLightingModel

from ..display.normal_map_node import NormalMapNode

from ..shadernode.shader_node_elements import (
        float, vec3, vec4, normalView, add, context,
        assign, label, mul, invert, mix, texture, uniform,
        materialRoughness, materialMetalness, materialEmissive)

defaultValues = MeshStandardMaterial()

class MeshStandardNodeMaterial(NodeMaterial):
    
    def __init__(self, parameters = None) -> None:

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

        self.lightsNode = None

        self.positionNode = None

        self.setDefaultValues( defaultValues )
        self.setValues( parameters )

    def build( self, builder ):
        main = self.generateMain( builder )
        colorNode = main['colorNode']
        diffuseColorNode = main['diffuseColorNode']

        envNode = self.envNode or builder.scene.environmentNode
        diffuseColorNode = self.generateStandardMaterial( builder, { 'colorNode': colorNode, 'diffuseColorNode': diffuseColorNode } )

        if self.lightsNode:
            builder.lightsNode = self.lightsNode

        materialLightsNode = []

        if envNode:
            materialLightsNode.append(EnvironmentNode(envNode))

        if builder.material.aoMap:
            materialLightsNode.append(AONode(texture(builder.material.aoMap)))

        if len(materialLightsNode)>0:
            builder.lightsNode = LightsNode( builder.lightsNode.lightNodes + materialLightsNode)

        outgoingLightNode = self.generateLight(builder, {
                                               'diffuseColorNode': diffuseColorNode, 'lightingModelNode': PhysicalLightingModel})

        self.generateOutput( builder, { 'diffuseColorNode': diffuseColorNode, 'outgoingLightNode': outgoingLightNode } )


    def generateStandardMaterial( self, builder, parameters ):

        colorNode = parameters['colorNode']
        diffuseColorNode = parameters['diffuseColorNode']

        material = builder.material

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

        normalNode = vec3(self.normalNode) if self.normalNode else (
            NormalMapNode(texture(material.normalMap), uniform(material.normalScale)) if material.normalMap else normalView)
            
        builder.addFlow( 'fragment', label( normalNode, 'TransformedNormalView' ) )

        return diffuseColorNode

    def generateLight(self, builder, parameters):

        diffuseColorNode = parameters['diffuseColorNode']
        lightingModelNode = parameters['lightingModelNode']
        
        lightsNode = parameters.get("lightsNode", builder.lightsNode)

        renderer = builder.renderer

        outgoingLightNode = super().generateLight(builder, {
            'diffuseColorNode': diffuseColorNode, 'lightsNode': lightsNode, 'lightingModelNode': lightingModelNode})

        # EMISSIVE
        outgoingLightNode = add(
            vec3(self.emissiveNode or materialEmissive), outgoingLightNode)

        # TONE MAPPING
        if renderer.toneMappingNode:
            outgoingLightNode = context(renderer.toneMappingNode, {'color': outgoingLightNode})

        return outgoingLightNode

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

        self.lightsNode = source.lightsNode

        self.positionNode = source.positionNode

        return super().copy( source )
