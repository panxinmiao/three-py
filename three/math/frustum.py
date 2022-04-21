import math, three
from ..structure import NoneAttribute
from .plane import Plane
from .sphere import Sphere
from .vector3 import Vector3

_sphere = Sphere()
_vector = Vector3()

class Frustum(NoneAttribute):
    def __init__(self, p0 = None, p1 = None, p2 = None, p3 = None, p4 = None, p5 = None) -> None:
        self.planes = [ p0 or Plane(), p1 or Plane() , p2 or Plane(), p3 or Plane(), p4 or Plane(), p5 or Plane() ]

    def set( self, p0, p1, p2, p3, p4, p5 ):
        planes = self.planes
        planes[ 0 ].copy( p0 )
        planes[ 1 ].copy( p1 )
        planes[ 2 ].copy( p2 )
        planes[ 3 ].copy( p3 )
        planes[ 4 ].copy( p4 )
        planes[ 5 ].copy( p5 )

        return self


    def copy( self, frustum:'Frustum' ):
        planes = self.planes

        for i in range(6):
            planes[ i ].copy( frustum.planes[ i ] )

        return self

    def setFromProjectionMatrix( self, m:'three.Matrix4' ):
        planes = self.planes
        me = m.elements
        me0 = me[ 0 ]; me1 = me[ 1 ]; me2 = me[ 2 ]; me3 = me[ 3 ]
        me4 = me[ 4 ]; me5 = me[ 5 ]; me6 = me[ 6 ]; me7 = me[ 7 ]
        me8 = me[ 8 ]; me9 = me[ 9 ]; me10 = me[ 10 ]; me11 = me[ 11 ]
        me12 = me[ 12 ]; me13 = me[ 13 ]; me14 = me[ 14 ]; me15 = me[ 15 ]

        planes[ 0 ].setComponents( me3 - me0, me7 - me4, me11 - me8, me15 - me12 ).normalize()
        planes[ 1 ].setComponents( me3 + me0, me7 + me4, me11 + me8, me15 + me12 ).normalize()
        planes[ 2 ].setComponents( me3 + me1, me7 + me5, me11 + me9, me15 + me13 ).normalize()
        planes[ 3 ].setComponents( me3 - me1, me7 - me5, me11 - me9, me15 - me13 ).normalize()
        planes[ 4 ].setComponents( me3 - me2, me7 - me6, me11 - me10, me15 - me14 ).normalize()
        planes[ 5 ].setComponents( me3 + me2, me7 + me6, me11 + me10, me15 + me14 ).normalize()

        return self

    def intersectsObject( self, object:'three.Mesh' ):
        geometry:'three.Geometry' = object.geometry
        if geometry.boundingSphere is None:
            geometry.computeBoundingSphere()
        _sphere.copy( geometry.boundingSphere ).applyMatrix4( object.matrixWorld )
        return self.intersectsSphere( _sphere )

    def intersectsSprite( self, sprite:'three.Sprite' ):
        _sphere.center.set( 0, 0, 0 )
        _sphere.radius = 0.7071067811865476
        _sphere.applyMatrix4( sprite.matrixWorld )

        return self.intersectsSphere( _sphere )


    def intersectsSphere( self, sphere:'Sphere' ):
        planes = self.planes
        center = sphere.center
        negRadius = - sphere.radius
        for i in range(6):
            distance = planes[ i ].distanceToPoint( center )

            if distance < negRadius:
                return False

        return True

    def intersectsBox( self, box ):

        planes = self.planes

        for i in range(6):

            plane = planes[ i ]

            # corner at max distance

            _vector.x = box.max.x if plane.normal.x > 0 else box.min.x
            _vector.y = box.max.y if plane.normal.y > 0 else box.min.y
            _vector.z = box.max.z if plane.normal.z > 0 else box.min.z

            if ( plane.distanceToPoint( _vector ) < 0 ):
                return False

        return True

    def containsPoint( self, point ):

        planes = self.planes

        for i in range(6):
            if ( planes[ i ].distanceToPoint( point ) < 0 ):
                return False

        return True

    def clone(self):
        return Frustum().copy(self)
