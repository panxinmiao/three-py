import math
from .lighting_node import LightingNode
from ..core.context_node import ContextNode
# from ..utils.max_mip_level_node import MaxMipLevelNode
from ..shadernode.shader_node import ShaderNode
from ..shadernode.shader_node_elements import (
        float, add, mul, div, log2, clamp, roughness, reflect, mix, positionViewDirection, negate, normalize, equirectUV, vec2, invert, 
        transformedNormalView, transformedNormalWorld, transformDirection, cameraViewMatrix
    )
from ..core.cache_node import CacheNode
from ..utils.specular_mip_level_node import SpecularMipLevelNode

# def __getSpecularMIPLevel(inputs, *args):
#     texture = inputs['texture']
#     levelNode = inputs['levelNode']

#     maxMIPLevelScalar = MaxMipLevelNode(texture)

#     sigma = div(mul(math.pi, mul(levelNode, levelNode)), add(1.0, levelNode))
#     desiredMIPLevel = add(maxMIPLevelScalar, log2(sigma))

#     return clamp(desiredMIPLevel, 0.0, maxMIPLevelScalar)


# _getSpecularMIPLevel = ShaderNode(__getSpecularMIPLevel)


class EnvironmentNode(LightingNode):

    def __init__(self, envNode=None) -> None:
        super().__init__()

        self.envNode = envNode

    def construct(self, builder):
        envNode = self.envNode
        properties = builder.getNodeProperties(self)

        #flipNormalWorld = vec3(negate(transformedNormalWorld.x), transformedNormalWorld.yz)

        # reflectVec = reflect(negate(positionViewDirection), transformedNormalView)
        # reflectVec = normalize(mix(reflectVec, transformedNormalView, mul(roughness, roughness)))
        # reflectVec = transformDirection(reflectVec, cameraViewMatrix)
        #reflectVec = vec3(negate(reflectVec.x), reflectVec.yz)

        # reflectVec = normalize(mix(new ReflectNode(), flipNormalWorld, mul(roughness, roughness)))

        reflectVec = None
        radianceTextureUVNode = None
        irradianceTextureUVNode = None

        def _getRadianceUVNode(textureNode):
            nonlocal reflectVec
            if reflectVec is None:
                reflectVec = reflect(negate(positionViewDirection), transformedNormalView)
                reflectVec = normalize(mix(reflectVec, transformedNormalView, mul(roughness, roughness)))
                reflectVec = transformDirection(reflectVec, cameraViewMatrix)

            if textureNode.isCubeTextureNode:                
                node = reflectVec
            elif textureNode.isTextureNode:
                nonlocal radianceTextureUVNode
                if radianceTextureUVNode is None:
                    # TODO: need PMREM
                    radianceTextureUVNode = equirectUV( reflectVec )
                    radianceTextureUVNode = vec2( radianceTextureUVNode.x, invert( radianceTextureUVNode.y ) )

                node = radianceTextureUVNode

            return node

        radianceContext = ContextNode(envNode, {
            "getUVNode": _getRadianceUVNode,
            "getSamplerLevelNode": lambda *args: roughness,
            "getMIPLevelAlgorithmNode": lambda textureNode, levelNode: SpecularMipLevelNode(textureNode, levelNode)
        })

        def _getIrradianceUVNode(textureNode):
            if textureNode.isCubeTextureNode:       
                node = transformedNormalWorld
            elif textureNode.isTextureNode:
                nonlocal irradianceTextureUVNode
                if irradianceTextureUVNode is None:
                    # TODO: need PMREM
                    irradianceTextureUVNode = equirectUV( transformedNormalWorld )
                    irradianceTextureUVNode = vec2( irradianceTextureUVNode.x, invert( irradianceTextureUVNode.y ) )

                node = irradianceTextureUVNode
            
            return node

        irradianceContext = ContextNode(envNode, {
            "getUVNode": _getIrradianceUVNode,
            "getSamplerLevelNode": lambda *args: float(1),
            "getMIPLevelAlgorithmNode": lambda textureNode, levelNode: SpecularMipLevelNode(textureNode, levelNode)
        })


        isolateRadianceFlowContext = CacheNode(radianceContext)

        builder.context.radiance.add(isolateRadianceFlowContext)

        builder.context.iblIrradiance.add(mul(math.pi, irradianceContext))

        properties.radianceContext = isolateRadianceFlowContext
        properties.irradianceContext = irradianceContext
