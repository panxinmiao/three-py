from ...structure import Dict
from ..shadernode.shader_node import ShaderNode
from ..shadernode.shader_node_base_elements import (
    mul, clamp, dot, transformedNormalView, property,
    diffuseColor, specularColor)

from .BSDF.BRDF_BlinnPhong import BRDF_BlinnPhong
from .BSDF.BRDF_Lambert import BRDF_Lambert


def __RE_Direct_BlinnPhong(inputs, *args):
    lightDirection = inputs['lightDirection']
    lightColor = inputs['lightColor']
    reflectedLight = inputs['reflectedLight']

    dotNL = clamp( dot( transformedNormalView, lightDirection ) )
    irradiance = mul( dotNL, lightColor )

    # shininess = nodeImmutable(PropertyNode, 'Shininess', 'float')
    shininess = property('Shininess', 'float')
    specularStrength = property('SpecularStrength', 'float')

    reflectedLight.directSpecular.add( mul( mul( irradiance, BRDF_BlinnPhong( { 'lightDirection': lightDirection, 'specularColor': specularColor, 'shininess': shininess } ) ), specularStrength ) )

    reflectedLight.directDiffuse.add( mul( irradiance, BRDF_Lambert( { 'diffuseColor': diffuseColor.rgb } ) ) )


RE_Direct_BlinnPhong = ShaderNode(__RE_Direct_BlinnPhong)


def __RE_IndirectDiffuse_BlinnPhong(inputs, *args):
    irradiance = inputs['irradiance']
    reflectedLight = inputs['reflectedLight']
    reflectedLight.indirectDiffuse.add(
        mul(irradiance, BRDF_Lambert.call({"diffuseColor": diffuseColor})))


RE_IndirectDiffuse_BlinnPhong = ShaderNode(__RE_IndirectDiffuse_BlinnPhong)


PhongLightingModel = Dict({
    "direct": RE_Direct_BlinnPhong,
    "indirectDiffuse": RE_IndirectDiffuse_BlinnPhong,
})
