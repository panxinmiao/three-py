from ...shadernode.shader_node import ShaderNode
from ...shadernode.shader_node_base_elements import mul
import math

def __BRDF_Lambert(inputs):
    return mul( 1 / math.pi, inputs['diffuseColor'] )  # punctual light

BRDF_Lambert = ShaderNode( __BRDF_Lambert )