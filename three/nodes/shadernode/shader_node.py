import re, math
import weakref

from ..core.node import Node
from ..core.const_node import ConstNode
from ..core.stack_node import StackNode
from ..utils.split_node import SplitNode
from ..utils.array_element_node import ArrayElementNode
from ..utils.convert_node import ConvertNode
from ..utils.join_node import JoinNode
from ..core.node_utils import getValueFromType
from ..math.operator_node import OperatorNode
from ..math.math_node import MathNode

nodeObjectsCacheMap = weakref.WeakKeyDictionary()

def ShaderNodeObject(obj):
    if isinstance(obj, int) or isinstance(obj, float) or isinstance(obj, bool):
        return ShaderNodeObject(getAutoTypedConstNode(obj))
    elif isinstance(obj, dict):
        return ShaderNodeObjects(obj)
    elif isinstance(obj, object):
        if isinstance(obj, Node):
            nodeObject = nodeObjectsCacheMap.get(obj, None)
            if not nodeObject:
                nodeObject = ProxyNode( obj )
                nodeObjectsCacheMap[obj] = nodeObject
                nodeObjectsCacheMap[nodeObject] = nodeObject
            return nodeObject
    return obj

def ShaderNodeObjects( objects: dict ):
    for name in objects:
        value = objects[name]
        objects[name] = ShaderNodeObject(value)
    
    return objects

def ShaderNodeArray( array ):
    if isinstance(array, tuple):
        array = list(array)
    for i, val in enumerate(array):
        array[i] = ShaderNodeObject(val)

    return array

def ShaderNodeProxy( NodeClass, scope = None, factor = None, settings = None ):

    def assignNode( node ):
        if settings:
            node.__dict__.update(settings)
        return nodeObject(node)

    if scope is None:
        return lambda *params : assignNode( NodeClass( *ShaderNodeArray( params ) ) )
    
    elif factor is not None:
        factor = ShaderNodeObject(factor)
        return lambda *params: assignNode(NodeClass(scope, *ShaderNodeArray(params), factor))

    else:
        return lambda *params: assignNode(NodeClass(scope, *ShaderNodeArray(params)))


def ShaderNodeImmutable(NodeClass, *args):
    return nodeObject(NodeClass(*nodeArray(args)))


nodeObject = ShaderNodeObject
nodeObjects = ShaderNodeObjects
nodeArray = ShaderNodeArray
nodeProxy = ShaderNodeProxy
nodeImmutable = ShaderNodeImmutable

# TODO: move this logic to Node object?
class ProxyNode:
    p1 = re.compile(r'^[xyzwrgbastpq]{1,4}$')
    p2 = re.compile(r'^\d+$')

    def __init__(self, node) -> None:
        object.__setattr__(self, 'ori_node', node)

    def __getattribute__(self, prop: str):
        node = object.__getattribute__(self, 'ori_node')
        if prop == 'ori_node':
            return node
        if type(prop) == str and getattr(node, prop) == None:
            if ProxyNode.p1.match(prop):
                prop = re.sub(r"r|s", 'x', prop)
                prop = re.sub(r"g|t", 'y', prop)
                prop = re.sub(r"b|p", 'z', prop)
                prop = re.sub(r"a|q", 'w', prop)
                
                return ShaderNodeObject(SplitNode(node, prop))
            
            elif ProxyNode.p2.match(prop):
                return ShaderNodeObject(ArrayElementNode(node, ConstNode(int(prop), 'uint')))
                
        return getattr(node, prop)

    def __repr__(self) -> str:
        return f'Proxy({str(self.ori_node)})'

    def __setattr__(self, prop: str, value):
        node = object.__getattribute__(self, 'ori_node')
        setattr(node, prop, value)

    def __getitem__(self, prop):
        return ProxyNode.__getattribute__(self, str(prop))

    def __add__(self, other):
        return nodeProxy(OperatorNode, '+')(self, other)
    
    def __radd__(self, other):
        return nodeProxy(OperatorNode, '+')(other, self)

    def __sub__(self, other):
        return nodeProxy(OperatorNode, '-')(self, other)
    
    def __rsub__(self, other):
        return nodeProxy(OperatorNode, '-')(other, self)

    def __mul__(self, other):
        return nodeProxy(OperatorNode, '*')(self, other)
    
    def __rmul__(self, other):
        return nodeProxy(OperatorNode, '*')(other, self)

    def __div__(self, other):
        return nodeProxy(OperatorNode, '/')(self, other)
    
    def __rdiv__(self, other):
        return nodeProxy(OperatorNode, '/')(other, self)

    def __mod__(self, other):
        return nodeProxy(OperatorNode, '%')(self, other)

    # def __eq__(self, other):
    #     return nodeProxy(OperatorNode, '==')(self, other)

    def __neg__(self):
        return nodeProxy(MathNode, 'negate')(self)

    def __lt__(self, other):
        return nodeProxy(OperatorNode, '<')(self, other)

    def __gt__(self, other):
        return nodeProxy(OperatorNode, '>')(self, other)

    def __le__(self, other):
        return nodeProxy(OperatorNode, '<=')(self, other)

    def __ge__(self, other):
        return nodeProxy(OperatorNode, '>=')(self, other)

    def __or__(self, other):
        return nodeProxy(OperatorNode, '|')(self, other)

    def __and__(self, other):
        return nodeProxy(OperatorNode, '&')(self, other)

    def __xor__(self, other):
        return nodeProxy(OperatorNode, '^')(self, other)

    def __lshift__(self, other):
        return nodeProxy(OperatorNode, '<<')(self, other)

    def __rshift__(self, other):
        return nodeProxy(OperatorNode, '>>')(self, other)

    def __pow__(self, other):
        # TODO: check if this is correct
        return nodeProxy(MathNode, 'pow')(self, other)


