from ..core.node import Node
from ..core.property_node import PropertyNode
from ..core.var_node import VarNode
from ..core.attribute_node import AttributeNode
from ..core.uniform_node import UniformNode
from ..core.bypass_node import BypassNode
from ..core.instance_index_node import InstanceIndexNode
from ..core.context_node import ContextNode
from ..core.function_node import FunctionNode
from ..core.function_call_node import FunctionCallNode
from ..core.code_node import CodeNode
from ..core.expression_node import ExpressionNode
from ..core.vary_node import VaryNode

from ..accessors.buffer_node import BufferNode
from ..accessors.storage_buffer_node import StorageBufferNode
from ..accessors.camera_node import CameraNode
from ..accessors.material_node import MaterialNode
from ..accessors.model_node import ModelNode
from ..accessors.model_view_projection_node import ModelViewProjectionNode
from ..accessors.normal_node import NormalNode
from ..accessors.position_node import PositionNode
from ..accessors.texture_node import TextureNode
from ..accessors.uv_node import UVNode
from ..accessors.reference_node import ReferenceNode
from ..accessors.material_reference_node import MaterialReferenceNode
from ..accessors.point_uv_node import PointUVNode
from ..accessors.userdata_node import UserDataNode

# display
from ..display.front_facing_node import FrontFacingNode

# gpgpu
from ..gpgpu.compute_node import ComputeNode

# math nodes
from ..math.operator_node import OperatorNode
from ..math.cond_node import CondNode
from ..math.math_node import MathNode

# util nodes
from ..utils.array_element_node import ArrayElementNode
from ..utils.convert_node import ConvertNode

# shader node base
from .shader_node import nodeObject, nodeProxy, ConvertType, cacheMaps, getConstNodeType, nodeImmutable

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

# core
# func = lambda *args: nodeObject( FunctionNode( *args ) )

def func(code):
    node = nodeObject(FunctionNode(code))
    node.call = lambda *args: nodeObject(node.call(*args))
    return node


def uniform(nodeOrType):
    nodeType = getConstNodeType(nodeOrType)
    if isinstance(nodeOrType, Node):
        value = nodeOrType.node.value if nodeOrType.node else nodeOrType.value
    else:
        value = nodeOrType

    return nodeObject( UniformNode( value, nodeType ))

attribute = lambda name, nodeType: nodeObject( AttributeNode( name, nodeType ) )
property = lambda name, nodeOrType: nodeObject( PropertyNode( name, getConstNodeType( nodeOrType ) ) )

bypass = nodeProxy( BypassNode )
code = nodeProxy( CodeNode )
context = nodeProxy( ContextNode )
expression = nodeProxy( ExpressionNode )
call = nodeProxy( FunctionCallNode )
instanceIndex = nodeImmutable( InstanceIndexNode )
label = nodeProxy( VarNode )
temp = label
vary = nodeProxy( VaryNode )


#accesors
buffer = lambda value, nodeOrType, count: nodeObject( BufferNode( value, getConstNodeType( nodeOrType ), count ) )
storage = lambda value, nodeOrType, count: nodeObject( StorageBufferNode( value, getConstNodeType( nodeOrType ), count ) )

cameraProjectionMatrix = nodeImmutable(CameraNode, CameraNode.PROJECTION_MATRIX )
cameraViewMatrix = nodeImmutable(CameraNode, CameraNode.VIEW_MATRIX)
cameraNormalMatrix = nodeImmutable(CameraNode, CameraNode.NORMAL_MATRIX)
cameraWorldMatrix = nodeImmutable(CameraNode, CameraNode.WORLD_MATRIX)
cameraPosition = nodeImmutable(CameraNode, CameraNode.POSITION)

