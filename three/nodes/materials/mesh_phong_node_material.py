from three.materials import MeshPhongMaterial
from three.constants import MultiplyOperation, MixOperation, AddOperation

from .node_material import NodeMaterial
from ..functions.phong_lighting_model import phongLightingModel

from ..shadernode.shader_node_elements import (
        vec3, add, lightingContext, cubeTexture, mix, mul, nodeObject, float, max, label, clamp,
        materialShininess, shininess, materialSpecularColor, specularColor, diffuseColor, 
        materialReflectivity, nodeObject, materialEmissive)

defaultValues = MeshPhongMaterial()

class MeshPhongNodeMaterial(NodeMaterial):

    isMeshPhongNodeMaterial = True
    
    def __init__(self, parameters = None) -> None:

        super().__init__()

        self.lights = True

        self.colorNode = None
        self.opacityNode = None

        self.shininessNode = None
        self.specularNode = None

        self.alphaTestNode = None

        self.lightNode = None

        self.positionNode = None

        self.envNode = None

        self.setDefaultValues( defaultValues )
        self.setValues( parameters )

    def constructLightingModel(self, *args ):
        return phongLightingModel

    def constructLighting(self, builder, stack):
        material = builder.material

        # OUTGOING LIGHT

        lights = self.lights is True or self.lightsNode is not None

        lightsNode = self.constructLights( builder ) if lights else None
        lightingModelNode = self.constructLightingModel( builder ) if lightsNode else None

        outgoingLightNode = diffuseColor.xyz

        if lightsNode and lightsNode.hasLight is not False:
            outgoingLightNode = label( lightingContext( lightsNode, lightingModelNode ), 'Light' )

        # label( lightingContext( lightsNode, lightingModelNode ), 'Light' )

        envNode = self.envNode or builder.material.envMap or builder.scene.environmentNode or builder.scene.environment
        if envNode:
            if envNode.isTexture:
                envNode = cubeTexture(envNode)
            else:
                envNode = nodeObject(envNode)
            outgoingLightNode = clamp( outgoingLightNode, 0.0, 1.0 )
            if builder.material.combine == MultiplyOperation:
                outgoingLightNode = mix(outgoingLightNode, mul(outgoingLightNode, envNode.xyz), materialReflectivity)
            elif builder.material.combine == MixOperation:
                outgoingLightNode = mix(outgoingLightNode, envNode.xyz, materialReflectivity)
            elif builder.material.combine == AddOperation:
                outgoingLightNode = add(outgoingLightNode, mul(envNode.xyz, materialReflectivity))

        # EMISSIVE
        if (self.emissiveNode and self.emissiveNode.isNode) or (material.emissive and material.emissive.isColor):
            outgoingLightNode = outgoingLightNode + vec3( self.emissiveNode or materialEmissive )
        
        return outgoingLightNode

    def constructVariants(self, builder, stack ):

        # SHININESS

        shininessNode = max(float(self.shininessNode or materialShininess), 1e-4 )  # to prevent pow( 0.0, 0.0 )
        stack.assign( shininess, shininessNode )

        # SPECULAR COLOR

        specularNode = vec3( self.specularNode or materialSpecularColor )
        stack.assign( specularColor, specularNode )

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
