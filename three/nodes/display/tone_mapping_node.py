from ..core.temp_node import TempNode
from ..shader.shader_node import ShaderNode
from ..shader.shader_node_base_elements import mul, float

from ...constants import LinearToneMapping

LinearToneMappingNode = ShaderNode(
    lambda inputs: mul(inputs['color'], inputs['exposure'])
)

class ToneMappingNode(TempNode):

    def __init__(self, toneMapping, exposureNode = float( 1 ), colorNode = None ) -> None:
        super().__init__('vec3')

        self.toneMapping = toneMapping

        self.exposureNode = exposureNode
        self.colorNode = colorNode

    def generate( self, builder ):
        type = self.getNodeType( builder )
        colorNode = self.color or builder.context.color

        toneMapping = self.toneMapping
        toneMappingParams = { 'exposure': self.exposureNode, 'color': colorNode }

        if toneMapping == LinearToneMapping:
            return LinearToneMappingNode( toneMappingParams ).build( builder, type )
        else:
            return self.colorNode.build( builder, type )