materialAlphaTest = nodeImmutable(MaterialNode, MaterialNode.ALPHA_TEST)
materialColor = nodeImmutable(MaterialNode, MaterialNode.COLOR)
materialEmissive = nodeImmutable(MaterialNode, MaterialNode.EMISSIVE)
materialOpacity = nodeImmutable(MaterialNode, MaterialNode.OPACITY)
# materialSpecular = nodeImmutable(MaterialNode, MaterialNode.SPECULAR)
materialRoughness = nodeImmutable(MaterialNode, MaterialNode.ROUGHNESS)
materialMetalness = nodeImmutable(MaterialNode, MaterialNode.METALNESS)
materialRotation = nodeImmutable(MaterialNode, MaterialNode.ROTATION)

diffuseColor = nodeImmutable(PropertyNode, 'DiffuseColor', 'vec4')
roughness = nodeImmutable(PropertyNode, 'Roughness', 'float')
metalness = nodeImmutable(PropertyNode, 'Metalness', 'float')
alphaTest = nodeImmutable(PropertyNode, 'AlphaTest', 'float')
specularColor = nodeImmutable(PropertyNode, 'SpecularColor', 'color')

reference = lambda name, nodeOrType, object=None: nodeObject(ReferenceNode(name, getConstNodeType(nodeOrType), object))
materialReference = lambda name, nodeOrType, material=None: nodeObject(MaterialReferenceNode(name, getConstNodeType(nodeOrType), material))
userData = lambda name, inputType, userData=None: nodeObject(UserDataNode(name, inputType, userData))

modelViewProjection = nodeProxy(ModelViewProjectionNode)

normalGeometry = nodeImmutable(NormalNode, NormalNode.GEOMETRY)
normalLocal = nodeImmutable(NormalNode, NormalNode.LOCAL)
normalWorld = nodeImmutable(NormalNode, NormalNode.WORLD)
normalView = nodeImmutable(NormalNode, NormalNode.VIEW)
transformedNormalView = nodeImmutable(VarNode, normalView, 'TransformedNormalView')

modelViewMatrix = nodeImmutable(ModelNode, ModelNode.VIEW_MATRIX)
modelNormalMatrix = nodeImmutable(ModelNode, ModelNode.NORMAL_MATRIX)
modelWorldMatrix = nodeImmutable(ModelNode, ModelNode.WORLD_MATRIX)
modelPosition = nodeImmutable(ModelNode, ModelNode.POSITION)
modelViewPosition = nodeImmutable(ModelNode, ModelNode.VIEW_POSITION)

positionGeometry = nodeImmutable(PositionNode, PositionNode.GEOMETRY)
positionLocal = nodeImmutable(PositionNode, PositionNode.LOCAL)
positionWorld = nodeImmutable(PositionNode, PositionNode.WORLD)
positionView = nodeImmutable(PositionNode, PositionNode.VIEW)
positionViewDirection = nodeImmutable(PositionNode, PositionNode.VIEW_DIRECTION)

texture = nodeProxy(TextureNode)
sampler = lambda texture: nodeObject(ConvertNode(texture if texture.isNode else TextureNode(texture), 'sampler'))
uv = lambda *args: nodeObject(UVNode(*args))
pointUV = nodeImmutable(PointUVNode)


# gpgpu

compute = lambda node, count, workgroupSize = None: nodeObject(ComputeNode(nodeObject(node), count, workgroupSize))

# math

EPSILON = float( 1e-6 )
INFINITY = float( 1e6 )

cond = nodeProxy( CondNode )

add = nodeProxy(OperatorNode, '+')
sub = nodeProxy(OperatorNode, '-')
mul = nodeProxy(OperatorNode, '*')
div = nodeProxy(OperatorNode, '/')
remainder = nodeProxy(OperatorNode, '%')
equal = nodeProxy(OperatorNode, '==')
assign = nodeProxy(OperatorNode, '=')
lessThan = nodeProxy(OperatorNode, '<')
greaterThan = nodeProxy(OperatorNode, '>')
lessThanEqual = nodeProxy(OperatorNode, '<=')
greaterThanEqual = nodeProxy(OperatorNode, '>=')
and_ = nodeProxy(OperatorNode, '&&')
or_ = nodeProxy(OperatorNode, '||')
xor = nodeProxy(OperatorNode, '^^')
bitAnd = nodeProxy(OperatorNode, '&')
bitOr = nodeProxy(OperatorNode, '|')
bitXor = nodeProxy(OperatorNode, '^')
shiftLeft = nodeProxy(OperatorNode, '<<')
shiftRight = nodeProxy(OperatorNode, '>>')

