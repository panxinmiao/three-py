import three

from ..shadernode.shader_node import ShaderNode
from ..shadernode.shader_node_base_elements import vec3, pow, mul, sub, mix, vec4, lessThanEqual

from ..core.temp_node import TempNode
from ..core.node_builder import NodeBuilder


def __LinearTosRGB(inputs):
    
    value = inputs.value
    rgb = value.rgb
    a = sub( mul( pow( value.rgb, vec3( 0.41666 ) ), 1.055 ), vec3( 0.055 ) )
    b = mul( rgb, 12.92 )
    factor = vec3( lessThanEqual( rgb, vec3( 0.0031308 ) ) )
    rgbResult = mix( a, b, factor )
    return vec4(rgbResult, value.a)


LinearToLinear = ShaderNode(lambda inputs : inputs.value )

LinearTosRGB = ShaderNode(__LinearTosRGB)


EncodingLib = {
    'LinearToLinear': LinearToLinear,
    'LinearTosRGB': LinearTosRGB
}


class ColorSpaceNode(TempNode):
    LINEAR_TO_LINEAR = 'LinearToLinear'
    LINEAR_TO_SRGB = 'LinearTosRGB'

    def __init__(self, method, node) -> None:
        super().__init__('vec4')
        self.method = method
        self.node = node

    def fromEncoding(self, encoding ):
        method = None
        if encoding == three.LinearEncoding:
            method = 'Linear'
        elif encoding == three.sRGBEncoding:
            method = 'sRGB'

        self.method = 'LinearTo' + method

        return self

    def construct(self, builder: 'NodeBuilder'):

        method = self.method
        node = self.node

        outputNode = None

        if method != ColorSpaceNode.LINEAR_TO_LINEAR:
            encodingFunctionNode = EncodingLib[ method ]
            outputNode = encodingFunctionNode({
                'value': node,
            })

        else:
            outputNode = node

        return outputNode