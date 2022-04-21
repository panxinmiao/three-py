#from array import array
from ..structure import NoneAttribute, TypedArray, Dict
from ..structure import Int8Array, Uint8Array,  Int16Array, Uint16Array, Int32Array, Uint32Array, BigInt64Array, BigUint64Array ,Float32Array, Float64Array
from copy import copy
from ..math import Color, Vector2, Vector3, Vector4, Matrix3, Matrix4
from warnings import warn


_vector = Vector3()
_vector2 = Vector2()

class BufferAttribute(NoneAttribute):
    def __init__(self, ary: TypedArray, itemSize, normalized = False) -> None:

        if not isinstance(ary, TypedArray):
            raise TypeError('array should be a Typed Array')
        
        self.name = ''

        # TODO use numpy.ndarray & dtype?
        self.array = ary

        self.itemSize = itemSize
        self._count = 0 if ary is None else int(len(ary)/itemSize)
        self.normalized = normalized
        self._need_update = False

        #self.usage
        self.updateRange = Dict({ 'offset':0, 'count': -1})
        self.version = 0

    @property
    def count(self):
        return self._count

    @property
    def needsUpdate( self ):
        return self._need_update

    @needsUpdate.setter
    def needsUpdate( self, value):
        self._need_update = value
        if value:
            self.version += 1

    def onUploadCallback(self):
        pass

    def onUpload( self, callback ):
        self.onUploadCallback = callback
        return self


    def setUsage( self, value ):
        self.usage = value
        return self

    def copy( self, source:'BufferAttribute' ):
        self.name = source.name
        #self.array.frombytes(source.array.tobytes)
        self.array = source.array.copy()
        self.itemSize = source.itemSize
        self.count = source.count
        self.normalized = source.normalized
        
        self.usage = source.usage

        return self

    def copyAt(self, index1, attribute: 'BufferAttribute', index2 ):
        index1 *= self.itemSize
        index2 *= attribute.itemSize

        for i in range(self.itemSize):
            self.array[ index1 + i ] = attribute.array[ index2 + i ]

        return self

    def copyArray( self, array:TypedArray ):
        self.array.copy_buffer(array.buffer)
        return self

    def copyColorsArray( self, colors ):
        array = self.array
        offset = 0

        for i in range(len(colors)):
            color = colors[ i ]
            if color is None:
                warn( f'THREE.BufferAttribute.copyColorsArray(): color is undefined, {i}' )
                color = Color()
            array[ offset  ] = color.r
            offset +=1
            array[ offset  ] = color.g
            offset +=1
            array[ offset  ] = color.b
            offset +=1

        return self


    def copyVector2sArray( self, vectors ):
        array = self.array
        offset = 0

        for i in range(len(vectors)):

            vector = vectors[ i ]
            if vector is None:
                warn( f'THREE.BufferAttribute.copyVector2sArray(): Vector is undefined, {i}' )
                vector = Vector2()
            array[ offset  ] = vector.x
            offset +=1
            array[ offset  ] = vector.y
            offset +=1

        return self

    def copyVector3sArray( self, vectors ):
        array = self.array
        offset = 0

        for i in range(len(vectors)):

            vector = vectors[ i ]
            if vector is None:
                warn( f'THREE.BufferAttribute.copyVector3sArray(): Vector is undefined, {i}' )
                vector = Vector3()
            array[ offset  ] = vector.x
            offset +=1
            array[ offset  ] = vector.y
            offset +=1
            array[ offset  ] = vector.z
            offset +=1

        return self

    def copyVector4sArray( self, vectors ):
        array = self.array
        offset = 0

        for i in range(len(vectors)):

            vector = vectors[ i ]
            if vector is None:
                warn( f'THREE.BufferAttribute.copyVector4sArray(): Vector is undefined, {i}' )
                vector = Vector4()
            array[ offset  ] = vector.x
            offset +=1
            array[ offset  ] = vector.y
            offset +=1
            array[ offset  ] = vector.z
            offset +=1
            array[ offset  ] = vector.w
            offset +=1

        return self

    def applyMatrix3( self, m: Matrix3 ):
        if self.itemSize == 2:
            for i in range(self.count):
                _vector2.fromBufferAttribute( self, i )
                _vector2.applyMatrix3( m )
                self.setXY( i, _vector2.x, _vector2.y )

        elif self.itemSize == 3:
            for i in range(self.count):
                _vector.fromBufferAttribute( self, i )
                _vector.applyMatrix3( m )

                self.setXYZ( i, _vector.x, _vector.y, _vector.z )

        return self

    def applyMatrix4( self, m: Matrix4 ):

        for i in range(self.count):

            _vector.x = self.getX( i )
            _vector.y = self.getY( i )
            _vector.z = self.getZ( i )

            _vector.applyMatrix4( m )

            self.setXYZ( i, _vector.x, _vector.y, _vector.z )

        return self

    def applyNormalMatrix( self, m ):

        for i in range(self.count):

            _vector.x = self.getX( i )
            _vector.y = self.getY( i )
            _vector.z = self.getZ( i )

            _vector.applyNormalMatrix( m )

            self.setXYZ( i, _vector.x, _vector.y, _vector.z )

        return self

    def transformDirection( self, m ):

        for i in range(self.count):

            _vector.x = self.getX( i )
            _vector.y = self.getY( i )
            _vector.z = self.getZ( i )

            _vector.transformDirection( m )

            self.setXYZ( i, _vector.x, _vector.y, _vector.z )

        return self


    def set(self, value, offset = 0):
        self.array[offset] = value
        return self
    
    def getX( self, index ):
        return self.array[ index * self.itemSize ]

    def setX( self, index, x ):
        self.array[ index * self.itemSize ] = x
        return self

    def getY( self, index ):
        return self.array[ index * self.itemSize + 1]

    def setY( self, index, y ):
        self.array[ index * self.itemSize + 1] = y
        return self

    def getZ( self, index ):
        return self.array[ index * self.itemSize + 2]

    def setZ( self, index, z ):
        self.array[ index * self.itemSize + 2] = z
        return self

    def getW( self, index ):
        return self.array[ index * self.itemSize + 3]

    def setW( self, index, w ):
        self.array[ index * self.itemSize + 3] = w
        return self

    def setXY( self, index, x, y ):
        index *= self.itemSize

        self.array[ index + 0 ] = x
        self.array[ index + 1 ] = y

        return self

    def setXYZ( self, index, x, y, z ):

        index *= self.itemSize

        self.array[ index + 0 ] = x
        self.array[ index + 1 ] = y
        self.array[ index + 2 ] = z

        return self

    def setXYZW( self, index, x, y, z, w ):

        index *= self.itemSize

        self.array[ index + 0 ] = x
        self.array[ index + 1 ] = y
        self.array[ index + 2 ] = z
        self.array[ index + 3 ] = w

        return self

    def onUpload( self, callback ):
        self.onUploadCallback = callback
        return self

    def clone(self):
        return BufferAttribute( self.array, self.itemSize ).copy( self )


    #TODO set and transform


