import random
from ..core.node import Node
from ..shadernode.shader_node_base_elements import attribute, float
from ...core.instanced_buffer_attribute import InstancedBufferAttribute
from ...structure import Float32Array
from ...math import math_utils

class RangeNode(Node):

    def __init__(self, min, max) -> None:
        super().__init__()

        self.min = min
        self.max = max

    def getVectorLength(self):
        min = self.min
        length = 1
        if min.isVector2:
            length = 2
        elif min.isVector3:
            length = 3
        elif min.isVector4:
            length = 4
        elif min.isColor:
            length = 3

        return length

    def getNodeType( self, builder ):
        return builder.getTypeFromLength( self.getVectorLength() ) if builder.object.isInstancedMesh else 'float'

    def construct( self, builder ):
        min = self.min
        max = self.max
        object = builder.object
        geometry = builder.geometry

        vectorLength = self.getVectorLength()
        attributeName = 'node' + str(self.id)

        output = None

        if object.isInstancedMesh:
            length = vectorLength * object.count
            array = Float32Array( length )

            if vectorLength ==1:
                for i in range(length):
                    array[ i ] = math_utils.lerp( min, max, random.random() )

            elif min.isColor:
                for i in range(0, length, 3):
                    array[ i ] = math_utils.lerp( min.r, max.r, random.random() )
                    array[ i + 1 ] = math_utils.lerp( min.g, max.g, random.random() )
                    array[ i + 2 ] = math_utils.lerp( min.b, max.b, random.random() )

            else:
                for i in range(length):
                    index = i % vectorLength
                    minValue = min.getComponent( index )
                    maxValue = max.getComponent( index )
                    array[ i ] = math_utils.lerp( minValue, maxValue, random.random() )


            geometry.setAttribute( attributeName, InstancedBufferAttribute( array, vectorLength ) )

            output = attribute( attributeName, builder.getTypeFromLength( vectorLength ) )

        else:
            output = float( 0 )

        return output