
import math
from ..structure import NoneAttribute
from .vector3 import Vector3
from .box3 import Box3
import three


_box = Box3()
_v1 = Vector3()
_toFarthestPoint = Vector3()
_toPoint = Vector3()

class Sphere(NoneAttribute):

    def __init__(self, center:'Vector3' = None, radius = - 1) -> None:
        if center is None:
            center = Vector3()
        self.center = center
        self.radius = radius

    def __repr__(self) -> str:
        return f"Sphere({self.center}, {self.radius})"

    def set( self, center, radius ) -> 'Sphere':
        self.center.copy( center )
        self.radius = radius
        return self


    def setFromPoints( self, points, optionalCenter = None ) -> 'Sphere':
        center = self.center
        if optionalCenter:
            center.copy( optionalCenter )
        else:
            _box.setFromPoints( points ).getCenter( center )

        maxRadiusSq = 0

        for p in points:
            maxRadiusSq = max( maxRadiusSq, center.distanceToSquared( p ) )
        
        self.radius = math.sqrt( maxRadiusSq )

        return self

    def copy( self, sphere:'Sphere' ) -> 'Sphere':
        self.center.copy( sphere.center )
        self.radius = sphere.radius
        return self

    def isEmpty(self) -> 'bool':
        return ( self.radius < 0 )

    def makeEmpty(self) -> 'Sphere':

        self.center.set( 0, 0, 0 )
        self.radius = - 1

        return self

    def containsPoint( self, point:'Vector3' ) -> 'bool':
        return ( point.distanceToSquared( self.center ) <= ( self.radius * self.radius ) )


    def distanceToPoint( self, point:'Vector3' ) -> 'float':
        return ( point.distanceTo( self.center ) - self.radius )

    def intersectsSphere( self, sphere:'Sphere' ) -> 'bool':
        radiusSum = self.radius + sphere.radius
        return sphere.center.distanceToSquared( self.center ) <= ( radiusSum * radiusSum )

    def intersectsBox( self,  box:'Box3' ) -> bool:
        return box.intersectsSphere( self )

    def intersectsPlane( self, plane:'three.Plane') -> bool:
        return abs( plane.distanceToPoint( self.center ) ) <= self.radius

    def clampPoint( self, point, target:'Vector3' ):
        deltaLengthSq = self.center.distanceToSquared( point )
        target.copy( point )

        if deltaLengthSq > ( self.radius * self.radius ):
            target.sub( self.center ).normalize()
            target.multiplyScalar( self.radius ).add( self.center )
        
        return target

    def getBoundingBox( self, target:'Box3' ):
        if self.isEmpty():

            # Empty sphere produces empty bounding box
            target.makeEmpty()
            return target
        
        target.set( self.center, self.center )
        target.expandByScalar( self.radius )

        return target

    def applyMatrix4( self, matrix:'three.Matrix4' ) -> 'Sphere':
        self.center.applyMatrix4( matrix )
        self.radius = self.radius * matrix.getMaxScaleOnAxis()

        return self

    def translate( self, offset ) -> 'Sphere':
        self.center.add( offset )
        return self

    def expandByPoint( self, point ) -> 'Sphere':
        
        # from https://github.com/juj/MathGeoLib/blob/2940b99b99cfe575dd45103ef20f4019dee15b54/src/Geometry/Sphere.cpp#L649-L671

        _toPoint.subVectors( point, self.center )

        lengthSq = _toPoint.lengthSq()

        if lengthSq > ( self.radius * self.radius ):

            length = math.sqrt( lengthSq )
            missingRadiusHalf = ( length - self.radius ) * 0.5

            # Nudge this sphere towards the target point. Add half the missing distance to radius,
            # and the other half to position. This gives a tighter enclosure, instead of if
            # the whole missing distance were just added to radius.

            self.center.add( _toPoint.multiplyScalar( missingRadiusHalf / length ) )
            self.radius += missingRadiusHalf

        return self


    def union( self, sphere:'Sphere' ) -> 'Sphere':

        # from https://github.com/juj/MathGeoLib/blob/2940b99b99cfe575dd45103ef20f4019dee15b54/src/Geometry/Sphere.cpp#L759-L769

        # To enclose another sphere into this sphere, we only need to enclose two points:
        # 1) Enclose the farthest point on the other sphere into this sphere.
        # 2) Enclose the opposite point of the farthest point into this sphere.

        if self.center.equals( sphere.center ) == True:
            _toFarthestPoint.set( 0, 0, 1 ).multiplyScalar( sphere.radius )

        else:
            _toFarthestPoint.subVectors( sphere.center, self.center ).normalize().multiplyScalar( sphere.radius )

        self.expandByPoint( _v1.copy( sphere.center ).add( _toFarthestPoint ) )
        self.expandByPoint( _v1.copy( sphere.center ).sub( _toFarthestPoint ) )

        return self

    def __eq__(self, sphere: object) -> bool:
        return sphere.center.equals( self.center ) and ( sphere.radius == self.radius )

    equals = __eq__

    def clone( self ) -> 'Sphere':
        return Sphere().copy( self )
