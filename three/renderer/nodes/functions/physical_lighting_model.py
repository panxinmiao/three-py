from ..shader.shader_node_elements import mul, saturate, dot, transformedNormalView, diffuseColor, specularColor, roughness
from ..shader.shader_node import ShaderNode
from .BSDF.BRDF_GGX import BRDF_GGX
from .BSDF.BRDF_Lambert import BRDF_Lambert

def __RE_Direct_Physical( inputs ):
    #const { lightDirection, lightColor, directDiffuse, directSpecular } = inputs

    lightDirection = inputs['lightDirection']
    lightColor = inputs['lightColor']
    reflectedLight = inputs['reflectedLight']
    # directDiffuse = inputs['directDiffuse']
    # directSpecular = inputs['directSpecular']

    dotNL = saturate( dot( transformedNormalView, lightDirection ) )
    irradiance = mul( dotNL, lightColor )

    reflectedLight.directSpecular.add( mul( irradiance, BRDF_GGX( { 'lightDirection': lightDirection, 'f0': specularColor, 'f90': 1, 'roughness': roughness } ) ) )

    reflectedLight.directDiffuse.add( mul( irradiance, BRDF_Lambert( { 'diffuseColor': diffuseColor.rgb } ) ) )


RE_Direct_Physical = ShaderNode(__RE_Direct_Physical)

# PHYSICALLY_CORRECT_LIGHTS <-> builder.renderer.physicallyCorrectLights === true
PhysicalLightingModel = ShaderNode( lambda inputs, *args: RE_Direct_Physical( inputs ))
