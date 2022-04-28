import three

# from three.renderer.nodes import TempNode, NodeBuilder, ShaderNode, vec3, pow, mul, sub, mix, join, lessThanEqual

from ..core.temp_node import TempNode
from ..core.node_builder import NodeBuilder
from ..shader.shader_node import ShaderNode


def __LinearTosRGB(inputs):
    from ..shader.shader_node_elements import vec3, pow, mul, sub, mix, join, lessThanEqual
    value = inputs.value
    rgb = value.rgb
    a = sub( mul( pow( value.rgb, vec3( 0.41666 ) ), 1.055 ), vec3( 0.055 ) )
    b = mul( rgb, 12.92 )
    factor = vec3( lessThanEqual( rgb, vec3( 0.0031308 ) ) )
    rgbResult = mix( a, b, factor )
    return join( rgbResult.r, rgbResult.g, rgbResult.b, value.a )


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
        #self.factor = None


    def fromEncoding(self, encoding ):
        #components = __getEncodingComponents( encoding )
        method = None
        if encoding == three.LinearEncoding:
            method = 'Linear'
        elif encoding == three.sRGBEncoding:
            method = 'sRGB'

        self.method = 'LinearTo' + method
        #self.factor = components[ 1 ]

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
