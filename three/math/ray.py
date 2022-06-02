from .vector3 import Vector3
from ..structure import NoneAttribute
import math, three

_vector = Vector3()
_segCenter = Vector3()
_segDir = Vector3()
_diff = Vector3()

_edge1 = Vector3()
_edge2 = Vector3()
_normal = Vector3()

class Ray(NoneAttribute):
    def __init__(self, origin = None, direction = None) -> None:
        self.origin = origin or Vector3()
        self.direction = direction or Vector3( 0, 0, - 1 )

    def set( self, origin, direction ):
        self.origin.copy( origin )
        self.direction.copy( direction )

        return self


    def copy( self, ray:'Ray' ):
        self.origin.copy( ray.origin )
        self.direction.copy( ray.direction )

        return self

    def at( self, t, target:'Vector3' ):
        return target.copy( self.direction ).multiplyScalar( t ).add( self.origin )


    def lookAt( self, v ):
        self.direction.copy( v ).sub( self.origin ).normalize()
        return self

    def recast( self, t ):
        self.origin.copy( self.at( t, _vector ) )
        return self

    def closestPointToPoint( self, point:'Vector3', target:'Vector3' ):
        target.subVectors( point, self.origin )
        directionDistance = target.dot( self.direction )

        if directionDistance < 0:
            return target.copy( self.origin )

        return target.copy( self.direction ).multiplyScalar( directionDistance ).add( self.origin )

    def distanceToPoint( self, point ):
        return math.sqrt( self.distanceSqToPoint( point ) )

    def distanceSqToPoint( self, point ):
        directionDistance = _vector.subVectors( point, self.origin ).dot( self.direction )
        # point behind the ray
        if directionDistance < 0:
            return self.origin.distanceToSquared( point )

        _vector.copy( self.direction ).multiplyScalar( directionDistance ).add( self.origin )
        return _vector.distanceToSquared( point )

    def distanceSqToSegment( self, v0:'Vector3', v1:'Vector3', optionalPointOnRay:'Vector3' = None, optionalPointOnSegment:'Vector3' = None ):

        # from https:#github.com/pmjoniak/GeometricTools/blob/master/GTEngine/Include/Mathematics/GteDistRaySegment.h
        # It returns the min distance between the ray and the segment
        # defined by v0 and v1
        # It can also set two optional targets :
        # - The closest point on the ray
        # - The closest point on the segment

        _segCenter.copy( v0 ).add( v1 ).multiplyScalar( 0.5 )
        _segDir.copy( v1 ).sub( v0 ).normalize()
        _diff.copy( self.origin ).sub( _segCenter )

        segExtent = v0.distanceTo( v1 ) * 0.5
        a01 = - self.direction.dot( _segDir )
        b0 = _diff.dot( self.direction )
        b1 = - _diff.dot( _segDir )
        c = _diff.lengthSq()
        det = abs( 1 - a01 * a01 )

        if det > 0:
            # The ray and segment are not parallel.

            s0 = a01 * b1 - b0
            s1 = a01 * b0 - b1
            extDet = segExtent * det

            if s0 >= 0:
                if s1 >= - extDet:
                    if s1 <= extDet:
                        # region 0
                        # Minimum at interior points of ray and segment.
                        invDet = 1 / det
                        s0 *= invDet
                        s1 *= invDet
                        sqrDist = s0 * ( s0 + a01 * s1 + 2 * b0 ) + s1 * ( a01 * s0 + s1 + 2 * b1 ) + c
                    else:
                        # region 1
                        s1 = segExtent
                        s0 = max( 0, - ( a01 * s1 + b0 ) )
                        sqrDist = - s0 * s0 + s1 * ( s1 + 2 * b1 ) + c

                else:
                    # region 5
                    s1 = - segExtent
                    s0 = max( 0, - ( a01 * s1 + b0 ) )
                    sqrDist = - s0 * s0 + s1 * ( s1 + 2 * b1 ) + c

            else:
                if s1 <= - extDet:
                    # region 4
                    s0 = max( 0, - ( - a01 * segExtent + b0 ) )
                    s1 = - segExtent if ( s0 > 0 ) else min( max( - segExtent, - b1 ), segExtent )
                    sqrDist = - s0 * s0 + s1 * ( s1 + 2 * b1 ) + c

                elif s1 <= extDet:
                    # region 3
                    s0 = 0
                    s1 = min( max( - segExtent, - b1 ), segExtent )
                    sqrDist = s1 * ( s1 + 2 * b1 ) + c

                else:
                    # region 2
                    s0 = max( 0, - ( a01 * segExtent + b0 ) )
                    s1 = segExtent if( s0 > 0 ) else min( max( - segExtent, - b1 ), segExtent )
                    sqrDist = - s0 * s0 + s1 * ( s1 + 2 * b1 ) + c
        else:
            # Ray and segment are parallel.
            s1 = - segExtent if ( a01 > 0 ) else segExtent
            s0 = max( 0, - ( a01 * s1 + b0 ) )
            sqrDist = - s0 * s0 + s1 * ( s1 + 2 * b1 ) + c

        if optionalPointOnRay:
            optionalPointOnRay.copy( self.direction ).multiplyScalar( s0 ).add( self.origin )

        if optionalPointOnSegment:
            optionalPointOnSegment.copy( _segDir ).multiplyScalar( s1 ).add( _segCenter )

        return sqrDist

    def intersectSphere( self, sphere:'three.Sphere', target ):

        _vector.subVectors( sphere.center, self.origin )
        tca = _vector.dot( self.direction )
        d2 = _vector.dot( _vector ) - tca * tca
        radius2 = sphere.radius * sphere.radius

        if d2 > radius2:
            return None

        thc = math.sqrt( radius2 - d2 )

        # t0 = first intersect point - entrance on front of sphere
        t0 = tca - thc

        # t1 = second intersect point - exit point on back of sphere
        t1 = tca + thc

        # test to see if both t0 and t1 are behind the ray - if so, return null
        if t0 < 0 and t1 < 0 :
            return None

        # test to see if t0 is behind the ray:
        # if it is, the ray is inside the sphere, so return the second exit point scaled by t1,
        # in order to always return an intersect point that is in front of the ray.
        if t0 < 0:
            return self.at( t1, target )

        # else t0 is in front of the ray, so return the first collision point scaled by t0
        return self.at( t0, target )

    def intersectsSphere( self, sphere:'three.Sphere' ):
        return self.distanceSqToPoint( sphere.center ) <= ( sphere.radius * sphere.radius )

    def distanceToPlane( self, plane:'three.Plane' ):
        denominator = plane.normal.dot( self.direction )
        if denominator == 0:
            # line is coplanar, return origin
            if plane.distanceToPoint( self.origin ) == 0:
                return 0
            # Null is preferable to undefined since undefined means.... it is undefined
            return None

        t = - ( self.origin.dot( plane.normal ) + plane.constant ) / denominator

        # Return if the ray never intersects the plane

        return t if t >= 0 else None

    def intersectPlane( self, plane:'three.Plane', target ):
        t = self.distanceToPlane( plane )

        if t is None:
            return None
        return self.at( t, target )

    def intersectsPlane( self, plane:'three.Plane' ):
        # check if the ray lies on the plane first
        distToPoint = plane.distanceToPoint( self.origin )
        if distToPoint == 0:
            return True

        denominator = plane.normal.dot( self.direction )
        if denominator * distToPoint < 0:
            return True
        # ray origin is behind the plane (and is pointing behind it)
        return False

    def intersectBox( self, box:'three.Box3', target ):
        invdirx = 1 / self.direction.x
        invdiry = 1 / self.direction.y
        invdirz = 1 / self.direction.z

        origin = self.origin

        if invdirx >= 0:
            tmin = ( box.min.x - origin.x ) * invdirx
            tmax = ( box.max.x - origin.x ) * invdirx
        else:
            tmin = ( box.max.x - origin.x ) * invdirx
            tmax = ( box.min.x - origin.x ) * invdirx

        if invdiry >= 0:
            tymin = ( box.min.y - origin.y ) * invdiry
            tymax = ( box.max.y - origin.y ) * invdiry

        else:
            tymin = ( box.max.y - origin.y ) * invdiry
            tymax = ( box.min.y - origin.y ) * invdiry


        if ( ( tmin > tymax ) or ( tymin > tmax ) ):
            return None

        # These lines also handle the case where tmin or tmax is NaN
        # (result of 0 * Infinity). x !== x returns true if x is NaN

        if tymin > tmin or tmin != tmin:
            tmin = tymin

        if tymax < tmax or tmax != tmax:
            tmax = tymax

        if invdirz >= 0:
            tzmin = ( box.min.z - origin.z ) * invdirz
            tzmax = ( box.max.z - origin.z ) * invdirz

        else:
            tzmin = ( box.max.z - origin.z ) * invdirz
            tzmax = ( box.min.z - origin.z ) * invdirz

        if tmin > tzmax or tzmin > tmax:
            return None

        if tzmin > tmin or tmin != tmin:
            tmin = tzmin

        if tzmax < tmax or tmax != tmax:
            tmax = tzmax

        # return point closest to the ray (positive side)

        if tmax < 0 :
            return None

        return self.at( tmin if tmin >= 0 else tmax, target )


    def intersectsBox( self, box ):
        return self.intersectBox( box, _vector ) != None

    def intersectTriangle( self, a, b, c, backfaceCulling, target ):

        # Compute the offset origin, edges, and normal.

        # from https:#github.com/pmjoniak/GeometricTools/blob/master/GTEngine/Include/Mathematics/GteIntrRay3Triangle3.h

        _edge1.subVectors( b, a )
        _edge2.subVectors( c, a )
        _normal.crossVectors( _edge1, _edge2 )

        # Solve Q + t*D = b1*E1 + b2*E2 (Q = kDiff, D = ray direction,
        # E1 = kEdge1, E2 = kEdge2, N = Cross(E1,E2)) by
        #   |Dot(D,N)|*b1 = sign(Dot(D,N))*Dot(D,Cross(Q,E2))
        #   |Dot(D,N)|*b2 = sign(Dot(D,N))*Dot(D,Cross(E1,Q))
        #   |Dot(D,N)|*t = -sign(Dot(D,N))*Dot(Q,N)
        DdN = self.direction.dot( _normal )

        if DdN > 0:
            if backfaceCulling:
                return None
            sign = 1

        elif DdN < 0:
            sign = - 1
            DdN = - DdN

        else:
            return None


        _diff.subVectors( self.origin, a )
        DdQxE2 = sign * self.direction.dot( _edge2.crossVectors( _diff, _edge2 ) )

        # b1 < 0, no intersection
        if DdQxE2 < 0:
            return None

        DdE1xQ = sign * self.direction.dot( _edge1.cross( _diff ) )

        # b2 < 0, no intersection
        if DdE1xQ < 0:
            return None

        # b1+b2 > 1, no intersection
        if DdQxE2 + DdE1xQ > DdN:
            return None

        # Line intersects triangle, check if ray does.
        QdN = - sign * _diff.dot( _normal )

        # t < 0, no intersection
        if QdN < 0:
            return None

        # Ray intersects triangle.
        return self.at( QdN / DdN, target )

    def applyMatrix4( self, matrix4 ):
        self.origin.applyMatrix4( matrix4 )
        self.direction.transformDirection( matrix4 )

        return self

    def equals( self, ray:'Ray' ):
        return ray.origin.equals( self.origin ) and ray.direction.equals( self.direction )

    def clone(self):
        return Ray().copy( self )
