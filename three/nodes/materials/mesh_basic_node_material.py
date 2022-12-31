from .node_material import NodeMaterial
from three.materials import MeshBasicMaterial
from three.constants import MultiplyOperation, MixOperation, AddOperation

from ..shadernode.shader_node_elements import ( add, cubeTexture, mix, mul, diffuseColor, materialReflectivity, nodeObject)

defaultValues = MeshBasicMaterial()

class MeshBasicNodeMaterial(NodeMaterial):

    isMeshStandardNodeMaterial = True

    def __init__(self, parameters = None ) -> None:
        super().__init__()
        self.lights = False
        self.colorNode = None
        self.opacityNode = None
        self.alphaTestNode = None
        self.lightsNode = None
        self.positionNode = None

        self.setDefaultValues( defaultValues )
        self.setValues( parameters )

    def copy( self, source ):
        self.colorNode = source.colorNode
        self.opacityNode = source.opacityNode
        self.alphaTestNode = source.alphaTestNode
        self.lightsNode = source.lightsNode
        self.positionNode = source.positionNode
        return super().copy( source )

    def constructLighting(self, builder, stack):
        outgoingLightNode = diffuseColor.xyz
        envNode = self.envNode or builder.material.envMap or builder.scene.environmentNode or builder.scene.environment
        if envNode:
            if envNode.isTexture:
                envNode = cubeTexture(envNode)
            else:
                envNode = nodeObject(envNode)

            if builder.material.combine == MultiplyOperation:
                outgoingLightNode = mix(outgoingLightNode, mul(outgoingLightNode, envNode.xyz), materialReflectivity)
            elif builder.material.combine == MixOperation:
                outgoingLightNode = mix(outgoingLightNode, envNode.xyz, materialReflectivity)
            elif builder.material.combine == AddOperation:
                outgoingLightNode = add(outgoingLightNode, mul(envNode.xyz, materialReflectivity))

        return outgoingLightNode



    # def generateLight(self, builder, parameters):

    #     renderer = builder.renderer

    #     outgoingLightNode = super().generateLight(builder, parameters)

    #     # ENV MAPPING
    #     envNode = self.envNode or builder.material.envMap or builder.scene.environmentNode or builder.scene.environment

    #     if envNode and envNode.isTexture:
    #         envNode = cubeTexture(envNode)
    #     else:
    #         envNode = nodeObject(envNode)

    #     if envNode:
    #         reflectivity = MaterialReferenceNode('reflectivity', 'float')
    #         material = builder.material
    #         if material.specularMap and material.specularMap.isTexture:
    #             specularStrength = SplitNode(TextureNode(material.specularMap), 'r')
    #         else:
    #             specularStrength = 1.0

    #         if builder.material.combine == MultiplyOperation:
    #             outgoingLightNode = mix(outgoingLightNode, mul(outgoingLightNode, envNode.xyz), mul(specularStrength, reflectivity))
    #         elif builder.material.combine == MixOperation:
    #             outgoingLightNode = mix(outgoingLightNode, envNode.xyz, mul(specularStrength, reflectivity))
    #         elif builder.material.combine == AddOperation:
    #             outgoingLightNode = add(outgoingLightNode, mul(envNode.xyz, mul(specularStrength, reflectivity)))

    #     # TONE MAPPING
    #     if renderer.toneMappingNode:
    #         outgoingLightNode = context(renderer.toneMappingNode, {'color': outgoingLightNode})

    #     return outgoingLightNode