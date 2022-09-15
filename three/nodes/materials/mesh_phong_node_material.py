from three.materials import MeshPhongMaterial
from three.constants import MultiplyOperation, MixOperation, AddOperation

from .node_material import NodeMaterial
from ..lighting.lights_node import LightsNode
from ..lighting.ao_node import AONode
from ..functions.phong_lighting_model import PhongLightingModel

from ..display.normal_map_node import NormalMapNode

from ..accessors.material_reference_node import MaterialReferenceNode
from ..accessors.texture_node import TextureNode
from ..utils.split_node import SplitNode

from ..shadernode.shader_node_elements import (
        vec3, vec4, normalView, add, context, cubeTexture, mix, mul, property, nodeObject, 
        label, texture, uniform, materialEmissive)

defaultValues = MeshPhongMaterial()

class MeshPhongNodeMaterial(NodeMaterial):

    isMeshPhongNodeMaterial = True
    
    def __init__(self, parameters = None) -> None:

        super().__init__()

        self.colorNode = None
        self.opacityNode = None

        self.alphaTestNode = None

        self.normalNode = None

        self.emissiveNode = None

        self.specularNode = None

        self.envNode = None

        self.lightsNode = None

        self.positionNode = None

        self.setDefaultValues( defaultValues )
        self.setValues( parameters )

    def build( self, builder ):
        self.generatePosition(builder)

        diffuseColor = self.generateDiffuseColor(builder)

        colorNode = diffuseColor['colorNode']
        diffuseColorNode = diffuseColor['diffuseColorNode']

        diffuseColorNode = self.generatePhongMaterial( builder, { 'colorNode': colorNode, 'diffuseColorNode': diffuseColorNode } )

        if self.lightsNode:
            builder.lightsNode = self.lightsNode

        materialLightsNode = []

        # if envNode:
        #     materialLightsNode.append(EnvironmentNode(envNode))

        if builder.material.aoMap:
            materialLightsNode.append(AONode(texture(builder.material.aoMap)))

        if len(materialLightsNode)>0:
            builder.lightsNode = LightsNode( builder.lightsNode.lightNodes + materialLightsNode)

        outgoingLightNode = self.generateLight(builder, {
                                               'diffuseColorNode': diffuseColorNode, 'lightingModelNode': PhongLightingModel})

        self.generateOutput( builder, { 'diffuseColorNode': diffuseColorNode, 'outgoingLightNode': outgoingLightNode } )


    def generatePhongMaterial( self, builder, parameters ):

        # colorNode = parameters['colorNode']
        diffuseColorNode = parameters['diffuseColorNode']

        material = builder.material

        # SPECULAR COLOR

        specularNode = self.specularNode or MaterialReferenceNode( 'specular', 'color' )
        # if not specularNode:
        #     materialSpecular = MaterialReferenceNode( 'specular', 'color' )
        #     if material.specularMap and material.specularMap.isTexture:
        #         specularMap = TextureNode(material.specularMap)
        #         specularNode = OperatorNode('*', materialSpecular, specularMap)
        #     else:
        #         specularNode = materialSpecular

        specularColorNode = vec4(specularNode) 

        builder.addFlow( 'fragment', label( specularColorNode, 'SpecularColor' ) )

        # Specular Strength
        if material.specularMap and material.specularMap.isTexture:
            specularStrength = SplitNode(TextureNode(material.specularMap), 'r')
        else:
            specularStrength = 1.0
        
        builder.addFlow( 'fragment', label( specularStrength, 'SpecularStrength' ) )

        # Shininess
        shininessNode = MaterialReferenceNode('shininess', 'float')
        builder.addFlow( 'fragment', label( shininessNode, 'Shininess' ) )

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

        # ENV MAPPING
        envNode = self.envNode

        if not envNode:
            if builder.material.envMap and builder.material.envMap.isTexture:
                envNode = cubeTexture(builder.material.envMap)

        if not envNode:
            if builder.scene.environmentNode:
                if builder.scene.environmentNode.isTexture:
                    envNode = cubeTexture(builder.scene.environmentNode)
                else:
                    envNode = nodeObject(builder.scene.environmentNode)
            elif builder.scene.environment:
                envNode = cubeTexture(builder.scene.environment)

        if envNode:
            reflectivity = MaterialReferenceNode('reflectivity', 'float')
            if builder.material.combine == MultiplyOperation:
                outgoingLightNode = mix(outgoingLightNode, mul(outgoingLightNode, envNode.xyz), mul(property('SpecularStrength', 'float'), reflectivity))
            elif builder.material.combine == MixOperation:
                outgoingLightNode = mix(outgoingLightNode, envNode.xyz, mul(property('SpecularStrength', 'float'), reflectivity))
            elif builder.material.combine == AddOperation:
                outgoingLightNode = add(outgoingLightNode, mul(envNode.xyz, mul(property('SpecularStrength', 'float'), reflectivity)))

        # TONE MAPPING
        if renderer.toneMappingNode:
            outgoingLightNode = context(renderer.toneMappingNode, {'color': outgoingLightNode})

        return outgoingLightNode

    def copy( self, source: 'MeshPhongNodeMaterial' ):

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
