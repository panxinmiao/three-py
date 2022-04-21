import three
from three import Color, Matrix3, Matrix4, Vector2, Vector3, Vector4

def getNodesKeys( object:'object' ):
    props = []

    for name in object.__dict__:
        value = object.__dict__[ name ]

        if value and isinstance(value, three.Node) == True:
            props.append( name )

    return props

def getValueType( value ):
    if type(value) == int or type(value) == float:
        return 'float'

    elif type(value) == bool:
        return 'bool'

    elif value and value.isVector2:
        return 'vec2'

    elif value and value.isVector3:
        return 'vec3'

    elif value and value.isVector4:
        return 'vec4'

    elif value and value.isMatrix3:
        return 'mat3'

    elif value and value.isMatrix4:
        return 'mat4'

    elif value and value.isColor:
        return 'color'

    return None

#  const getValueFromType = ( type, ...params ) => {

# 	const last4 = type?.slice( -4 );

# 	if ( type === 'color' ) {

# 		return new Color( ...params );

# 	} else if ( last4 === 'vec2' ) {

# 		return new Vector2( ...params );

# 	} else if ( last4 === 'vec3' ) {

# 		return new Vector3( ...params );

# 	} else if ( last4 === 'vec4' ) {

# 		return new Vector4( ...params );

# 	} else if ( last4 === 'mat3' ) {

# 		return new Matrix3( ...params );

# 	} else if ( last4 === 'mat4' ) {

# 		return new Matrix4( ...params );

# 	} else if ( type === 'bool' ) {

# 		return false;

# 	} else if ( ( type === 'float' ) || ( type === 'int' ) || ( type === 'uint' ) ) {

# 		return 0;

# 	}

# 	return null;

# };

def getValueFromType(type, *params):
    if type is None:
        return None
    
    last4 = type[-4:]

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
        return False

    elif type == 'float' or type == 'int' or type == 'uint':
        return 0

    return None
