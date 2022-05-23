from ..core.property_node import PropertyNode
from ..core.var_node import VarNode
from ..core.attribute_node import AttributeNode
from ..core.uniform_node import UniformNode
from ..core.bypass_node import BypassNode
from ..core.instance_index_node import InstanceIndexNode
from ..core.context_node import ContextNode
from ..core.function_node import FunctionNode

from ..accessors.buffer_node import BufferNode
from ..accessors.storage_buffer_node import StorageBufferNode
from ..accessors.camera_node import CameraNode
from ..accessors.material_node import MaterialNode
from ..accessors.model_node import ModelNode
from ..accessors.model_view_projection_node import ModelViewProjectionNode
from ..accessors.normal_node import NormalNode
from ..accessors.position_node import PositionNode
from ..accessors.skinning_node import SkinningNode
from ..accessors.texture_node import TextureNode
from ..accessors.uv_node import UVNode
from ..accessors.instance_node import InstanceNode

#gpgpu
from ..gpgpu.compute_node import ComputeNode

# math nodes
from ..math.operator_node import OperatorNode
from ..math.cond_node import CondNode
from ..math.math_node import MathNode

# util nodes
from ..utils.array_element_node import ArrayElementNode
from ..utils.convert_node import ConvertNode
from ..utils.join_node import JoinNode
from ..utils.timer_node import TimerNode
#from ..utils.split_node import SplitNode

# other nodes
from ..display.color_space_node import ColorSpaceNode
from ..lights.light_context_node import LightContextNode
from ..lights.reflected_light_node import ReflectedLightNode

from .shader_node_utils import nodeObject, nodeArray, nodeProxy, ConvertType, cacheMaps

color = ConvertType( 'color' )

float = ConvertType( 'float', cacheMaps['float'] )
int = ConvertType( 'int', cacheMaps['int'] )
uint = ConvertType( 'uint', cacheMaps['uint'] )
bool = ConvertType( 'bool', cacheMaps['bool'] )

vec2 = ConvertType( 'vec2' )
ivec2 = ConvertType( 'ivec2' )
uvec2 = ConvertType( 'uvec2' )
bvec2 = ConvertType( 'bvec2' )

vec3 = ConvertType( 'vec3' )
ivec3 = ConvertType( 'ivec3' )
uvec3 = ConvertType( 'uvec3' )
bvec3 = ConvertType( 'bvec3' )

vec4 = ConvertType( 'vec4' )
ivec4 = ConvertType( 'ivec4' )
uvec4 = ConvertType( 'uvec4' )
bvec4 = ConvertType( 'bvec4' )

mat3 = ConvertType( 'mat3' )
imat3 = ConvertType( 'imat3' )
umat3 = ConvertType( 'umat3' )
bmat3 = ConvertType( 'bmat3' )

mat4 = ConvertType( 'mat4' )
imat4 = ConvertType( 'imat4' )
umat4 = ConvertType( 'umat4' )
bmat4 = ConvertType( 'bmat4' )


def uniform(value):
    nodeType = value.nodeType or value.convertTo

    if value.isNode:
        value = value.node.value if value.node else value.value

    return nodeObject( UniformNode( value, nodeType ))

def label(node, name):
    node = nodeObject( node )
    if node.isVarNode == True and node.name == name:
        return node
    return nodeObject( VarNode( node, name ) )

# def temp(node):
#     return nodeObject( VarNode( nodeObject( node ) ) )

temp = nodeProxy( VarNode )

join = lambda *args: nodeObject( JoinNode( nodeArray( list(args) ) ) )
uv = lambda *args: nodeObject( UVNode( *args ) )
attribute = lambda *args: nodeObject( AttributeNode( *args ) )
storage = lambda *args: nodeObject( StorageBufferNode( *args ) )
buffer = lambda *args: nodeObject( BufferNode( *args ) )
texture = lambda *args: nodeObject( TextureNode( *args ) )
sampler = lambda texture: nodeObject(ConvertNode(
    texture if texture.isNode else TextureNode(texture), 'sampler'))

timer = lambda *args: nodeObject( TimerNode( *args ) )

compute = lambda *args: nodeObject( ComputeNode( *args ) )
func = lambda *args: nodeObject( FunctionNode( *args ) )

cond = nodeProxy( CondNode )

add = nodeProxy( OperatorNode, '+' )
sub = nodeProxy( OperatorNode, '-' )
mul = nodeProxy( OperatorNode, '*' )
div = nodeProxy( OperatorNode, '/' )
remainder = nodeProxy( OperatorNode, '%' )
equal = nodeProxy( OperatorNode, '==' )
assign = nodeProxy( OperatorNode, '=' )
lessThan = nodeProxy( OperatorNode, '<' )
greaterThan = nodeProxy( OperatorNode, '>' )
lessThanEqual = nodeProxy( OperatorNode, '<=' )
greaterThanEqual = nodeProxy( OperatorNode, '>=' )
and_ = nodeProxy( OperatorNode, '&&' )
or_ = nodeProxy( OperatorNode, '||' )
xor = nodeProxy( OperatorNode, '^^' )
bitAnd = nodeProxy( OperatorNode, '&' )
bitOr = nodeProxy( OperatorNode, '|' )
bitXor = nodeProxy( OperatorNode, '^' )
shiftLeft = nodeProxy( OperatorNode, '<<' )
shiftRight = nodeProxy( OperatorNode, '>>' )

element = nodeProxy( ArrayElementNode )
instanceIndex = nodeObject( InstanceIndexNode() )

modelViewProjection = nodeProxy( ModelViewProjectionNode )

