from ...shader.shader_node import ShaderNode
from ...shader.shader_node_base_elements import max, abs, dFdx, dFdy, normalGeometry

def __getGeometryRoughness():
    dxy = max( abs( dFdx( normalGeometry ) ), abs( dFdy( normalGeometry ) ) )
    geometryRoughness = max( max( dxy.x, dxy.y ), dxy.z )
    return geometryRoughness

getGeometryRoughness = ShaderNode( __getGeometryRoughness )
