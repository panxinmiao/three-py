import math
from .lighting_node import LightingNode
from ..core.context_node import ContextNode
from ..utils.max_mip_level_node import MaxMipLevelNode
from ..shadernode.shader_node import ShaderNode
from ..shadernode.shader_node_base_elements import float, add, mul, div, log2, clamp, roughness, reflect, mix, positionViewDirection, negate, normalize, transformedNormalView, transformedNormalWorld, transformDirection, cameraViewMatrix


def __getSpecularMIPLevel(inputs, *args):
    texture = inputs['texture']
    levelNode = inputs['levelNode']

    maxMIPLevelScalar = MaxMipLevelNode(texture)

    sigma = div(mul(math.pi, mul(levelNode, levelNode)), add(1.0, levelNode))
    desiredMIPLevel = add(maxMIPLevelScalar, log2(sigma))

    return clamp(desiredMIPLevel, 0.0, maxMIPLevelScalar)


_getSpecularMIPLevel = ShaderNode(__getSpecularMIPLevel)


class EnvironmentNode(LightingNode):

    def __init__(self, envNode=None) -> None:
        super().__init__()

        self.envNode = envNode

    def construct(self, builder):
        envNode = self.envNode
        properties = builder.getNodeProperties(self)

        #flipNormalWorld = vec3(negate(transformedNormalWorld.x), transformedNormalWorld.yz)

        reflectVec = reflect(negate(positionViewDirection), transformedNormalView)
        reflectVec = normalize(mix(reflectVec, transformedNormalView, mul(roughness, roughness)))
        reflectVec = transformDirection(reflectVec, cameraViewMatrix)
        #reflectVec = vec3(negate(reflectVec.x), reflectVec.yz)

        # reflectVec = normalize(mix(new ReflectNode(), flipNormalWorld, mul(roughness, roughness)))

        radianceContext = ContextNode(envNode, {
            "tempRead": False,
            "uvNode": reflectVec,
            "levelNode": roughness,
            "levelShaderNode": _getSpecularMIPLevel
        })

        irradianceContext = ContextNode(envNode, {
            "tempRead": False,
            "uvNode": transformedNormalWorld,
            "levelNode": float(1),
            "levelShaderNode": _getSpecularMIPLevel
        })

        # it's used to cache the construct only if necessary: See `CubeTextureNode.getConstructReference()`
        radianceContext.context.environmentContext = radianceContext
        irradianceContext.context.environmentContext = irradianceContext

        builder.context.radiance.add(radianceContext)

        builder.context.iblIrradiance.add(mul(math.pi, irradianceContext))

        properties.radianceContext = radianceContext
        properties.irradianceContext = irradianceContext
