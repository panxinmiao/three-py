#from three.renderer.nodes import Node
from .node import Node
from three import Color, Matrix3, Matrix4, Vector2, Vector3, Vector4
from warnings import warn


def getValueType( value ):
    if value is None:
        return None

    if type(value) == int or type(value) == float:
        return 'float'
    elif type(value) == bool:
        return 'bool'

    elif value.isVector2:
        return 'vec2'

    elif value.isVector3:
        return 'vec3'

    elif value.isVector4:
        return 'vec4'

    elif value.isMatrix3:
        return 'mat3'

    elif value.isMatrix4:
        return 'mat4'

    elif value.isColor:
        return 'color'

    return None

def getValueFromType( type ):

    if type == 'color':

        return Color()

    elif type == 'vec2':

        return Vector2()

    elif type == 'vec3':

        return Vector3()

    elif type == 'vec4':

        return Vector4()

    elif type == 'mat3':

        return Matrix3()

    elif type == 'mat4':

        return Matrix4()

    return None

class InputNode(Node):
    def __init__(self, value, nodeType = None ) -> None:
        super().__init__(nodeType)
        self._value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if value is None:
            warn('InputNode.value should be not None.')
            value = 0
        self._value = value

    def getNodeType( self, *args):  #  /*builder*/
        if self.nodeType is None:
            return getValueType( self.value )
        return self.nodeType

    def getInputType( self, builder ):
        return self.getNodeType( builder )


    def serialize(self, data ):
        super().serialize( data )
        if self.value and hasattr(self.value, 'toArray'):
            data.value = self.value.toArray()
        else:
            data.value = self.value

        data.valueType = getValueType( self.value )
        data.nodeType = self.nodeType


    def deserialize( self, data ):
        super().deserialize( data )

        self.nodeType = data.nodeType
        self.value = getValueFromType( data.valueType )

        if self.value and hasattr(self.value, 'fromArray'):
            self.value = self.value.fromArray( data.value )
        else:
            self.value = data.value


    def generate( self, *args ):  # builder, output
        warn('Abstract function.')