radians = nodeProxy( MathNode, MathNode.RADIANS )
degrees = nodeProxy( MathNode, MathNode.DEGREES )
exp = nodeProxy( MathNode, MathNode.EXP )
exp2 = nodeProxy( MathNode, MathNode.EXP2 )
log = nodeProxy( MathNode, MathNode.LOG )
log2 = nodeProxy( MathNode, MathNode.LOG2 )
sqrt = nodeProxy( MathNode, MathNode.SQRT )
inversesqrt = nodeProxy( MathNode, MathNode.INVERSE_SQRT )
floor = nodeProxy( MathNode, MathNode.FLOOR )
ceil = nodeProxy( MathNode, MathNode.CEIL )
normalize = nodeProxy( MathNode, MathNode.NORMALIZE )
fract = nodeProxy( MathNode, MathNode.FRACT )
sin = nodeProxy( MathNode, MathNode.SIN )
cos = nodeProxy( MathNode, MathNode.COS )
tan = nodeProxy( MathNode, MathNode.TAN )
asin = nodeProxy( MathNode, MathNode.ASIN )
acos = nodeProxy( MathNode, MathNode.ACOS )
atan = nodeProxy( MathNode, MathNode.ATAN )
abs = nodeProxy( MathNode, MathNode.ABS )
sign = nodeProxy( MathNode, MathNode.SIGN )
length = nodeProxy( MathNode, MathNode.LENGTH )
negate = nodeProxy( MathNode, MathNode.NEGATE )
invert = nodeProxy( MathNode, MathNode.INVERT )
dFdx = nodeProxy( MathNode, MathNode.DFDX )
dFdy = nodeProxy( MathNode, MathNode.DFDY )
saturate = nodeProxy( MathNode, MathNode.SATURATE )
round = nodeProxy( MathNode, MathNode.ROUND )

atan2 = nodeProxy(MathNode, MathNode.ATAN2)
min = nodeProxy(MathNode, MathNode.MIN)
max = nodeProxy(MathNode, MathNode.MAX)
mod = nodeProxy(MathNode, MathNode.MOD)
step = nodeProxy(MathNode, MathNode.STEP)
reflect = nodeProxy(MathNode, MathNode.REFLECT)
distance = nodeProxy(MathNode, MathNode.DISTANCE)
dot = nodeProxy(MathNode, MathNode.DOT)
cross = nodeProxy(MathNode, MathNode.CROSS)
pow = nodeProxy(MathNode, MathNode.POW)
pow2 = nodeProxy(MathNode, MathNode.POW, 2)
pow3 = nodeProxy(MathNode, MathNode.POW, 3)
pow4 = nodeProxy(MathNode, MathNode.POW, 4)
transformDirection = nodeProxy(MathNode, MathNode.TRANSFORM_DIRECTION)

mix = nodeProxy( MathNode, MathNode.MIX )
clamp = nodeProxy( MathNode, MathNode.CLAMP )
refract = nodeProxy( MathNode, MathNode.REFRACT )
smoothstep = nodeProxy( MathNode, MathNode.SMOOTHSTEP )
faceforward = nodeProxy( MathNode, MathNode.FACEFORWARD )

# display

frontFacing = nodeImmutable(FrontFacingNode)
faceDirection = sub(mul(float(frontFacing), 2), 1)

# utils

element = nodeProxy(ArrayElementNode)

# miscellaneous

dotNV = saturate(dot(transformedNormalView, positionViewDirection))
transformedNormalWorld = normalize(transformDirection(transformedNormalView, cameraViewMatrix))
