from ..core.node import Node
from ..core.var_node import VarNode
from ..core.property_node import PropertyNode
from ..core.attribute_node import AttributeNode
from ..core.const_node import ConstNode
from ..core.uniform_node import UniformNode

from ..utils.join_node import JoinNode
#from ..utils.split_node import SplitNode
from ..utils.convert_node import ConvertNode
from ..utils.array_element_node import ArrayElementNode
# from ..math import CondNode, OperatorNode, MathNode
from ..math.cond_node import CondNode
from ..math.operator_node import OperatorNode
from ..math.math_node import MathNode
from ..accessors.position_node import PositionNode
from ..accessors.buffer_node import BufferNode
from ..accessors.normal_node import NormalNode
from ..accessors.camera_node import CameraNode
from ..accessors.model_node import ModelNode
from ..accessors.uv_node import UVNode
from ..accessors.texture_node import TextureNode

# from ..accessors import NormalNode, PositionNode

# from three.math import Color, Vector2, Vector3, Vector4, Matrix3, Matrix4
from ..core.node_utils import getValueFromType

from .shader_node_utils import shader_node_object as nodeObject
from .shader_node_utils import shader_node_array as ShaderNodeArray
from .shader_node_utils import shader_node_proxy as ShaderNodeProxy


#TODO __all__ = []

# uniform = ShaderNode( lambda input_node: input_node.setConst( False ))

uniform = lambda constNode: nodeObject( UniformNode( constNode.value, constNode.nodeType ) )

def label(node, name):
    node = nodeObject( node )
    if node.isVarNode == True:
        node.name = name
        return node
    return nodeObject( VarNode( node, name ) )

def temp(node):
    return nodeObject( VarNode( nodeObject( node ) ) )

# def ConvertType( type, valueClass = None, valueComponents = 1):

#     def __call( *params):
#         params = list(params)
#         if params and len(params)>0 and params[ 0 ].isNode:
#             return nodeObject( ConvertNode( params[ 0 ], type ) )

#         if len(params) == 1 and valueComponents != 1:

# 			# Providing one scalar value: This value is used for all components
#             for i in range(1, valueComponents):
#                 params.append(params [ 0 ])

#         val = params[ 0 ] if ( valueClass is None or isinstance(params[ 0 ], valueClass) ) else valueClass().set( *params )

#         return nodeObject( ConstNode( val, type ) )

#     return __call

class ConvertType:

    def __init__(self, type, valueClass = None, valueComponents = 1) -> None:
        self.type = type
        self.valueClass = valueClass
        self.valueComponents = valueComponents

    
    def __call__(self, *args, **kwds):
        # if args:
        params = list(args)
        
        if len(params)>0 and isinstance( params[ 0 ], Node):
            return nodeObject( ConvertNode( params[ 0 ], self.type ) )

        if len(params) == 1 and self.valueComponents != 1:

            # Providing one scalar value: This value is used for all components
            for i in range(1, self.valueComponents):
                params.append(params [ 0 ])

        val = params[ 0 ] if ( self.valueClass is None or isinstance(params[ 0 ], self.valueClass) ) else self.valueClass().set( *params )

        return nodeObject( ConstNode( val, self.type ) )



# float = ConvertType( 'float' )
# int = ConvertType( 'int' )
# uint = ConvertType( 'uint' )
# bool = ConvertType( 'bool' )
# color = ConvertType( 'color', Color )

# vec2 = ConvertType( 'vec2', Vector2, 2 )
# ivec2 = ConvertType( 'ivec2', Vector2, 2 )
# uvec2 = ConvertType( 'uvec2', Vector2, 2 )
# bvec2 = ConvertType( 'bvec2', Vector2, 2 )

# vec3 = ConvertType( 'vec3', Vector3, 3 )
# ivec3 = ConvertType( 'ivec3', Vector3, 3 )
# uvec3 = ConvertType( 'uvec3', Vector3, 3 )
# bvec3 = ConvertType( 'bvec3', Vector3, 3 )

# vec4 = ConvertType( 'vec4', Vector4, 4 )
# ivec4 = ConvertType( 'ivec4', Vector4, 4 )
# uvec4 = ConvertType( 'uvec4', Vector4, 4 )
# bvec4 = ConvertType( 'bvec4', Vector4, 4 )

# mat3 = ConvertType( 'mat3', Matrix3 )
# imat3 = ConvertType( 'imat3', Matrix3 )
# umat3 = ConvertType( 'umat3', Matrix3 )
# bmat3 = ConvertType( 'bmat3', Matrix3 )

