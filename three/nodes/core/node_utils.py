import base64, types
from three import Color, Matrix3, Matrix4, Vector2, Vector3, Vector4

def getNodeChildren( node:'object' ):
    
    for property in node.__dict__:

        if property.startswith('_'):
            continue

        _object = node.__dict__[property]
        if isinstance(_object, list):
            for index, child in enumerate(_object):
                if child and getattr(child, 'isNode', False):
                    yield property, index, child

        elif _object and getattr(_object, 'isNode', False):
            yield property, None, _object

        elif isinstance(_object, dict):
            for subProperty in _object:
                child = _object[subProperty]
                if child and getattr(child, 'isNode', False):
                    yield property, subProperty, child


def getCacheKey( object ):
    cacheKey = '{'

    if object.isNode:
        cacheKey += object.id

    for property, _ , childNode in getNodeChildren( object ):
        cacheKey += f',{ property[0:-4] }:{ childNode.getCacheKey() }'

    cacheKey += '}'

    return cacheKey

def getValueType( value ):
    if value is None:
        return None
    
    if getattr(value, 'isNode', False):
        return 'node'

    elif type(value) is int or type(value) is float:
        return 'float'

    elif type(value) is bool:
        return 'bool'

    elif type(value) is str:
        return 'string'
    
    elif type(value) is types.FunctionType:
        return 'shader'

    elif isinstance(value, Vector2):
        return 'vec2'

    elif isinstance(value, Vector3):
        return 'vec3'

    elif isinstance(value, Vector4):
        return 'vec4'

    elif isinstance(value, Matrix3):
        return 'mat3'

    elif isinstance(value, Matrix4):
        return 'mat4'

    elif isinstance(value, Color):
        return 'color'

    elif isinstance(value, bytearray):
        return 'ArrayBuffer'

    return None

def getValueFromType(type, *params):
    if type is None:
        return None
    
    last4 = type[-4:]

    if len(params) == 1:
        if last4 == 'vec2':
            params = [ params[ 0 ], params[ 0 ] ]
        elif last4 == 'vec3':
            params = [ params[ 0 ], params[ 0 ], params[ 0 ] ]
        elif last4 == 'vec4':
            params = [ params[ 0 ], params[ 0 ], params[ 0 ], params[ 0 ] ]
    
    if type == 'color':
        return Color( *params )

    elif last4 == 'vec2':
        return Vector2( *params )

    elif last4 == 'vec3':
        return Vector3( *params )

    elif last4 == 'vec4':
        return Vector4( *params )

    elif last4 == 'mat3':
        return Matrix3( *params )

    elif last4 == 'mat4':
        return Matrix4( *params )

    elif type == 'bool':
        return params[ 0 ] or False

    elif type == 'float' or type == 'int' or type == 'uint':
        return params[ 0 ] or 0
    
    elif type == 'string':
        return params[ 0 ] or ''

    elif type == 'ArrayBuffer':
        return bytearray( base64.b64decode( params[0] ) )

    return None