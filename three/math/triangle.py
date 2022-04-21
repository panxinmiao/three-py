from .vector3 import Vector3
from ..structure import NoneAttribute
import math
import three


_v0 = Vector3()
_v1 = Vector3()
_v2 = Vector3()
_v3 = Vector3()

_vab = Vector3()
_vac = Vector3()
_vbc = Vector3()
_vap = Vector3()
_vbp = Vector3()
_vcp = Vector3()

class Triangle(NoneAttribute):

    def __init__(self, a=None, b=None, c=None) -> None:
        self.a = a or Vector3()
        self.b = b or Vector3()
        self.c = c or Vector3()

    @staticmethod
    def _getNormal( a, b, c, target:'Vector3' ):

        target.subVectors( c, b )
        _v0.subVectors( a, b )
        target.cross( _v0 )

        targetLengthSq = target.lengthSq()
        if targetLengthSq > 0:

            return target.multiplyScalar( 1 / math.sqrt( targetLengthSq ) )


        return target.set( 0, 0, 0 )

    # static/instance method to calculate barycentric coordinates
    # based on: http://www.blackpawn.com/texts/pointinpoly/default.html
    @staticmethod
    def _getBarycoord( point, a, b, c, target ):

        _v0.subVectors( c, a )
        _v1.subVectors( b, a )
        _v2.subVectors( point, a )

        dot00 = _v0.dot( _v0 )
        dot01 = _v0.dot( _v1 )
        dot02 = _v0.dot( _v2 )
        dot11 = _v1.dot( _v1 )
        dot12 = _v1.dot( _v2 )

        denom = ( dot00 * dot11 - dot01 * dot01 )

		# collinear or singular triangle
        if denom == 0:
            # arbitrary location outside of triangle?
            # not sure if self is the best idea, maybe should be returning undefined
            return target.set( - 2, - 1, - 1 )


        invDenom = 1 / denom
        u = ( dot11 * dot02 - dot01 * dot12 ) * invDenom
        v = ( dot00 * dot12 - dot01 * dot02 ) * invDenom

        # barycentric coordinates must always sum to 1
        return target.set( 1 - u - v, v, u )

    @staticmethod
    def _containsPoint( point, a, b, c ):
        Triangle.getBarycoord( point, a, b, c, _v3 )
        return ( _v3.x >= 0 ) and ( _v3.y >= 0 ) and ( ( _v3.x + _v3.y ) <= 1 )

    @staticmethod
    def _getUV( point, p1, p2, p3, uv1, uv2, uv3, target:'Vector3' ):

        Triangle.getBarycoord( point, p1, p2, p3, _v3 )

        target.set( 0, 0 )
        target.addScaledVector( uv1, _v3.x )
        target.addScaledVector( uv2, _v3.y )
        target.addScaledVector( uv3, _v3.z )

        return target

    @staticmethod
    def _isFrontFacing( a, b, c, direction ):
        _v0.subVectors( c, b )
        _v1.subVectors( a, b )

        # strictly front facing
        return _v0.cross( _v1 ).dot( direction ) < 0 

    def set( self, a, b, c ):
        self.a.copy( a )
        self.b.copy( b )
        self.c.copy( c )

        return self


    def setFromPointsAndIndices( self, points, i0, i1, i2 ):
        self.a.copy( points[ i0 ] )
        self.b.copy( points[ i1 ] )
        self.c.copy( points[ i2 ] )

        return self


    def setFromAttributeAndIndices( self, attribute, i0, i1, i2 ):
        self.a.fromBufferAttribute( attribute, i0 )
        self.b.fromBufferAttribute( attribute, i1 )
        self.c.fromBufferAttribute( attribute, i2 )

        return self

    def clone(self):
        return Triangle().copy( self )

    def copy( self, triangle ):
        self.a.copy( triangle.a )
        self.b.copy( triangle.b )
        self.c.copy( triangle.c )

        return self

    def getArea(self):
        _v0.subVectors( self.c, self.b )
        _v1.subVectors( self.a, self.b )

        return _v0.cross( _v1 ).length() * 0.5

    def getMidpoint( self, target:'Vector3' ):
        return target.addVectors( self.a, self.b ).add( self.c ).multiplyScalar( 1 / 3 )

    def getNormal( self, target ):
        return Triangle._getNormal( self.a, self.b, self.c, target )

    def getPlane(self, target:'three.Plane' ):
        return target.setFromCoplanarPoints( self.a, self.b, self.c )
        
    def getBarycoord( self, point, target ):
        return Triangle._getBarycoord( point, self.a, self.b, self.c, target )

    def getUV( self, point, uv1, uv2, uv3, target ):
        return Triangle._getUV( point, self.a, self.b, self.c, uv1, uv2, uv3, target )

    def containsPoint( self, point ):
        return Triangle._containsPoint( point, self.a, self.b, self.c )

    def isFrontFacing( self, direction ):
        return Triangle._isFrontFacing( self.a, self.b, self.c, direction )

    def intersectsBox( self, box:'three.Box3' ):
        return box.intersectsTriangle( self )





