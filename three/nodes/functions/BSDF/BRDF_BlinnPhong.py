import math
from .F_Schlick import F_Schlick
from ...shadernode.shader_node import ShaderNode
from ...shadernode.shader_node_base_elements import add, mul, clamp, dot, pow, normalize, transformedNormalView, positionViewDirection, shininess, specularColor

def __G_BlinnPhong_Implicit():
    return 0.25

G_BlinnPhong_Implicit = ShaderNode( __G_BlinnPhong_Implicit )

def __D_BlinnPhong( **inputs ):
    dotNH = inputs['dotNH']
    return (1/ math.pi) * ( shininess * 0.5 + 1.0 ) * pow( dotNH, shininess )
    # return (shininess * (1/ math.pi) * 0.5 + 1.0) * pow( dotNH, shininess )
    # return mul( mul( 1/ math.pi, add(mul(shininess, 0.5), 1.0) ), pow( dotNH, shininess) )

D_BlinnPhong = ShaderNode( __D_BlinnPhong )

def __BRDF_BlinnPhong( inputs ):

    lightDirection = inputs['lightDirection']

    halfDir = normalize( add( lightDirection, positionViewDirection ) )

    dotNH = clamp( dot( transformedNormalView, halfDir ) )
    dotVH = clamp( dot( positionViewDirection, halfDir ) )

    F = F_Schlick( { 'f0':specularColor, 'f90':1.0, 'dotVH':dotVH } )

    G = G_BlinnPhong_Implicit()

    D = D_BlinnPhong( shininess = shininess, dotNH = dotNH )
    
    return mul( F, mul( G, D ) )

BRDF_BlinnPhong = ShaderNode( __BRDF_BlinnPhong ) # validated