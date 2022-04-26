from ...shader.shader_node import ShaderNode
from ...shader.shader_node_elements import mul
import math

def __BRDF_Lambert(inputs):
    return mul( 1 / math.pi, inputs['diffuseColor'] )  # punctual light

BRDF_Lambert = ShaderNode( __BRDF_Lambert )