# mat4 = ConvertType( 'mat4', Matrix4 )
# imat4 = ConvertType( 'imat4', Matrix4 )
# umat4 = ConvertType( 'umat4', Matrix4 )
# bmat4 = ConvertType( 'bmat4', Matrix4 )

# def float(val):
#     return nodeObject( FloatNode(val).setConst(True) )

# def color( *args ):
# 	return nodeObject( ColorNode( Color( *args ) ).setConst( True ) )


def join( *args ):
    return nodeObject( JoinNode( ShaderNodeArray( list(args) ) ) )

def uv( *args ):
    return nodeObject( UVNode( *args ) )

def attribute( *args ):
    return nodeObject( AttributeNode( *args ) )

def buffer( *args ):
    return nodeObject( BufferNode( *args ) )

def texture( *args ):
    return nodeObject( TextureNode( *args ) )

def sampler( texture ):
    return nodeObject( ConvertNode( texture if texture.isNode else TextureNode( texture ), 'sampler' ) )

def cond( *args ):
    return nodeObject( CondNode( *ShaderNodeArray( list(args) ) ) )

# def vec2( *args ):
#     if len(args) >0 and isinstance(args[0], Node):
#         return nodeObject( ConvertNode( args[ 0 ], 'vec2' ) )
#     else:
#         # Providing one scalar value: This value is used for all components
#         if ( len(args) == 1 ):
#             args+=args
      
#         return nodeObject( Vector2Node( Vector2( *args ) ).setConst( True ) )

# def vec3( *args ):
#     if len(args) >0 and isinstance(args[0], Node):
#         return nodeObject( ConvertNode( args[ 0 ], 'vec3' ) )
#     else:
#         # Providing one scalar value: This value is used for all components
#         if ( len(args) == 1 ):
#             args += (args+(args[0],))
      
#         return nodeObject( Vector3Node( Vector3( *args ) ).setConst( True ) )

# def vec4( *args ):
#     if len(args) >0 and isinstance(args[0], Node):
#         return nodeObject( ConvertNode( args[ 0 ], 'vec4' ) )
#     else:
#         # Providing one scalar value: This value is used for all components
#         if ( len(args) == 1 ):
#             args += args
#             args += args
      
#         return nodeObject( Vector4Node( Vector4( *args ) ).setConst( True ) )

# def mat3( val ):
# 	return nodeObject( Matrix3Node( val ).setConst( True ) )


# def mat4( val ):
# 	return nodeObject(Matrix4Node( val ).setConst( True ) )

def addTo( varNode, *params ):
	varNode.node = add( varNode.node, *ShaderNodeArray( params ) )
	return nodeObject( varNode )


# uv = ShaderNodeProxy( UVNode )
# attribute = ShaderNodeProxy( AttributeNode )
# texture = ShaderNodeProxy( TextureNode )

add = ShaderNodeProxy( OperatorNode, '+' )
sub = ShaderNodeProxy( OperatorNode, '-' )
mul = ShaderNodeProxy( OperatorNode, '*' )
div = ShaderNodeProxy( OperatorNode, '/' )
remainder = ShaderNodeProxy( OperatorNode, '%' )
equal = ShaderNodeProxy( OperatorNode, '==' )
assign = ShaderNodeProxy( OperatorNode, '=' )
lessThan = ShaderNodeProxy( OperatorNode, '<' )
greaterThan = ShaderNodeProxy( OperatorNode, '>' )
lessThanEqual = ShaderNodeProxy( OperatorNode, '<=' )
greaterThanEqual = ShaderNodeProxy( OperatorNode, '>=' )
and_ = ShaderNodeProxy( OperatorNode, '&&' )
or_ = ShaderNodeProxy( OperatorNode, '||' )
xor = ShaderNodeProxy( OperatorNode, '^^' )
bitAnd = ShaderNodeProxy( OperatorNode, '&' )
bitOr = ShaderNodeProxy( OperatorNode, '|' )
bitXor = ShaderNodeProxy( OperatorNode, '^' )
shiftLeft = ShaderNodeProxy( OperatorNode, '<<' )
shiftRight = ShaderNodeProxy( OperatorNode, '>>' )

element = ShaderNodeProxy( ArrayElementNode )

normalGeometry = nodeObject(NormalNode( NormalNode.GEOMETRY ))
normalLocal = nodeObject(NormalNode( NormalNode.LOCAL ))
normalWorld = nodeObject(NormalNode( NormalNode.WORLD ))
normalView = nodeObject(NormalNode( NormalNode.VIEW ))
transformedNormalView = nodeObject(VarNode( NormalNode( NormalNode.VIEW ), 'TransformedNormalView', 'vec3' ))