class Int8BufferAttribute(BufferAttribute):

    def __init__(self, ary, itemSize, normalized=False) -> None:
        super().__init__( Int8Array( ary ), itemSize, normalized)



class Uint8BufferAttribute(BufferAttribute):

    def __init__(self, ary, itemSize, normalized=False) -> None:
        super().__init__( Uint8Array( ary ), itemSize, normalized)


class Uint8ClampedBufferAttribute(BufferAttribute):
    def __init__(self, ary, itemSize, normalized=False) -> None:
        super().__init__( Uint8Array( ary ), itemSize, normalized)


# class Int16BufferAttribute(BufferAttribute):
#     def __init__(self, ary, itemSize, normalized=False) -> None:
#         super().__init__( Uint8ClampedArray( ary ), itemSize, normalized)


class Uint16BufferAttribute(BufferAttribute):
    def __init__(self, ary, itemSize, normalized=False) -> None:
        super().__init__( Uint16Array( ary ), itemSize, normalized)

class Int32BufferAttribute(BufferAttribute):
    def __init__(self, ary, itemSize, normalized=False) -> None:
        super().__init__( Int32Array( ary ), itemSize, normalized)

class Uint32BufferAttribute(BufferAttribute):
    def __init__(self, ary, itemSize, normalized=False) -> None:
        super().__init__( Uint32Array( ary ), itemSize, normalized)

# class Float16BufferAttribute(BufferAttribute):
#     def __init__(self, ary, itemSize, normalized=False) -> None:
#         super().__init__( Float16Array( ary ), itemSize, normalized)


class Float32BufferAttribute(BufferAttribute):
    def __init__(self, ary, itemSize, normalized=False) -> None:
        super().__init__( Float32Array( ary ), itemSize, normalized)

class Float64BufferAttribute(BufferAttribute):
    def __init__(self, ary, itemSize, normalized=False) -> None:
        super().__init__( Float64Array( ary ), itemSize, normalized)


    
