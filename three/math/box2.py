from ..structure import NoneAttribute
from .vector2 import Vector2

_vector = Vector2()

class Box2(NoneAttribute):

    isBox2 = True

    def __init__( self,min = None, max = None ) -> None:
        if min is None:
            min = Vector2( float('inf'), float('inf') )
        if max is None:
            max = Vector2( float('-inf'), float('-inf') )

        self.min = min
        self.max = max

    def set( self, min, max ) -> 'Box2':
        self.min.copy( min )
        self.max.copy( max )
        return self


    def setFromPoints( self, points ) -> 'Box2':
        self.makeEmpty()

        for p in points:
            self.expandByPoint( p )
        
        return self


    def setFromCenterAndSize( self, center, size ) -> 'Box2':
        halfSize = _vector.copy( size ).multiplyScalar( 0.5 )
        self.min.copy( center ).sub( halfSize )
        self.max.copy( center ).add( halfSize )

        return self


    def clone(self) -> 'Box2':
        return Box2().copy(self)


    def copy( self, box ) -> 'Box2':
        self.min.copy( box.min )
        self.max.copy( box.max )

        return self


    def makeEmpty(self) -> 'Box2':
        self.min.x = self.min.y = float('inf')
        self.max.x = self.max.y = float('-inf')

        return self


    def isEmpty(self) -> 'bool':

        # self is a more robust check for empty than ( volume <= 0 ) because volume can get positive with two negative axes
        return ( self.max.x < self.min.x ) or ( self.max.y < self.min.y )

    def getCenter( self, target ) -> 'Vector2':
        return target.set( 0, 0 ) if self.isEmpty() else target.addVectors( self.min, self.max ).multiplyScalar( 0.5 )

    def getSize(self, target ) -> 'Vector2':
        return target.set( 0, 0 ) if self.isEmpty() else target.subVectors( self.max, self.min )

    def expandByPoint( self, point ) -> 'Box2':
        self.min.min( point )
        self.max.max( point )

        return self

    def expandByVector( self, vector ) -> 'Box2':

        self.min.sub( vector )
        self.max.add( vector )

        return self


    def expandByScalar( self, scalar ) -> 'Box2':

        self.min.addScalar( - scalar )
        self.max.addScalar( scalar )

        return self


    def containsPoint( self, point ) -> 'bool':
        return False if (point.x < self.min.x or point.x > self.max.x or point.y < self.min.y or point.y > self.max.y) else True


    def containsBox( self, box ) -> 'bool':
        return self.min.x <= box.min.x and box.max.x <= self.max.x and self.min.y <= box.min.y and box.max.y <= self.max.y


    def getParameter( self, point, target )-> 'Vector2':

        # This can potentially have a divide by zero if the box
        # has a size dimension of 0.
        return target.set(
            ( point.x - self.min.x ) / ( self.max.x - self.min.x ),
            ( point.y - self.min.y ) / ( self.max.y - self.min.y )
        )


    def intersectsBox( self, box ) -> 'bool':

        # using 4 splitting planes to rule out intersections
        return False if (box.max.x < self.min.x or box.min.x > self.max.x or box.max.y < self.min.y or box.min.y > self.max.y) else True

    def clampPoint( self, point, target ) -> 'Vector2':
        return target.copy( point ).clamp( self.min, self.max )

    def distanceToPoint( self, point ) -> 'float':
        clampedPoint = _vector.copy( point ).clamp( self.min, self.max )
        return clampedPoint.sub( point ).length()

    def intersect( self, box ) -> 'Box2':

        self.min.max( box.min )
        self.max.min( box.max )

        return self

    def union( self, box ) -> 'Box2':

        self.min.min( box.min )
        self.max.max( box.max )

        return self

    def translate( self, offset ) -> 'Box2':

        self.min.add( offset )
        self.max.add( offset )

        return self

    def __eq__( self, box ) -> 'bool':
        return box.min.equals( self.min ) and box.max.equals( self.max )

    equals = __eq__