class ShaderNode(Node):

    def __init__(self, func) -> None:
        if not callable(func):
            raise ValueError("ShaderNode func must be callable")
        super().__init__()
        self.func = func

    def call(self, *args, **kwds):
        return self(*args, **kwds)

    def __call__(self, *args, **kwds):
        # 
        args = nodeArray(args)
        kwds = nodeObjects(kwds)

        return nodeObject(self.func(*args, **kwds))

    def getNodeType(self, builder):
        outputNode = builder.getNodeProperties(self).outputNode
        return outputNode.getNodeType( builder ) if outputNode else super().getNodeType( builder )

    def construct(self, builder):
        stackNode = StackNode()
        argLength = self.func.__code__.co_argcount
        stackNode.outputNode = self.call(*[{}, stackNode, builder][:argLength])
        return stackNode

    # def generate(self, builder, output):
    #     nodeCall = self.call( {}, builder )
    #     if nodeCall is None:
    #         return ""
    #     return builder.format( nodeCall.build( builder ), nodeCall.getNodeType( builder ), output )


bools = [ False, True ]
uints = [ 0, 1, 2, 3 ]
ints = [ -1, -2 ]
floats = [ 0.5, 1.5, 1 / 3, 1e-6, 1e6, math.pi, math.pi * 2, 1 / math.pi, 2 / math.pi, 1 / ( math.pi * 2 ), math.pi / 2 ]

boolsCacheMap = {}
for _bool in bools:
    boolsCacheMap[_bool] = ConstNode( _bool )

uintsCacheMap = {}
intsCacheMap = {}
floatsCacheMap = {}

for uint in uints:
    uintsCacheMap[uint] = ConstNode( uint, 'uint' )
    intsCacheMap[uint] = ConstNode( uint, 'int' )
    floatsCacheMap[uint] = ConstNode( float(uint) )

for _int in ints:
    intsCacheMap[_int] = ConstNode( _int, 'int' )
    floatsCacheMap[_int] = ConstNode( float(_int) )

for _float in floats:
    floatsCacheMap[_float] = ConstNode( _float )
    floatsCacheMap[-_float] = ConstNode( -_float )

cacheMaps = {
    'bool': boolsCacheMap,
    'uint': uintsCacheMap,
    'int': intsCacheMap,
    'float': floatsCacheMap
}

constNodesCacheMap = {**boolsCacheMap, **floatsCacheMap}

def getAutoTypedConstNode( value ):
    if value in constNodesCacheMap:
        return constNodesCacheMap[value]
    elif isinstance(value, Node):
        return value
    else:
        return ConstNode( value )
        

class ConvertType:

    def __init__(self, type, cacheMap = None ) -> None:
        self.type = type
        self.cacheMap = cacheMap

    def __call__(self, *args, **kwds):
        # if args:
        params = list(args)
        type = self.type
        if len(params) == 0:
            return nodeObject( ConstNode( getValueFromType( type ), type ) )
        else:
            if type == 'color' and not isinstance( params[ 0 ], Node):
                params = [ getValueFromType( type, *params ) ]

            if len(params) == 1 and self.cacheMap is not None and params[ 0 ] in self.cacheMap:
                return self.cacheMap[ params[ 0 ]]

            nodes = [getAutoTypedConstNode( p ) for p in params]
            
            if len(nodes) == 1:
                return nodeObject( nodes[ 0 ] if nodes[ 0 ].nodeType == type else ConvertNode( nodes[ 0 ], type ) )

        
            return nodeObject(JoinNode(nodes, type)) 


def getConstNodeType(value):
    return getattr(value, 'nodeType', None) or getattr(value, 'convertTo', None) or (value if type(value) == str else None)
    # if isinstance(value, NoneAttribute):
    #     return value.nodeType or value.convertTo or None
    # else:
    #     return value if type(value) == str else None


