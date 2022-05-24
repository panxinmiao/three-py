from ...shadernode.shader_node import ShaderNode
from ...shadernode.shader_node_base_elements import dotNV, vec2, vec4, add, mul, min, exp2

'''
Analytical approximation of the DFG LUT, one half of the
split-sum approximation used in indirect specular lighting.
via 'environmentBRDF' from "Physically Based Shading on Mobile"
https: // www.unrealengine.com/blog/physically-based-shading-on-mobile
'''
def __DFGApprox( inputs ):
    roughness = inputs["roughness"]

    c0 = vec4(- 1, - 0.0275, - 0.572, 0.022)

    c1 = vec4(1, 0.0425, 1.04, - 0.04)

    r = add(mul(roughness, c0), c1)

    a004 = add(mul(min(mul(r.x, r.x), exp2(mul(- 9.28, dotNV))), r.x), r.y)

    fab = add(mul(vec2(- 1.04, 1.04), a004), r.zw)

    return fab

DFGApprox = ShaderNode(__DFGApprox) 
