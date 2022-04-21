import three
from ..structure import NoneAttribute
from .vector3 import Vector3
from .matrix3 import Matrix3

_vector1 = Vector3()
_vector2 = Vector3()
_normalMatrix = Matrix3()

class Plane(NoneAttribute):

    def __init__(self, normal = None, constant = 0 ) -> None:
        if normal is None:
            normal = Vector3( 1, 0, 0 )
        self.normal = normal
        self.constant = constant

    def set( self, normal:Vector3, constant ) -> 'Plane':
        self.normal.copy( normal )
        self.constant = constant
        return self

    def setComponents( self, x, y, z, w ) -> 'Plane':
        self.normal.set( x, y, z )
        self.constant = w
        return self


    def setFromNormalAndCoplanarPoint( self, normal:Vector3, point:Vector3 ) -> 'Plane':
        self.normal.copy( normal )
        self.constant = - point.dot( self.normal )
        return self


    def setFromCoplanarPoints( self, a, b, c ) -> 'Plane':
        normal = _vector1.subVectors( c, b ).cross( _vector2.subVectors( a, b ) ).normalize()

        # Q: should an error be thrown if normal is zero (e.g. degenerate plane)?

        self.setFromNormalAndCoplanarPoint( normal, a )

        return self


    def copy( self, plane:'Plane' ) -> 'Plane':
        self.normal.copy( plane.normal )
        self.constant = plane.constant
        return self


    def normalize(self) -> 'Plane':

        # Note: will lead to a divide by zero if the plane is invalid.

        inverseNormalLength = 1.0 / self.normal.length()
        self.normal.multiplyScalar( inverseNormalLength )
        self.constant *= inverseNormalLength
        return self


    def negate(self) -> 'Plane':
        self.constant *= - 1
        self.normal.negate()
        return self

    def distanceToPoint( self, point:Vector3 ) -> 'float':
        return self.normal.dot( point ) + self.constant


    def distanceToSphere( self, sphere:'three.Sphere' ) -> 'Plane':
        return self.distanceToPoint( sphere.center ) - sphere.radius


    def projectPoint( self, point:Vector3, target:Vector3 ) -> 'Vector3':
        return target.copy( self.normal ).multiplyScalar( - self.distanceToPoint( point ) ).add( point )


    def intersectLine( self, line:'three.Line3', target:Vector3 ) -> 'Vector3':
        direction = line.delta( _vector1 )
        denominator = self.normal.dot( direction )

        if denominator == 0:

            # line is coplanar, return origin
            if self.distanceToPoint( line.start ) == 0 :
                return target.copy( line.start )

            # Unsure if this is the correct method to handle this case.
            return None

        t = - ( line.start.dot( self.normal ) + self.constant ) / denominator

        if t < 0 or t > 1:
            return None

        return target.copy( direction ).multiplyScalar( t ).add( line.start )


    def intersectsLine( self, line:'three.Line3' ) -> 'bool':

        # Note: this tests if a line intersects the plane, not whether it (or its end-points) are coplanar with it.

        startSign = self.distanceToPoint( line.start )
        endSign = self.distanceToPoint( line.end )
        
        return (startSign < 0 and endSign > 0)  or ( endSign < 0 and startSign > 0 )


    def intersectsBox( self, box:'three.Box3' ):
        return box.intersectsPlane( self )


    def intersectsSphere( self, sphere:'three.Sphere' ):
        return sphere.intersectsPlane( self )

    def coplanarPoint( self, target:Vector3 ) -> 'Vector3':
        return target.copy( self.normal ).multiplyScalar( - self.constant )


    def applyMatrix4( self, matrix, optionalNormalMatrix ) -> 'Plane':
        normalMatrix = optionalNormalMatrix or _normalMatrix.getNormalMatrix( matrix )
        referencePoint = self.coplanarPoint( _vector1 ).applyMatrix4( matrix )
        normal = self.normal.applyMatrix3( normalMatrix ).normalize()

        self.constant = - referencePoint.dot( normal )

        return self

    def translate( self, offset:'Vector3' ) -> 'Plane':
        self.constant -= offset.dot( self.normal )
        return self

    def equals( self, plane:'Plane' ) -> 'bool':
        return plane.normal.equals( self.normal ) and ( plane.constant == self.constant )


    def clone(self):
        return Plane().copy( self )
