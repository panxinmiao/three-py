from warnings import warn
from ..core.temp_node import TempNode
from ..shadernode.shader_node import ShaderNode
from ..shadernode.shader_node_base_elements import mul, float, clamp, vec3, max, pow, mat3
from ...constants import NoToneMapping, LinearToneMapping, ReinhardToneMapping, CineonToneMapping, ACESFilmicToneMapping

LinearToneMappingNode = ShaderNode(
    lambda inputs: mul(inputs['color'], inputs['exposure'])
)

# source: https://www.cs.utah.edu/docs/techreports/2002/pdf/UUCS-02-001.pdf
def __reinhardToneMapping(inputs):
    color = mul(inputs['color'], inputs['exposure'])
    return clamp( color / ( vec3( 1.0 ) + color ) )

ReinhardToneMappingNode = ShaderNode(__reinhardToneMapping)


# source: http://filmicworlds.com/blog/filmic-tonemapping-operators/
def __OptimizedCineonToneMapping(inputs):
    color = mul(inputs['color'], inputs['exposure'])
    color = max( vec3( 0.0 ), color-0.004 )

    a = color * ( 6.2 * color + 0.5 )
    b = color * ( 6.2 * color + 1.7 ) + 0.06

    return pow( a / b, vec3( 2.2 ) )

OptimizedCineonToneMappingNode = ShaderNode(__OptimizedCineonToneMapping)


# source: https://github.com/selfshadow/ltc_code/blob/master/webgl/shaders/ltc/ltc_blit.fs
def __RRTAndODTFit(inputs):
    # a = color.mul( color.add( 0.0245786 ) ).sub( 0.000090537 )
    color = inputs['color'],
    a = color * ( color + 0.0245786 ) - 0.000090537
    b = color * ( color + 0.4329510 ) * 0.983729 + 0.238081 

    return a / b

RRTAndODTFit = ShaderNode(__RRTAndODTFit)

# source: https://github.com/selfshadow/ltc_code/blob/master/webgl/shaders/ltc/ltc_blit.fs
def __ACESFilmicToneMapping(inputs):
    color = inputs['color']
    exposure = inputs['exposure']
    
    # sRGB => XYZ => D65_2_D60 => AP1 => RRT_SAT
    ACESInputMat = mat3(
		vec3( 0.59719, 0.07600, 0.02840 ), # transposed from source
		vec3( 0.35458, 0.90834, 0.13383 ),
		vec3( 0.04823, 0.01566, 0.83777 )
	)

    # ODT_SAT => XYZ => D60_2_D65 => sRGB
    ACESOutputMat = mat3(
		vec3( 1.60475, - 0.10208, - 0.00327 ), # transposed from source
		vec3( - 0.53108, 1.10813, - 0.07276 ),
		vec3( - 0.07367, - 0.00605, 1.07602 )
	)

    color = (color * exposure) / 0.6 
    color = ACESInputMat * color

    # Apply RRT and ODT
    color = RRTAndODTFit( { 'color': color } )

    color = ACESOutputMat * color

    # Clamp to [0, 1]
    return clamp( color )

ACESFilmicToneMappingNode = ShaderNode(__ACESFilmicToneMapping)

toneMappingLib = {
    LinearToneMapping: LinearToneMappingNode,
    ReinhardToneMapping: ReinhardToneMappingNode,
    CineonToneMapping: OptimizedCineonToneMappingNode,
    ACESFilmicToneMapping: ACESFilmicToneMappingNode
}

class ToneMappingNode(TempNode):

    def __init__(self, toneMapping=NoToneMapping, exposureNode = float( 1 ), colorNode = None ) -> None:
        super().__init__('vec3')

        self.toneMapping = toneMapping

        self.exposureNode = exposureNode
        self.colorNode = colorNode

    def construct(self, builder):

        colorNode = self.colorNode or builder.context.color

        toneMapping = self.toneMapping

        if toneMapping == NoToneMapping:
            return colorNode

        toneMappingParams = { 'exposure': self.exposureNode, 'color': colorNode }

        toneMappingNode = toneMappingLib.get(toneMapping, None)
        outputNode = None

        if toneMappingNode:
            outputNode = toneMappingNode( toneMappingParams )
        else:
            warn( f'ToneMappingNode: Unsupported Tone Mapping configuration. {toneMapping}' )
            outputNode = colorNode
        
        return outputNode