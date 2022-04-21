from ..structure import NoneAttribute
from .vector3 import Vector3

class SphericalHarmonics3(NoneAttribute):
   
    def __init__(self) -> None:
        self.coefficients:'list[Vector3]' = []
        for i in range(9):
            self.coefficients.append( Vector3() )

    def set( self, coefficients ):
        for i in range(9):
            self.coefficients[ i ].copy( coefficients[ i ] )
        return self

    def zero(self):
        for i in range(9):
            self.coefficients[ i ].set( 0, 0, 0 )

        return self

    def getAt( self, normal, target:'Vector3' ):

        # normal is assumed to be unit length

        x = normal.x
        y = normal.y
        z = normal.z

        coeff = self.coefficients

        # band 0
        target.copy( coeff[ 0 ] ).multiplyScalar( 0.282095 )

        # band 1
        target.addScaledVector( coeff[ 1 ], 0.488603 * y )
        target.addScaledVector( coeff[ 2 ], 0.488603 * z )
        target.addScaledVector( coeff[ 3 ], 0.488603 * x )

        # band 2
        target.addScaledVector( coeff[ 4 ], 1.092548 * ( x * y ) )
        target.addScaledVector( coeff[ 5 ], 1.092548 * ( y * z ) )
        target.addScaledVector( coeff[ 6 ], 0.315392 * ( 3.0 * z * z - 1.0 ) )
        target.addScaledVector( coeff[ 7 ], 1.092548 * ( x * z ) )
        target.addScaledVector( coeff[ 8 ], 0.546274 * ( x * x - y * y ) )

        return target

    def getIrradianceAt( self, normal, target:'Vector3' ):

		# normal is assumed to be unit length

        x = normal.x
        y = normal.y
        z = normal.z

        coeff = self.coefficients

        # band 0
        target.copy( coeff[ 0 ] ).multiplyScalar( 0.886227 ) # π * 0.282095

        # band 1
        target.addScaledVector( coeff[ 1 ], 2.0 * 0.511664 * y ) # ( 2 * π / 3 ) * 0.488603
        target.addScaledVector( coeff[ 2 ], 2.0 * 0.511664 * z )
        target.addScaledVector( coeff[ 3 ], 2.0 * 0.511664 * x )

        # band 2
        target.addScaledVector( coeff[ 4 ], 2.0 * 0.429043 * x * y ) # ( π / 4 ) * 1.092548
        target.addScaledVector( coeff[ 5 ], 2.0 * 0.429043 * y * z )
        target.addScaledVector( coeff[ 6 ], 0.743125 * z * z - 0.247708 ) # ( π / 4 ) * 0.315392 * 3
        target.addScaledVector( coeff[ 7 ], 2.0 * 0.429043 * x * z )
        target.addScaledVector( coeff[ 8 ], 0.429043 * ( x * x - y * y ) ) # ( π / 4 ) * 0.546274

        return target

    def add( self, sh:'SphericalHarmonics3' ):
        for i in range(9):
            self.coefficients[ i ].add( sh.coefficients[ i ] )

        return self

    def addScaledSH( self, sh:'SphericalHarmonics3', s ):
        for i in range(9):
            self.coefficients[ i ].addScaledVector( sh.coefficients[ i ], s )
        return self
    
    def scale( self, s ):
        for i in range(9):
            self.coefficients[ i ].multiplyScalar( s )
        return self

    def lerp( self, sh:'SphericalHarmonics3', alpha ):
        for i in range(9):
            self.coefficients[ i ].lerp( sh.coefficients[ i ], alpha )
        return self

    def equals( self, sh:'SphericalHarmonics3' ):

        for i in range(9):
            if ( not self.coefficients[ i ].equals( sh.coefficients[ i ] ) ):
                return False

        return True

    def copy( self, sh ):
        return self.set( sh.coefficients )


    def clone(self):
        SphericalHarmonics3().copy(self)

    def fromArray( self, array, offset = 0 ):

        coefficients = self.coefficients
        for i in range(9):
            coefficients[ i ].fromArray( array, offset + ( i * 3 ) )

        return self

    def toArray( self, array = [], offset = 0 ):

        coefficients = self.coefficients
        for i in range(9):
            coefficients[ i ].toArray( array, offset + ( i * 3 ) )

        return array

    # evaluate the basis functions
    # shBasis is an Array[ 9 ]

    @staticmethod
    def getBasisAt( normal, shBasis ):

		# normal is assumed to be unit length

        x = normal.x
        y = normal.y
        z = normal.z

        # band 0
        shBasis[ 0 ] = 0.282095

        # band 1
        shBasis[ 1 ] = 0.488603 * y
        shBasis[ 2 ] = 0.488603 * z
        shBasis[ 3 ] = 0.488603 * x

        # band 2
        shBasis[ 4 ] = 1.092548 * x * y
        shBasis[ 5 ] = 1.092548 * y * z
        shBasis[ 6 ] = 0.315392 * ( 3 * z * z - 1 )
        shBasis[ 7 ] = 1.092548 * x * z
        shBasis[ 8 ] = 0.546274 * ( x * x - y * y )
