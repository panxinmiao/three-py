from .F_Schlick import F_Schlick
from .V_GGX_SmithCorrelated import V_GGX_SmithCorrelated
from .D_GGX import D_GGX
from ...shader.shader_node import ShaderNode

from ...shader.shader_node_elements import dotNV, add, mul, saturate, dot, pow2, normalize, transformedNormalView, positionViewDirection

def __BRDF_GGX( inputs ):
    #const { lightDirection, f0, f90, roughness } = inputs

    lightDirection = inputs['lightDirection']
    f0 = inputs['f0']
    f90 = inputs['f90']
    roughness = inputs['roughness']

    alpha = pow2( roughness ) # UE4's roughness

    halfDir = normalize( add( lightDirection, positionViewDirection ) )

    dotNL = saturate( dot( transformedNormalView, lightDirection ) )
    #dotNV = saturate( dot( transformedNormalView, positionViewDirection ) )
    dotNH = saturate( dot( transformedNormalView, halfDir ) )
    dotVH = saturate( dot( positionViewDirection, halfDir ) )

    F = F_Schlick( { 'f0':f0, 'f90':f90, 'dotVH':dotVH } )

    V = V_GGX_SmithCorrelated( { 'alpha':alpha, 'dotNL':dotNL, 'dotNV':dotNV } )

    D = D_GGX( { 'alpha':alpha, 'dotNH':dotNH } )
    
    return mul( F, mul( V, D ) )

BRDF_GGX = ShaderNode( __BRDF_GGX ); # validated