normalGeometry = nodeObject(NormalNode( NormalNode.GEOMETRY ))
normalLocal = nodeObject(NormalNode( NormalNode.LOCAL ))
normalWorld = nodeObject(NormalNode( NormalNode.WORLD ))
normalView = nodeObject(NormalNode( NormalNode.VIEW ))
transformedNormalView = nodeObject(VarNode( NormalNode( NormalNode.VIEW ), 'TransformedNormalView', 'vec3' ))

positionGeometry = nodeObject( PositionNode( PositionNode.GEOMETRY ))
positionLocal = nodeObject(PositionNode( PositionNode.LOCAL ))
positionWorld = nodeObject(PositionNode( PositionNode.WORLD ))
positionView = nodeObject(PositionNode( PositionNode.VIEW ))
positionViewDirection = nodeObject(PositionNode( PositionNode.VIEW_DIRECTION ))

viewMatrix = nodeObject(ModelNode( ModelNode.VIEW_MATRIX ) )
cameraPosition = nodeObject( CameraNode( CameraNode.POSITION ) )

# PI = float( 3.141592653589793 )
# PI2 = float( 6.283185307179586 )
# PI_HALF = float( 1.5707963267948966 )
# RECIPROCAL_PI = float( 0.3183098861837907 )
# RECIPROCAL_PI2 = float( 0.15915494309189535 )
# EPSILON = float( 1e-6 )

diffuseColor = nodeObject(PropertyNode( 'DiffuseColor', 'vec4' ))
roughness = nodeObject(PropertyNode( 'Roughness', 'float' ))
metalness = nodeObject(PropertyNode( 'Metalness', 'float' ))
alphaTest = nodeObject(PropertyNode( 'AlphaTest', 'float' ))
specularColor = nodeObject(PropertyNode( 'SpecularColor', 'color' ))

materialAlphaTest = nodeObject( MaterialNode( MaterialNode.ALPHA_TEST ) )
materialColor = nodeObject( MaterialNode( MaterialNode.COLOR ) )
materialOpacity = nodeObject( MaterialNode( MaterialNode.OPACITY ) )
materialSpecular = nodeObject( MaterialNode( MaterialNode.SPECULAR ) )
materialRoughness = nodeObject( MaterialNode( MaterialNode.ROUGHNESS ) )
materialMetalness = nodeObject( MaterialNode( MaterialNode.METALNESS ) )

skinning = nodeProxy( SkinningNode )
instance = nodeProxy( InstanceNode )

context = nodeProxy( ContextNode )
lightContext = nodeProxy( LightContextNode )

reflectedLight = nodeProxy( ReflectedLightNode )

colorSpace = lambda node, encoding : nodeObject( ColorSpaceNode( None, nodeObject( node ) ).fromEncoding( encoding ) )

bypass = nodeProxy( BypassNode )

abs = nodeProxy( MathNode, 'abs' )
acos = nodeProxy( MathNode, 'acos' )
asin = nodeProxy( MathNode, 'asin' )
atan = nodeProxy( MathNode, 'atan' )
ceil = nodeProxy( MathNode, 'ceil' )
clamp = nodeProxy( MathNode, 'clamp' )
cos = nodeProxy( MathNode, 'cos' )
cross = nodeProxy( MathNode, 'cross' )
degrees = nodeProxy( MathNode, 'degrees' )
dFdx = nodeProxy( MathNode, 'dFdx' )
dFdy = nodeProxy( MathNode, 'dFdy' )
distance = nodeProxy( MathNode, 'distance' )
dot = nodeProxy( MathNode, 'dot' )
exp = nodeProxy( MathNode, 'exp' )
exp2 = nodeProxy( MathNode, 'exp2' )
faceforward = nodeProxy( MathNode, 'faceforward' )
floor = nodeProxy( MathNode, 'floor' )
fract = nodeProxy( MathNode, 'fract' )
invert = nodeProxy( MathNode, 'invert' )
inversesqrt = nodeProxy( MathNode, 'inversesqrt' )
length = nodeProxy( MathNode, 'length' )
log = nodeProxy( MathNode, 'log' )
log2 = nodeProxy( MathNode, 'log2' )
max = nodeProxy( MathNode, 'max' )
min = nodeProxy( MathNode, 'min' )
mix = nodeProxy( MathNode, 'mix' )
mod = nodeProxy( MathNode, 'mod' )
negate = nodeProxy( MathNode, 'negate' )
normalize = nodeProxy( MathNode, 'normalize' )
pow = nodeProxy( MathNode, 'pow' )
pow2 = nodeProxy( MathNode, 'pow', 2 )
pow3 = nodeProxy( MathNode, 'pow', 3 )
pow4 = nodeProxy( MathNode, 'pow', 4 )
radians = nodeProxy( MathNode, 'radians' )
reflect = nodeProxy( MathNode, 'reflect' )
refract = nodeProxy( MathNode, 'refract' )
round = nodeProxy( MathNode, 'round' )
saturate = nodeProxy( MathNode, 'saturate' )
sign = nodeProxy( MathNode, 'sign' )
sin = nodeProxy( MathNode, 'sin' )
smoothstep = nodeProxy( MathNode, 'smoothstep' )
sqrt = nodeProxy( MathNode, 'sqrt' )
step = nodeProxy( MathNode, 'step' )
tan = nodeProxy( MathNode, 'tan' )
transformDirection = nodeProxy( MathNode, 'transformDirection' )

EPSILON = float( 1e-6 )
INFINITY = float( 1e6 )

dotNV = saturate( dot( transformedNormalView, positionViewDirection ) )