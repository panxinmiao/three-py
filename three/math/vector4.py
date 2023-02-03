import three
import math, random
from array import array
from ..structure import NoneAttribute, Float32Array

class Vector4(NoneAttribute):

    isVector4 = True

    def __init__(self, x: float = 0, y: float = 0, z: float = 0, w: float = 0) -> None:

        self._buffer = array('f', [x, y, z, w])

        # self.x = x
        # self.y = y
        # self.z = z
        # self.w = w

    @property
    def x(self):
        return self._buffer[0]
    
    @x.setter
    def x(self, value):
        self._buffer[0] = value
    
    @property
    def y(self):
        return self._buffer[1]
    
    @y.setter
    def y(self, value):
        self._buffer[1] = value
    
    @property
    def z(self):
        return self._buffer[2]
    
    @z.setter
    def z(self, value):
        self._buffer[2] = value
    
    @property
    def w(self):
        return self._buffer[3]
    
    @w.setter
    def w(self, value):
        self._buffer[3] = value

    @property
    def width(self):
        return self.z

    @width.setter
    def width(self, value):
        self.z = value

    @property
    def height(self):
        return self.w

    @height.setter
    def height(self, value):
        self.w = value

    def __repr__(self) -> str:
        return f"Vector4({self.x}, {self.y}, {self.z}, {self.w})"

    def set(self, x: float, y: float, z: float, w: float) -> "Vector4":
        self.x = x
        self.y = y
        self.z = z
        self.w = w
        return self

    def setScalar( self, scalar ) -> "Vector4":
        self.x = scalar
        self.y = scalar
        self.z = scalar
        self.w = scalar
        return self

    def setX( self, x ) -> "Vector4":
        self.x = x
        return self

    def setY( self, y ) -> "Vector4":
        self.y = y
        return self

    def setZ( self, z ) -> "Vector4":
        self.z = z
        return self

    def setW( self, w ) -> "Vector4":
        self.w = w
        return self


    def setComponent( self, index, value ) -> "Vector4":
        if index == 0:
            self.x = value
        elif index == 1:
            self.y = value
        elif index == 2:
            self.z = value
        elif index == 3:
            self.w = value
        else:
            raise RuntimeError(f'index:{index} out of range')

        return self

    def getComponent( self, index ):
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        elif index == 2:
            return self.z
        elif index == 3:
            return self.w
        else:
            raise RuntimeError(f'index:{index} out of range')

    def copy( self, v:'Vector4' ) -> "Vector4":
        self.x = v.x
        self.y = v.y
        self.z = v.z
        self.w = v.w if v.w is not None else 1
        return self
    
    def add( self, v:'Vector4' ) -> "Vector4":
        self.x += v.x
        self.y += v.y
        self.z += v.z
        self.w += v.w
        return self

    def addScalar( self, s ) -> "Vector4":
        self.x += s
        self.y += s
        self.z += s
        self.w += s
        return self

    def addVectors( self, a:'Vector4', b:'Vector4' ) -> "Vector4":
        self.x = a.x + b.x
        self.y = a.y + b.y
        self.z = a.z + b.z
        self.w = a.w + b.w
        return self

    def addScaledVector( self, v:'Vector4', s ) -> "Vector4":
        self.x += v.x * s
        self.y += v.y * s
        self.z += v.z * s
        self.w += v.w * s
        return self

    def sub( self, v:'Vector4' ) -> "Vector4":
        self.x -= v.x
        self.y -= v.y
        self.z -= v.z
        self.w -= v.w
        return self

    def subScalar( self, s ) -> "Vector4":
        self.x -= s
        self.y -= s
        self.z -= s
        self.w -= s
        return self

    def subVectors( self, a:'Vector4', b:'Vector4' ) -> "Vector4":
        self.x = a.x - b.x
        self.y = a.y - b.y
        self.z = a.z - b.z
        self.w = a.w - b.w
        return self

    def multiply( self, v:'Vector4' ) -> "Vector4":
        self.x *= v.x
        self.y *= v.y
        self.z *= v.z
        self.w *= v.w
        return self

    def multiplyScalar( self, scalar ) -> "Vector4":
        self.x *= scalar
        self.y *= scalar
        self.z *= scalar
        self.w *= scalar
        return self


    def applyMatrix4(self, m: "three.Matrix4") -> "Vector4":
        x = self.x
        y = self.y
        z = self.z
        w = self.w
        e = m.elements

        self.x = e[0] * x + e[4] * y + e[8] * z + e[12] * w
        self.y = e[1] * x + e[5] * y + e[9] * z + e[13] * w
        self.z = e[2] * x + e[6] * y + e[10] * z + e[14] * w
        self.w = e[3] * x + e[7] * y + e[11] * z + e[15] * w

        return self

    
    def divideScalar( self, scalar ) -> "Vector4":
        return self.multiplyScalar( 1 / scalar )

    def setAxisAngleFromQuaternion( self, q:'three.Quaternion' ) -> "Vector4":
        # http://www.euclideanspace.com/maths/geometry/rotations/conversions/quaternionToAngle/index.htm
        # q is assumed to be normalized
        self.w = 2 * math.acos( q.w )
        s = math.sqrt( 1 - q.w * q.w )

        if s < 0.0001:
            self.x = 1
            self.y = 0
            self.z = 0
        else:
            self.x = q.x / s
            self.y = q.y / s
            self.z = q.z / s

        return self


    def setAxisAngleFromRotationMatrix( self, m:'three.Matrix4' ) -> "Vector4":
        # http://www.euclideanspace.com/maths/geometry/rotations/conversions/matrixToAngle/index.htm
        # assumes the upper 3x3 of m is a pure rotation matrix (i.e, unscaled)
        # angle, x, y, z  # variables for result
        epsilon = 0.01    # margin to allow for rounding errors
        epsilon2 = 0.1    # margin to distinguish between 0 and 180 degrees

        te = m.elements,

        m11 = te[ 0 ]; m12 = te[ 4 ]; m13 = te[ 8 ]
        m21 = te[ 1 ]; m22 = te[ 5 ]; m23 = te[ 9 ]
        m31 = te[ 2 ]; m32 = te[ 6 ]; m33 = te[ 10 ]

        if (abs( m12 - m21 ) < epsilon ) and (abs( m13 - m31 ) < epsilon ) and (abs( m23 - m32 ) < epsilon  ):
            # singularity found
            # first check for identity matrix which must have +1 for all terms
            # in leading diagonal and zero in other terms

            if (abs( m12 + m21 ) < epsilon2) and (abs( m13 + m31 ) < epsilon2) and (abs( m23 + m32 ) < epsilon2) and (abs( m11 + m22 + m33 - 3 ) < epsilon2):

                # self singularity is identity matrix so angle = 0
                self.set( 1, 0, 0, 0 )
                
                return self 
                # zero angle, arbitrary axis

            # cotherwise self singularity is angle = 180

            angle = math.pi

            xx = ( m11 + 1 ) / 2
            yy = ( m22 + 1 ) / 2
            zz = ( m33 + 1 ) / 2
            xy = ( m12 + m21 ) / 4
            xz = ( m13 + m31 ) / 4
            yz = ( m23 + m32 ) / 4

            if ( xx > yy ) and ( xx > zz ):
                # m11 is the largest diagonal term
                if xx < epsilon:
                    x = 0
                    y = 0.707106781
                    z = 0.707106781
                else:
                    x = math.sqrt( xx )
                    y = xy / x
                    z = xz / x

            elif yy > zz:

                # m22 is the largest diagonal term
                if yy < epsilon:
                    x = 0.707106781
                    y = 0
                    z = 0.707106781
                else:
                    y = math.sqrt( yy )
                    x = xy / y
                    z = yz / y
            else:
                # m33 is the largest diagonal term so base result on self
                if zz < epsilon:
                    x = 0.707106781
                    y = 0.707106781
                    z = 0
                else:
                    z = math.sqrt( zz )
                    x = xz / z
                    y = yz / z

            self.set( x, y, z, angle )
            return self
             # return 180 deg rotation

        # as we have reached here there are no singularities so we can handle normally

        s = math.sqrt( ( m32 - m23 ) * ( m32 - m23 ) +( m13 - m31 ) * ( m13 - m31 ) + ( m21 - m12 ) * ( m21 - m12 ) )  # used to normalize

        if abs( s ) < 0.001:
            s = 1

        # prevent divide by zero, should not happen if matrix is orthogonal and should be
        # caught by singularity test above, but I've left it in just in case
        self.x = ( m32 - m23 ) / s
        self.y = ( m13 - m31 ) / s
        self.z = ( m21 - m12 ) / s
        self.w = math.acos( ( m11 + m22 + m33 - 1 ) / 2 )

        return self

    def min( self, v:'Vector4' ) -> "Vector4":
        self.x = min( self.x, v.x )
        self.y = min( self.y, v.y )
        self.z = min( self.z, v.z )
        self.w = min( self.w, v.w )

        return self


    def max( self, v:'Vector4' ) -> "Vector4":
        self.x = max( self.x, v.x )
        self.y = max( self.y, v.y )
        self.z = max( self.z, v.z )
        self.w = max( self.w, v.w )

        return self

    def clamp( self, _min:'Vector4', _max:'Vector4' ) -> "Vector4":
        # assumes min < max, componentwise
        self.x = max( _min.x, min( _max.x, self.x ) )
        self.y = max( _min.y, min( _max.y, self.y ) )
        self.z = max( _min.z, min( _max.z, self.z ) )
        self.w = max( _min.w, min( _max.w, self.w ) )

        return self

    def clampScalar( self, minVal, maxVal ) -> "Vector4":
        self.x = max( minVal, min( maxVal, self.x ) )
        self.y = max( minVal, min( maxVal, self.y ) )
        self.z = max( minVal, min( maxVal, self.z ) )
        self.w = max( minVal, min( maxVal, self.w ) )

        return self

    def clampLength( self, _min, _max ) -> "Vector4":
        length = self.length()
        return self.divideScalar( length or 1 ).multiplyScalar( max( _min, min( _max, length ) ) )

    def clone( self ) -> "Vector4":
        return Vector4(self.x, self.y, self.z, self.w)

    def floor( self ) -> "Vector4":
        self.x = math.floor( self.x )
        self.y = math.floor( self.y )
        self.z = math.floor( self.z )
        self.w = math.floor( self.w )

        return self

    def ceil( self ) -> "Vector4":
        self.x = math.ceil( self.x )
        self.y = math.ceil( self.y )
        self.z = math.ceil( self.z )
        self.w = math.ceil( self.w )
        return self

    def round( self ) -> "Vector4":
        self.x = round( self.x )
        self.y = round( self.y )
        self.z = round( self.z )
        self.w = round( self.w )
        return self

    def roundToZero( self ) -> "Vector4":
        self.x = math.ceil( self.x ) if self.x < 0 else math.floor( self.x )
        self.y = math.ceil( self.y ) if self.y < 0 else math.floor( self.y )
        self.z = math.ceil( self.z ) if self.z < 0 else math.floor( self.z )
        self.w = math.ceil( self.w ) if self.w < 0 else math.floor( self.w )
        return self

    def negate( self ) -> "Vector4":
        self.x = - self.x
        self.y = - self.y
        self.z = - self.z
        self.w = - self.w
        return self


    def dot( self, v ):
        return self.x * v.x + self.y * v.y + self.z * v.z + self.w * v.w

    def lengthSq( self ):
        return self.x * self.x + self.y * self.y + self.z * self.z + self.w * self.w

    def length( self ):
        return math.sqrt( self.x * self.x + self.y * self.y + self.z * self.z + self.w * self.w )
    
    def manhattanLength( self ):
        return abs( self.x ) + abs( self.y ) + abs( self.z ) + abs( self.w )

    def normalize( self ):
        return self.divideScalar( self.length() or 1 )

    def setLength( self, length ):
        return self.normalize().multiplyScalar( length )

    def lerp( self, v, alpha ) -> "Vector4":
        self.x += ( v.x - self.x ) * alpha
        self.y += ( v.y - self.y ) * alpha
        self.z += ( v.z - self.z ) * alpha
        self.w += ( v.w - self.w ) * alpha

        return self

    def lerpVectors( self, v1, v2, alpha ) -> "Vector4":
        self.x = v1.x + ( v2.x - v1.x ) * alpha
        self.y = v1.y + ( v2.y - v1.y ) * alpha
        self.z = v1.z + ( v2.z - v1.z ) * alpha
        self.w = v1.w + ( v2.w - v1.w ) * alpha

        return self

    def __eq__( self, v: object ) -> bool:
        return ( ( v.x == self.x ) and ( v.y == self.y ) and ( v.z == self.z ) and ( v.w == self.w ) )

    equals = __eq__


    def fromArray( self, arr: Float32Array, offset = 0 ) -> "Vector4":
        # m = memoryview(self._buffer)
        # m[:] = arr.buffer[offset:offset+4]
        self.x = arr[ offset ]
        self.y = arr[ offset + 1 ]
        self.z = arr[ offset + 2 ]
        self.w = arr[ offset + 3 ]

        return self

    def toArray( self, arr: Float32Array = None, offset = 0 ) -> "Vector4":
        if arr is None:
            arr = Float32Array(4)
        padding = offset + 4 - len(arr)
        if padding > 0:
            arr.extend((None for _ in range(padding)))

        arr[offset: offset + 4] = self._buffer

        # array[ offset ] = self.x
        # array[ offset + 1 ] = self.y
        # array[ offset + 2 ] = self.z
        # array[ offset + 3 ] = self.w

        return arr

    def fromBufferAttribute( self, attribute:'three.BufferAttribute', index ) -> "Vector4":

        self.x = attribute.getX( index )
        self.y = attribute.getY( index )
        self.z = attribute.getZ( index )
        self.w = attribute.getW( index )

        return self

    def random( self ) -> "Vector4":
        self.x = random.random()
        self.y = random.random()
        self.z = random.random()
        self.w = random.random()

        return self