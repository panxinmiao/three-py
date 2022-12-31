from ..shadernode.shader_node import ShaderNode
from ..shadernode.shader_node_base_elements import (
    mul, clamp, dot, transformedNormalView, lightingModel,
    diffuseColor, materialReflectivity)

from .BSDF.BRDF_BlinnPhong import BRDF_BlinnPhong
from .BSDF.BRDF_Lambert import BRDF_Lambert


def __RE_Direct_BlinnPhong(inputs, *args):
    lightDirection = inputs['lightDirection']
    lightColor = inputs['lightColor']
    reflectedLight = inputs['reflectedLight']

    dotNL = clamp( dot( transformedNormalView, lightDirection ) )
    irradiance = mul( dotNL, lightColor )

    reflectedLight.directSpecular.add( mul( mul( irradiance, BRDF_BlinnPhong( { 'lightDirection': lightDirection } ) ), materialReflectivity ) )

    reflectedLight.directDiffuse.add( mul( irradiance, BRDF_Lambert( { 'diffuseColor': diffuseColor.rgb } ) ) )


RE_Direct_BlinnPhong = ShaderNode(__RE_Direct_BlinnPhong)


def __RE_IndirectDiffuse_BlinnPhong(inputs, *args):
    irradiance = inputs['irradiance']
    reflectedLight = inputs['reflectedLight']
    reflectedLight.indirectDiffuse.add(
        mul(irradiance, BRDF_Lambert.call({"diffuseColor": diffuseColor})))


RE_IndirectDiffuse_BlinnPhong = ShaderNode(__RE_IndirectDiffuse_BlinnPhong)

phongLightingModel = lightingModel( RE_Direct_BlinnPhong, RE_IndirectDiffuse_BlinnPhong )