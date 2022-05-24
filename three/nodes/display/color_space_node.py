import three

from ..shader.shader_node import ShaderNode
from ..shader.shader_node_base_elements import vec3, pow, mul, sub, mix, vec4, lessThanEqual

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

    def generate(self, builder:'NodeBuilder' ):

        type = self.getNodeType( builder )

        method = self.method
        node = self.node

        if method != ColorSpaceNode.LINEAR_TO_LINEAR:
            encodingFunctionNode = EncodingLib[ method ]

            return encodingFunctionNode({
                'value': node,
            }).build( builder, type )

        else:
            return node.build( builder, type )