positionLocal = nodeObject(PositionNode( PositionNode.LOCAL ))
positionWorld = nodeObject(PositionNode( PositionNode.WORLD ))
positionView = nodeObject(PositionNode( PositionNode.VIEW ))
positionViewDirection = nodeObject(PositionNode( PositionNode.VIEW_DIRECTION ))

viewMatrix = nodeObject(ModelNode( ModelNode.VIEW_MATRIX ) )
cameraPosition = nodeObject( CameraNode( CameraNode.POSITION ) )

PI = float( 3.141592653589793 )
PI2 = float( 6.283185307179586 )
PI_HALF = float( 1.5707963267948966 )
RECIPROCAL_PI = float( 0.3183098861837907 )
RECIPROCAL_PI2 = float( 0.15915494309189535 )
EPSILON = float( 1e-6 )

diffuseColor = nodeObject(PropertyNode( 'DiffuseColor', 'vec4' ))
roughness = nodeObject(PropertyNode( 'Roughness', 'float' ))
metalness = nodeObject(PropertyNode( 'Metalness', 'float' ))
alphaTest = nodeObject(PropertyNode( 'AlphaTest', 'float' ))
specularColor = nodeObject(PropertyNode( 'SpecularColor', 'color' ))

abs = ShaderNodeProxy( MathNode, 'abs' )
acos = ShaderNodeProxy( MathNode, 'acos' )
asin = ShaderNodeProxy( MathNode, 'asin' )
atan = ShaderNodeProxy( MathNode, 'atan' )
ceil = ShaderNodeProxy( MathNode, 'ceil' )
clamp = ShaderNodeProxy( MathNode, 'clamp' )
cos = ShaderNodeProxy( MathNode, 'cos' )
cross = ShaderNodeProxy( MathNode, 'cross' )
degrees = ShaderNodeProxy( MathNode, 'degrees' )
dFdx = ShaderNodeProxy( MathNode, 'dpdx' )
dFdy = ShaderNodeProxy( MathNode, 'dpdy' )
distance = ShaderNodeProxy( MathNode, 'distance' )
dot = ShaderNodeProxy( MathNode, 'dot' )
exp = ShaderNodeProxy( MathNode, 'exp' )
exp2 = ShaderNodeProxy( MathNode, 'exp2' )
faceforward = ShaderNodeProxy( MathNode, 'faceforward' )
floor = ShaderNodeProxy( MathNode, 'floor' )
fract = ShaderNodeProxy( MathNode, 'fract' )
invert = ShaderNodeProxy( MathNode, 'invert' )
inversesqrt = ShaderNodeProxy( MathNode, 'inversesqrt' )
length = ShaderNodeProxy( MathNode, 'length' )
log = ShaderNodeProxy( MathNode, 'log' )
log2 = ShaderNodeProxy( MathNode, 'log2' )
max = ShaderNodeProxy( MathNode, 'max' )
min = ShaderNodeProxy( MathNode, 'min' )
mix = ShaderNodeProxy( MathNode, 'mix' )
mod = ShaderNodeProxy( MathNode, 'mod' )
negate = ShaderNodeProxy( MathNode, 'negate' )
normalize = ShaderNodeProxy( MathNode, 'normalize' )
pow = ShaderNodeProxy( MathNode, 'pow' )
pow2 = ShaderNodeProxy( MathNode, 'pow', 2 )
pow3 = ShaderNodeProxy( MathNode, 'pow', 3 )
pow4 = ShaderNodeProxy( MathNode, 'pow', 4 )
radians = ShaderNodeProxy( MathNode, 'radians' )
reflect = ShaderNodeProxy( MathNode, 'reflect' )
refract = ShaderNodeProxy( MathNode, 'refract' )
round = ShaderNodeProxy( MathNode, 'round' )
saturate = ShaderNodeProxy( MathNode, 'saturate' )
sign = ShaderNodeProxy( MathNode, 'sign' )
sin = ShaderNodeProxy( MathNode, 'sin' )
smoothstep = ShaderNodeProxy( MathNode, 'smoothstep' )
sqrt = ShaderNodeProxy( MathNode, 'sqrt' )
step = ShaderNodeProxy( MathNode, 'step' )
tan = ShaderNodeProxy( MathNode, 'tan' )
transformDirection = ShaderNodeProxy( MathNode, 'transformDirection' )

