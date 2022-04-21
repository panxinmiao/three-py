from .vector3 import Vector3
from .math_utils import clamp
from ..structure import NoneAttribute

_startP = Vector3()
_startEnd = Vector3()

class Line3(NoneAttribute):
    def __init__(self, start = None, end = None):
        self.start = start or Vector3()
        self.end = end or Vector3()

    def set( self, start, end ) -> 'Line3':
        self.start.copy( start )
        self.end.copy( end )

        return self

    def copy( self, line ) -> 'Line3':

        self.start.copy( line.start )
        self.end.copy( line.end )

        return self

    def getCenter( self, target: 'Vector3' ) -> 'Vector3':
        return target.addVectors( self.start, self.end ).multiplyScalar( 0.5 )


    def delta( self, target: 'Vector3' ) -> 'Vector3':
        return target.subVectors( self.end, self.start )


    def distanceSq(self):
        return self.start.distanceToSquared( self.end )

    def distance(self):
        return self.start.distanceTo( self.end )

    def at( self, t, target ) -> 'Vector3':
        return self.delta( target ).multiplyScalar( t ).add( self.start )

    def closestPointToPointParameter(self, point, clampToLine ):

        _startP.subVectors( point, self.start )
        _startEnd.subVectors( self.end, self.start )

        startEnd2 = _startEnd.dot( _startEnd )
        startEnd_startP = _startEnd.dot( _startP )

        t = startEnd_startP / startEnd2

        if clampToLine:
            t = clamp( t, 0, 1 )

        return t

    def closestPointToPoint( self, point, clampToLine, target ) -> 'Vector3':
        t = self.closestPointToPointParameter( point, clampToLine )
        return self.delta( target ).multiplyScalar( t ).add( self.start )


    def applyMatrix4( self, matrix ) -> 'Line3':
        self.start.applyMatrix4( matrix )
        self.end.applyMatrix4( matrix )

        return self

    def __eq__(self, __o: 'object') -> bool:
        return isinstance(__o, Line3) and __o.start.equals( self.start ) and __o.end.equals( self.end )

    equals = __eq__

    def clone( self ) -> 'Line3':
        return Line3().copy( self )

