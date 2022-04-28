# from three.renderer.nodes import Node, UVNode, ShaderNode, add, mul, floor, mod, sign

from ..core.node import Node
from ..shader.shader_node import ShaderNode
from ..shader.shader_node_elements import uv, add, mul, floor, mod, sign

def __checkerShaderNode(inputs):
	uv = mul( inputs.uv, 2.0 )

	cx = floor( uv.x )
	cy = floor( uv.y )
	result = mod( add( cx, cy ), 2.0 )

	return sign( result )

__checkerShaderNode = ShaderNode(__checkerShaderNode)

class CheckerNode(Node):

	def __init__(self, uvNode = None) -> None:
		super().__init__('float')
		self.uvNode = uvNode or uv()

	def generate( self, builder ):
		return __checkerShaderNode( { 'uv': self.uvNode } ).build( builder )
