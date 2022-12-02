from .F_Schlick import F_Schlick
from .V_GGX_SmithCorrelated import V_GGX_SmithCorrelated
from .D_GGX import D_GGX
from ...shadernode.shader_node import ShaderNode
from ...shadernode.shader_node_base_elements import dotNV, add, mul, clamp, dot, pow2, normalize, transformedNormalView, positionViewDirection

def __BRDF_GGX( inputs ):
    #const { lightDirection, f0, f90, roughness } = inputs

    lightDirection = inputs['lightDirection']
    f0 = inputs['f0']
    f90 = inputs['f90']
    roughness = inputs['roughness']

    alpha = pow2( roughness ) # UE4's roughness

    halfDir = normalize( add( lightDirection, positionViewDirection ) )

    dotNL = clamp( dot( transformedNormalView, lightDirection ) )
    #dotNV = clamp( dot( transformedNormalView, positionViewDirection ) )
    dotNH = clamp( dot( transformedNormalView, halfDir ) )
    dotVH = clamp( dot( positionViewDirection, halfDir ) )

    F = F_Schlick( { 'f0':f0, 'f90':f90, 'dotVH':dotVH } )

    V = V_GGX_SmithCorrelated( { 'alpha':alpha, 'dotNL':dotNL, 'dotNV':dotNV } )

    D = D_GGX( { 'alpha':alpha, 'dotNH':dotNH } )
    
    return mul( F, mul( V, D ) )

BRDF_GGX = ShaderNode( __BRDF_GGX ) # validated