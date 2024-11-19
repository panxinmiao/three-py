import three, math
from array import array
from ..structure import NoneAttribute, Float32Array

class Matrix3(NoneAttribute):

    __slots__ = ['elements']

    isMatrix3 = True

    def __init__(self) -> None:
        self.elements = array('f', [
            1, 0, 0,
            0, 1, 0,
            0, 0, 1,
        ])

    def __repr__(self) -> str:
        return f"Matrix3({self.elements[0]}, {self.elements[1]}, {self.elements[2]}, {self.elements[3]}, {self.elements[4]}, {self.elements[5]}, {self.elements[6]}, {self.elements[7]}, {self.elements[8]})"

    def set(
        self,
        n11: float,
        n12: float,
        n13: float,
        n21: float,
        n22: float,
        n23: float,
        n31: float,
        n32: float,
        n33: float,
    ) -> "three.Matrix4":
        te = self.elements

        te[0] = n11
        te[3] = n12
        te[6] = n13
        te[1] = n21
        te[4] = n22
        te[7] = n23
        te[2] = n31
        te[5] = n32
        te[8] = n33

        return self

    def identity(self)-> 'Matrix3':
        self.set(

            1, 0, 0,
            0, 1, 0,
            0, 0, 1

        )

        return self

    def copy( self, m:'Matrix3' ) -> 'Matrix3':
        te = self.elements
        me = m.elements

        te[ 0 ] = me[ 0 ]; te[ 1 ] = me[ 1 ]; te[ 2 ] = me[ 2 ]
        te[ 3 ] = me[ 3 ]; te[ 4 ] = me[ 4 ]; te[ 5 ] = me[ 5 ]
        te[ 6 ] = me[ 6 ]; te[ 7 ] = me[ 7 ]; te[ 8 ] = me[ 8 ]

        return self

    def extractBasis(self, xAxis:'three.Vector3', yAxis:'three.Vector3', zAxis:'three.Vector3' ) -> 'Matrix3':
        
        xAxis.setFromMatrix3Column( self, 0 )
        yAxis.setFromMatrix3Column( self, 1 )
        zAxis.setFromMatrix3Column( self, 2 )

        return self

    def setFromMatrix4(self,  m: 'three.Matrix4')-> 'Matrix3':

        me = m.elements

        self.set(

            me[ 0 ], me[ 4 ], me[ 8 ],
            me[ 1 ], me[ 5 ], me[ 9 ],
            me[ 2 ], me[ 6 ], me[ 10 ]

        )
        return self

    def multiply( self, m:'Matrix3' ) -> 'Matrix3':
        return self.multiplyMatrices( self, m )


    def premultiply( self, m:'Matrix3' ) -> 'Matrix3':
        return self.multiplyMatrices( m, self )


    def multiplyMatrices( self, a:'Matrix3', b:'Matrix3' ) -> 'Matrix3':

        ae = a.elements
        be = b.elements
        te = self.elements

        a11 = ae[ 0 ]; a12 = ae[ 3 ]; a13 = ae[ 6 ]
        a21 = ae[ 1 ]; a22 = ae[ 4 ]; a23 = ae[ 7 ]
        a31 = ae[ 2 ]; a32 = ae[ 5 ]; a33 = ae[ 8 ]

        b11 = be[ 0 ]; b12 = be[ 3 ]; b13 = be[ 6 ]
        b21 = be[ 1 ]; b22 = be[ 4 ]; b23 = be[ 7 ]
        b31 = be[ 2 ]; b32 = be[ 5 ]; b33 = be[ 8 ]

        te[ 0 ] = a11 * b11 + a12 * b21 + a13 * b31
        te[ 3 ] = a11 * b12 + a12 * b22 + a13 * b32
        te[ 6 ] = a11 * b13 + a12 * b23 + a13 * b33

        te[ 1 ] = a21 * b11 + a22 * b21 + a23 * b31
        te[ 4 ] = a21 * b12 + a22 * b22 + a23 * b32
        te[ 7 ] = a21 * b13 + a22 * b23 + a23 * b33

        te[ 2 ] = a31 * b11 + a32 * b21 + a33 * b31
        te[ 5 ] = a31 * b12 + a32 * b22 + a33 * b32
        te[ 8 ] = a31 * b13 + a32 * b23 + a33 * b33

        return self


    def multiplyScalar( self, s ) -> 'Matrix3':

        te = self.elements

        te[ 0 ] *= s; te[ 3 ] *= s; te[ 6 ] *= s
        te[ 1 ] *= s; te[ 4 ] *= s; te[ 7 ] *= s
        te[ 2 ] *= s; te[ 5 ] *= s; te[ 8 ] *= s

        return self


    def determinant( self ):

        te = self.elements

        a = te[ 0 ]; b = te[ 1 ]; c = te[ 2 ]
        d = te[ 3 ]; e = te[ 4 ]; f = te[ 5 ]
        g = te[ 6 ]; h = te[ 7 ]; i = te[ 8 ]

        return a * e * i - a * f * h - b * d * i + b * f * g + c * d * h - c * e * g

    def invert(self) -> "Matrix3":
        te = self.elements

        n11 = te[ 0 ]; n21 = te[ 1 ]; n31 = te[ 2 ]
        n12 = te[ 3 ]; n22 = te[ 4 ]; n32 = te[ 5 ]
        n13 = te[ 6 ]; n23 = te[ 7 ]; n33 = te[ 8 ]

        t11 = n33 * n22 - n32 * n23
        t12 = n32 * n13 - n33 * n12
        t13 = n23 * n12 - n22 * n13

        det = n11 * t11 + n21 * t12 + n31 * t13

        if det == 0:
            return self.set( 0, 0, 0, 0, 0, 0, 0, 0, 0 )

        detInv = 1 / det

        te[ 0 ] = t11 * detInv
        te[ 1 ] = ( n31 * n23 - n33 * n21 ) * detInv
        te[ 2 ] = ( n32 * n21 - n31 * n22 ) * detInv

        te[ 3 ] = t12 * detInv
        te[ 4 ] = ( n33 * n11 - n31 * n13 ) * detInv
        te[ 5 ] = ( n31 * n12 - n32 * n11 ) * detInv

        te[ 6 ] = t13 * detInv
        te[ 7 ] = ( n21 * n13 - n23 * n11 ) * detInv
        te[ 8 ] = ( n22 * n11 - n21 * n12 ) * detInv

        return self

    def transpose(self) -> "Matrix3":
        m = self.elements

        tmp = m[ 1 ]; m[ 1 ] = m[ 3 ]; m[ 3 ] = tmp
        tmp = m[ 2 ]; m[ 2 ] = m[ 6 ]; m[ 6 ] = tmp
        tmp = m[ 5 ]; m[ 5 ] = m[ 7 ]; m[ 7 ] = tmp

        return self

    def getNormalMatrix( self, matrix4:'three.Matrix4' )-> "Matrix3":

        return self.setFromMatrix4( matrix4 ).invert().transpose()

    def transposeIntoArray( self, r ):

        m = self.elements

        r[ 0 ] = m[ 0 ]
        r[ 1 ] = m[ 3 ]
        r[ 2 ] = m[ 6 ]
        r[ 3 ] = m[ 1 ]
        r[ 4 ] = m[ 4 ]
        r[ 5 ] = m[ 7 ]
        r[ 6 ] = m[ 2 ]
        r[ 7 ] = m[ 5 ]
        r[ 8 ] = m[ 8 ]

        return self


    def setUvTransform(self, tx, ty, sx, sy, rotation, cx, cy ) -> 'Matrix3':

        c = math.cos( rotation )
        s = math.sin( rotation )

        self.set(
            sx * c, sx * s, - sx * ( c * cx + s * cy ) + cx + tx,
            - sy * s, sy * c, - sy * ( - s * cx + c * cy ) + cy + ty,
            0, 0, 1
        )

        return self

    def scale( self, sx, sy ) -> 'Matrix3':
        te = self.elements
        te[ 0 ] *= sx; te[ 3 ] *= sx; te[ 6 ] *= sx
        te[ 1 ] *= sy; te[ 4 ] *= sy; te[ 7 ] *= sy
        return self


    def rotate( self, theta ) -> 'Matrix3':

        c = math.cos( theta )
        s = math.sin( theta )

        te = self.elements

        a11 = te[ 0 ]; a12 = te[ 3 ]; a13 = te[ 6 ]
        a21 = te[ 1 ]; a22 = te[ 4 ]; a23 = te[ 7 ]

        te[ 0 ] = c * a11 + s * a21
        te[ 3 ] = c * a12 + s * a22
        te[ 6 ] = c * a13 + s * a23

        te[ 1 ] = - s * a11 + c * a21
        te[ 4 ] = - s * a12 + c * a22
        te[ 7 ] = - s * a13 + c * a23

        return self

    def translate( self, tx, ty ) -> 'Matrix3':
        te = self.elements

        te[ 0 ] += tx * te[ 2 ]; te[ 3 ] += tx * te[ 5 ]; te[ 6 ] += tx * te[ 8 ]
        te[ 1 ] += ty * te[ 2 ]; te[ 4 ] += ty * te[ 5 ]; te[ 7 ] += ty * te[ 8 ]

        return self

    def equals( self, matrix:'Matrix3' ) -> 'bool':
        te = self.elements
        me = matrix.elements

        for i in range(9):
            if te[ i ] != me[ i ]:
                return False
        return True

    def __eq__(self, __o: object) -> bool:
        return isinstance(__o, Matrix3) and self.equals(__o)


    def fromArray(self, arr: Float32Array, offset: int = 0) -> "Matrix3":
        # m = memoryview(self.elements)
        # m[:] = arr.buffer[offset:offset+9]
        for i in range(9):
            self.elements[i] = arr[i + offset]
        return self

    def toArray( self, arr: Float32Array = None, offset = 0 ) -> 'Float32Array':

        if arr is None:
            arr = Float32Array(9)
        padding = offset + 9 - len(arr)
        if padding > 0:
            arr.extend((None for _ in range(padding)))

        arr[offset: offset + 9] = self.elements

        # te = self.elements

        # array[ offset ] = te[ 0 ]
        # array[ offset + 1 ] = te[ 1 ]
        # array[ offset + 2 ] = te[ 2 ]

        # array[ offset + 3 ] = te[ 3 ]
        # array[ offset + 4 ] = te[ 4 ]
        # array[ offset + 5 ] = te[ 5 ]

        # array[ offset + 6 ] = te[ 6 ]
        # array[ offset + 7 ] = te[ 7 ]
        # array[ offset + 8 ] = te[ 8 ]

        return arr


    def clone( self ) -> "Matrix3":
        return Matrix3().fromArray(self.elements)
