from .node_material import NodeMaterial
from three.materials import MeshStandardMaterial
from ..lighting.lights_node import LightsNode
from ..lighting.environment_node import EnvironmentNode
from ..lighting.ao_node import AONode
from ..functions.material.getRoughness import getRoughness
from ..functions.physical_lighting_model import physicalLightingModel

from ..shadernode.shader_node_elements import (
        float, vec3, vec4, mix, invert, texture, cubeTexture,
        materialRoughness, materialMetalness, materialColor, diffuseColor,
        metalness, roughness, specularColor)

defaultValues = MeshStandardMaterial()

class MeshStandardNodeMaterial(NodeMaterial):

    isMeshStandardNodeMaterial = True
    
    def __init__(self, parameters = None) -> None:

        super().__init__()

        self.lights = True

        self.colorNode = None
        self.opacityNode = None

        self.alphaTestNode = None

        self.normalNode = None

        self.emissiveNode = None

        self.metalnessNode = None
        self.roughnessNode = None

        self.envNode = None

        self.lightsNode = None

        self.positionNode = None

        self.setDefaultValues( defaultValues )
        self.setValues( parameters )

    def constructLightingModel(self, *args):
        return physicalLightingModel

    def constructLights(self, builder):
        # lightsNode = self.lightsNode or builder.lightsNode

        lightsNode = super().constructLights(builder)

        # envNode = self.envNode or builder.scene.environmentNode
        materialLightsNode = []
        envNode = self.envNode or builder.material.envMap or builder.scene.environmentNode or builder.scene.environment
        if envNode:
            if envNode.isTexture:
                envNode = cubeTexture(envNode)
            materialLightsNode.append( EnvironmentNode( envNode ) )
        
        if builder.material.aoMap:
            materialLightsNode.append( AONode( texture( builder.material.aoMap ) ) )

        if len( materialLightsNode ) > 0:
            lightsNode = LightsNode( materialLightsNode + lightsNode.lightNodes )
        
        return lightsNode

    def constructVariants( self, builder, stack ):
        # METALNESS
        metalnessNode = float(self.metalnessNode) if self.metalnessNode else materialMetalness
        stack.assign( metalness, metalnessNode )
        stack.assign( diffuseColor, vec4( diffuseColor.rgb * invert(metalnessNode) , diffuseColor.a ) )

        # ROUGHNESS
        roughnessNode = float(self.roughnessNode) if self.roughnessNode else materialRoughness
        roughnessNode = getRoughness( { 'roughness': roughnessNode } )
        stack.assign( roughness, roughnessNode )

        # SPECULAR COLOR
        specularColorNode = mix( vec3( 0.04 ), materialColor.rgb, metalnessNode )
        stack.assign( specularColor, specularColorNode )

    def copy( self, source: 'MeshStandardNodeMaterial' ):

        self.colorNode = source.colorNode
        self.opacityNode = source.opacityNode

        self.alphaTestNode = source.alphaTestNode

        self.normalNode = source.normalNode

        self.emissiveNode = source.emissiveNode

        self.metalnessNode = source.metalnessNode
        self.roughnessNode = source.roughnessNode

        self.envNode = source.envNode

        self.lightsNode = source.lightsNode

        self.positionNode = source.positionNode

        return super().copy( source )
