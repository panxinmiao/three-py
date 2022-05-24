from ...shadernode.shader_node import ShaderNode
from ...shadernode.shader_node_base_elements import add, sub, mul, div, pow2, max, sqrt, EPSILON

def __V_GGX_SmithCorrelated(inputs):
    alpha = inputs['alpha']
    dotNL = inputs['dotNL']
    dotNV = inputs['dotNV']

    a2 = pow2(alpha)
    gv = mul( dotNL, sqrt( add( a2, mul( sub( 1.0, a2 ), pow2( dotNV ) ) ) ) )
    gl = mul( dotNV, sqrt( add( a2, mul( sub( 1.0, a2 ), pow2( dotNL ) ) ) ) )

    return div( 0.5, max( add( gv, gl ), EPSILON ) )

V_GGX_SmithCorrelated = ShaderNode(__V_GGX_SmithCorrelated)