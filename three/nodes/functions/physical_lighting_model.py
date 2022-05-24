import math
from ...structure import Dict
from ..shader.shader_node import ShaderNode
from ..shader.shader_node_base_elements import (
    vec3, mul, saturate, add, sub, dot, div, transformedNormalView,
    pow, exp2, dotNV,
    diffuseColor, specularColor, roughness, temp)

from .BSDF.DFGApprox import DFGApprox
from .BSDF.BRDF_GGX import BRDF_GGX
from .BSDF.BRDF_Lambert import BRDF_Lambert


def computeMultiscattering(singleScatter, multiScatter, specularF90=1):
    '''
    Fdez-Agüera's "Multiple-Scattering Microfacet Model for Real-Time Image Based Lighting"
    Approximates multiscattering in order to preserve energy.
    http: // www.jcgt.org/published/0008/01/03/
    '''
    fab = DFGApprox.call({"roughness": roughness})

    FssEss = add(mul(specularColor, fab.x), mul(specularF90, fab.y))

    Ess = add(fab.x, fab.y)
    Ems = sub(1.0, Ess)

    Favg = add(specularColor, mul(sub(1.0, specularColor), 0.047619))  # 1/21
    Fms = div(mul(FssEss, Favg), sub(1.0, mul(Ems, Favg)))

    singleScatter.add(FssEss)
    multiScatter.add(mul(Fms, Ems))


def __RE_IndirectSpecular_Physical( inputs, *args ):
    radiance = inputs['radiance']
    iblIrradiance = inputs['iblIrradiance']
    reflectedLight = inputs['reflectedLight']

    # Both indirect specular and indirect diffuse light accumulate here
    singleScattering = temp(vec3())
    multiScattering = temp(vec3())
    cosineWeightedIrradiance = mul(iblIrradiance, 1 / math.pi)

    computeMultiscattering(singleScattering, multiScattering)

    diffuse = mul(diffuseColor, sub(1.0, add(singleScattering, multiScattering)))

    reflectedLight.indirectSpecular.add(mul(radiance, singleScattering))
    reflectedLight.indirectSpecular.add(mul(multiScattering, cosineWeightedIrradiance))

    reflectedLight.indirectDiffuse.add(mul(diffuse, cosineWeightedIrradiance))


RE_IndirectSpecular_Physical = ShaderNode(__RE_IndirectSpecular_Physical)


def __RE_IndirectDiffuse_Physical(inputs, *args):
    irradiance = inputs['irradiance']
    reflectedLight = inputs['reflectedLight']
    reflectedLight.indirectDiffuse.add(
        mul(irradiance, BRDF_Lambert.call({"diffuseColor": diffuseColor})))


RE_IndirectDiffuse_Physical = ShaderNode(__RE_IndirectDiffuse_Physical)


def __RE_Direct_Physical(inputs, *args):
    lightDirection = inputs['lightDirection']
    lightColor = inputs['lightColor']
    reflectedLight = inputs['reflectedLight']

    dotNL = saturate( dot( transformedNormalView, lightDirection ) )
    irradiance = mul( dotNL, lightColor )

    reflectedLight.directSpecular.add( mul( irradiance, BRDF_GGX( { 'lightDirection': lightDirection, 'f0': specularColor, 'f90': 1, 'roughness': roughness } ) ) )

    reflectedLight.directDiffuse.add( mul( irradiance, BRDF_Lambert( { 'diffuseColor': diffuseColor.rgb } ) ) )


RE_Direct_Physical = ShaderNode(__RE_Direct_Physical)


def __RE_AmbientOcclusion_Physical(inputs, *args):
    ambientOcclusion = inputs['ambientOcclusion']
    reflectedLight = inputs['reflectedLight']

    aoNV = add(dotNV, ambientOcclusion)
    aoExp = exp2(sub(mul(- 16.0, roughness), 1.0))

    aoNode = saturate(add(sub(pow(aoNV, aoExp), 1.0), ambientOcclusion))

    reflectedLight.indirectDiffuse.mul(ambientOcclusion)

    reflectedLight.indirectSpecular.mul(aoNode)


RE_AmbientOcclusion_Physical = ShaderNode(__RE_AmbientOcclusion_Physical)


PhysicalLightingModel = Dict({
	"direct": RE_Direct_Physical,
	"indirectDiffuse": RE_IndirectDiffuse_Physical,
	"indirectSpecular": RE_IndirectSpecular_Physical,
	"ambientOcclusion": RE_AmbientOcclusion_Physical
})
