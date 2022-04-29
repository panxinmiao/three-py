import re, math
import weakref
# from three.renderer.nodes import FloatNode, Node, SplitNode, ArrayElementNode
from ..core.node import Node
from ..core.const_node import ConstNode
from ..utils.split_node import SplitNode
from ..utils.array_element_node import ArrayElementNode
from ..utils.convert_node import ConvertNode
from ..utils.join_node import JoinNode
from ..core.node_utils import getValueFromType
from ..math.operator_node import OperatorNode
from ..math.math_node import MathNode

nodeObjectsCacheMap = weakref.WeakKeyDictionary()


def shader_node_object(obj):
    if isinstance(obj, int) or isinstance(obj, float) or isinstance(obj, bool):
        return shader_node_object( getAutoTypedConstNode( obj ) )
    elif isinstance(obj, object):
        if isinstance(obj, Node) and not isinstance(obj, ProxyNode):
            nodeObject = nodeObjectsCacheMap.get(obj, None)
            if not nodeObject:
                nodeObject = ProxyNode( obj )
                nodeObjectsCacheMap[obj] = nodeObject
                nodeObjectsCacheMap[nodeObject] = nodeObject
            return nodeObject
    return obj

def shader_node_objects( objects: dict ):
    for name in objects:
        value = objects[name]
        objects[name] = shader_node_object(value)
    
    return objects

def shader_node_array( array ):
    if isinstance(array, tuple):
        array = list(array)
    for i, val in enumerate(array):
        array[i] = shader_node_object( val )

    return array

def shader_node_proxy( NodeClass, scope = None, factor = None ):
    if scope is None:
        return lambda *params : shader_node_object( NodeClass( *shader_node_array( params ) ) )
    
    elif factor is None:
        return lambda *params : shader_node_object( NodeClass( scope, *shader_node_array( params ) ) )

    else:
        factor = shader_node_object( factor )
        return lambda *params : shader_node_object( NodeClass( scope, *shader_node_array( params ), factor ) )


class ProxyNode:
    p1 = re.compile(r'^[xyzwrgbastpq]{1,4}$')
    p2 = re.compile(r'^\d+$')

    def __init__(self, node) -> None:
        self.ori_node = node

    def __getattribute__(self, prop: str):
        node = object.__getattribute__(self, 'ori_node')        
        if type(prop) == str and getattr(node, prop) == None:
            if ProxyNode.p1.match(prop):
                prop = re.sub(r"r|s", 'x', prop)
                prop = re.sub(r"g|t", 'y', prop)
                prop = re.sub(r"b|p", 'z', prop)
                prop = re.sub(r"a|q", 'w', prop)
                
                return shader_node_object( SplitNode( node, prop ) )
            
            elif ProxyNode.p2.match(prop):
                return shader_node_object( ArrayElementNode( node, ConstNode( float( prop ), 'uint' ) ) )
                #return shader_node_object( ArrayElementNode( node, uint( float( prop ), 'uint' ) ) )
                
        return getattr(node, prop)

    def __add__(self, other):
        return nodeProxy(OperatorNode, '+')(self, other)

    def __sub__(self, other):
        return nodeProxy(OperatorNode, '-')(self, other)

    def __mul__(self, other):
        return nodeProxy(OperatorNode, '*')(self, other)

    def __div__(self, other):
        return nodeProxy(OperatorNode, '/')(self, other)

    def __mod__(self, other):
        return nodeProxy(OperatorNode, '%')(self, other)

    # def __eq__(self, other):
    #     return nodeProxy(OperatorNode, '==')(self, other)

    def __neg__(self):
        return nodeProxy(MathNode, 'negate')(self)

    def __lq__(self, other):
        return nodeProxy(OperatorNode, '<')(self, other)

    def __gq__(self, other):
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

    # def __getattr__(self, name):
    #     node = object.__getattribute__(self, 'node')
    #     return getattr(node, name)

nodeObject = shader_node_object
nodeObjects = shader_node_objects
nodeArray = shader_node_array
nodeProxy = shader_node_proxy

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
            if type == 'color' and isinstance( params[ 0 ], Node):
                params = [ getValueFromType( type, *params ) ]

            if len(params) == 1 and self.cacheMap is not None and params[ 0 ] in self.cacheMap:
                return self.cacheMap[ params[ 0 ]]

            nodes = [getAutoTypedConstNode( p ) for p in params]
            
            if len(nodes) == 1:
                return nodeObject( nodes[ 0 ] if nodes[ 0 ].nodeType == type else ConvertNode( nodes[ 0 ], type ) )

        
            return nodeObject(ConvertNode( JoinNode( nodes ), type )) 

