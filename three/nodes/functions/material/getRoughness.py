from .getGeometryRoughness import getGeometryRoughness

from ...shader.shader_node import ShaderNode
from ...shader.shader_node_base_elements import add, max, min

def __getRoughness(inputs):
    roughness = inputs['roughness']
    geometryRoughness = getGeometryRoughness()
    roughnessFactor = max( roughness, 0.0525 )  # 0.0525 corresponds to the base mip of a 256 cubemap.
    roughnessFactor = add( roughnessFactor, geometryRoughness )
    roughnessFactor = min( roughnessFactor, 1.0 )

    return roughnessFactor

getRoughness = ShaderNode( __getRoughness )