import three, math
from ..structure import NoneAttribute
from .vector3 import Vector3

class Box3(NoneAttribute):

    def __init__( self,min = None, max = None ) -> None:
        if min is None:
            min = Vector3( math.inf, math.inf, math.inf)
        if max is None:
            max = Vector3( -math.inf, -math.inf, -math.inf )

        self.min = min
        self.max = max

    def __repr__(self) -> str:
        return f"Box3({self.min}, {self.max})"

    def set( self, min, max ) -> 'Box3':
        self.min.copy( min )
        self.max.copy( max )
        return self

    def setFromArray( self, array ):
        minX = math.inf
        minY = math.inf
        minZ = math.inf

        maxX = -math.inf
        maxY = -math.inf
        maxZ = -math.inf

        for i in range(0, len(array), 3):
            x = array[ i ]
            y = array[ i + 1 ]
            z = array[ i + 2 ]

            if x < minX:
                minX = x
            if y < minY:
                minY = y
            if z < minZ:
                minZ = z

            if x > maxX:
                maxX = x
            if y > maxY:
                maxY = y
            if z > maxZ:
                maxZ = z

        self.min.set( minX, minY, minZ )
        self.max.set( maxX, maxY, maxZ )

        return self

    def setFromBufferAttribute( self, attribute:'three.BufferAttribute' ):
        minX = math.inf
        minY = math.inf
        minZ = math.inf
        maxX = -math.inf
        maxY = -math.inf
        maxZ = -math.inf
        for i in range(attribute.count): 
            x = attribute.getX( i )
            y = attribute.getY( i )
            z = attribute.getZ( i )

            if x < minX:
                minX = x
            if y < minY:
                minY = y
            if z < minZ:
                minZ = z

            if x > maxX:
                maxX = x
            if y > maxY:
                maxY = y
            if z > maxZ:
                maxZ = z

        self.min.set( minX, minY, minZ )
        self.max.set( maxX, maxY, maxZ )

        return self

    def setFromPoints( self, points ):
        self.makeEmpty()
        for point in points:
            self.expandByPoint( point )
        return self

    def setFromCenterAndSize( self, center, size ):
        halfSize = _vector.copy( size ).multiplyScalar( 0.5 )

        self.min.copy( center ).sub( halfSize )
        self.max.copy( center ).add( halfSize )

        return self

    def setFromObject( self, object, precise = False ):
        self.makeEmpty()
        return self.expandByObject( object, precise )

    def clone( self ):
        return Box3.copy( self )

    def copy( self, box: 'Box3' ):
        self.min.copy( box.min )
        self.max.copy( box.max )
        return self

    def makeEmpty( self ):
        self.min.x = self.min.y = self.min.z = math.inf
        self.max.x = self.max.y = self.max.z =  -math.inf

        return self

    def isEmpty( self ):
        # self is a more robust check for empty than ( volume <= 0 ) because volume can get positive with two negative axes
        return ( self.max.x < self.min.x ) or ( self.max.y < self.min.y ) or ( self.max.z < self.min.z )


    def getCenter( self, target:'three.Vector3' ):
        return target.set( 0, 0, 0 ) if self.isEmpty() else target.addVectors( self.min, self.max ).multiplyScalar( 0.5 )


    def getSize( self, target:'three.Vector3' ):
        return target.set( 0, 0, 0 ) if self.isEmpty() else target.subVectors( self.max, self.min )

    def expandByPoint( self, point ):
        self.min.min( point )
        self.max.max( point )
        return self

    def expandByVector( self, vector:'three.Vector3' ):
        self.min.sub( vector )
        self.max.add( vector )
        return self

    def expandByScalar( self, scalar ):
        self.min.addScalar( - scalar )
        self.max.addScalar( scalar )
        return self

    
    def expandByObject( self, object:'three.Mesh', precise = False ):
        # Computes the world-axis-aligned bounding box of an object (including its children),
        # accounting for both the object's, and children's, world transforms

        object.updateMatrixWorld( False, False )
        geometry:'three.Geometry' = object.geometry

        if geometry is not None:
            if precise and geometry.attributes and geometry.attributes.position:
                position = geometry.attributes.position
                for i in range(position.count):
                    _vector.fromBufferAttribute( position, i ).applyMatrix4( object.matrix_world )
                    self.expandByPoint( _vector )
            else:
                if geometry.boundingBox is None:
                    geometry.compute_bounding_box()
                    # geometry.computeBoundingBox()

                _box.copy( geometry.boundingBox )
                _box.applyMatrix4( object.matrixWorld )

                self.union( _box )

        children = object.children

        for child in children:
            self.expandByObject( child, precise )

        return self

    
    def containsPoint( self, point ):
        return False if (point.x < self.min.x or point.x > self.max.x or 
                        point.y < self.min.y or point.y > self.max.y or 
                        point.z < self.min.z or point.z > self.max.z) else True

    def containsBox( self, box ):
        return (self.min.x <= box.min.x and box.max.x <= self.max.x and
                self.min.y <= box.min.y and box.max.y <= self.max.y and
                self.min.z <= box.min.z and box.max.z <= self.max.z)

    def getParameter( self, point, target ):

        # This can potentially have a divide by zero if the box
        # has a size dimension of 0.
        return target.set(
            ( point.x - self.min.x ) / ( self.max.x - self.min.x ),
            ( point.y - self.min.y ) / ( self.max.y - self.min.y ),
            ( point.z - self.min.z ) / ( self.max.z - self.min.z )
        )

    def intersectsBox( self, box:'Box3' ):
        # using 6 splitting planes to rule out intersections.
        return False if (box.max.x < self.min.x or box.min.x > self.max.x or
                        box.max.y < self.min.y or box.min.y > self.max.y or
                        box.max.z < self.min.z or box.min.z > self.max.z ) else True

    def intersectsSphere( self, sphere: 'three.Sphere' ):
        # Find the point on the AABB closest to the sphere center.
        self.clampPoint( sphere.center, _vector )

        # If that point is inside the sphere, the AABB and sphere intersect.
        return _vector.distanceToSquared( sphere.center ) <= ( sphere.radius * sphere.radius )


    def intersectsPlane( self, plane:'three.Plane' ):

        # We compute the minimum and maximum dot product values. If those values
        # are on the same side (back or front) of the plane, then there is no intersection.

        min = None
        max = None
        if plane.normal.x > 0:
            min = plane.normal.x * self.min.x
            max = plane.normal.x * self.max.x
        else:
            min = plane.normal.x * self.max.x
            max = plane.normal.x * self.min.x

        if plane.normal.y > 0:
            min += plane.normal.y * self.min.y
            max += plane.normal.y * self.max.y

        else:

            min += plane.normal.y * self.max.y
            max += plane.normal.y * self.min.y

        if plane.normal.z > 0:

            min += plane.normal.z * self.min.z
            max += plane.normal.z * self.max.z

        else:

            min += plane.normal.z * self.max.z
            max += plane.normal.z * self.min.z

        return ( min <= - plane.constant and max >= - plane.constant )


    def intersectsTriangle( self, triangle ):
        if self.isEmpty():
            return False
        # compute box center and extents
        self.getCenter( _center )
        _extents.subVectors( self.max, _center )

        # translate triangle to aabb origin
        _v0.subVectors( triangle.a, _center )
        _v1.subVectors( triangle.b, _center )
        _v2.subVectors( triangle.c, _center )

        # compute edge vectors for triangle
        _f0.subVectors( _v1, _v0 )
        _f1.subVectors( _v2, _v1 )
        _f2.subVectors( _v0, _v2 )

        # test against axes that are given by cross product combinations of the edges of the triangle and the edges of the aabb
        # make an axis testing of each of the 3 sides of the aabb against each of the 3 sides of the triangle = 9 axis of separation
        # axis_ij = u_i x f_j (u0, u1, u2 = face normals of aabb = x,y,z axes vectors since aabb is axis aligned)
        axes = [
            0, - _f0.z, _f0.y, 0, - _f1.z, _f1.y, 0, - _f2.z, _f2.y,
            _f0.z, 0, - _f0.x, _f1.z, 0, - _f1.x, _f2.z, 0, - _f2.x,
            - _f0.y, _f0.x, 0, - _f1.y, _f1.x, 0, - _f2.y, _f2.x, 0
        ]
        if not satForAxes( axes, _v0, _v1, _v2, _extents ):
            return False

        # test 3 face normals from the aabb
        axes = [ 1, 0, 0, 0, 1, 0, 0, 0, 1 ]
        if not satForAxes( axes, _v0, _v1, _v2, _extents ):
            return False

        # finally testing the face normal of the triangle
        # use already existing triangle edge vectors here
        _triangleNormal.crossVectors( _f0, _f1 )
        axes = [ _triangleNormal.x, _triangleNormal.y, _triangleNormal.z ]

        return satForAxes( axes, _v0, _v1, _v2, _extents )

    def clampPoint( self, point, target ):
        return target.copy( point ).clamp( self.min, self.max )

    def distanceToPoint( self, point ):
        clampedPoint = _vector.copy( point ).clamp( self.min, self.max )
        return clampedPoint.sub( point ).length()

    def getBoundingSphere( self, target ):
        self.getCenter( target.center )
        target.radius = self.getSize( _vector ).length() * 0.5
        return target

    def intersect( self, box ):
        self.min.max( box.min )
        self.max.min( box.max )
        # ensure that if there is no overlap, the result is fully empty, not slightly empty with non-inf/+inf values that will cause subsequence intersects to erroneously return valid values.
        if self.isEmpty():
            self.makeEmpty()

        return self

    def union( self, box ):
        self.min.min( box.min )
        self.max.max( box.max )
        return self

    def applyMatrix4( self, matrix ):
        # transform of empty box is an empty box.
        if self.isEmpty():
            return self
        # NOTE: I am using a binary pattern to specify all 2^3 combinations below
        _points[ 0 ].set( self.min.x, self.min.y, self.min.z ).applyMatrix4( matrix ); # 000
        _points[ 1 ].set( self.min.x, self.min.y, self.max.z ).applyMatrix4( matrix ); # 001
        _points[ 2 ].set( self.min.x, self.max.y, self.min.z ).applyMatrix4( matrix ); # 010
        _points[ 3 ].set( self.min.x, self.max.y, self.max.z ).applyMatrix4( matrix ); # 011
        _points[ 4 ].set( self.max.x, self.min.y, self.min.z ).applyMatrix4( matrix ); # 100
        _points[ 5 ].set( self.max.x, self.min.y, self.max.z ).applyMatrix4( matrix ); # 101
        _points[ 6 ].set( self.max.x, self.max.y, self.min.z ).applyMatrix4( matrix ); # 110
        _points[ 7 ].set( self.max.x, self.max.y, self.max.z ).applyMatrix4( matrix ); # 111

        self.setFromPoints( _points )

        return self

    def translate( self, offset ):
        self.min.add( offset )
        self.max.add( offset )
        return self

    def equals( self, box ):
        return box.min.equals( self.min ) and box.max.equals( self.max )


_points = [
    Vector3(),
    Vector3(),
    Vector3(),
    Vector3(),
    Vector3(),
    Vector3(),
    Vector3(),
    Vector3()
]

_vector = Vector3()

_box = Box3()

# triangle centered vertices

_v0 = Vector3()
_v1 = Vector3()
_v2 = Vector3()

# triangle edge vectors

_f0 = Vector3()
_f1 = Vector3()
_f2 = Vector3()

_center = Vector3()
_extents = Vector3()
_triangleNormal = Vector3()
_testAxis = Vector3()

def satForAxes( axes, v0, v1, v2, extents ):
    i = 0
    j = len(axes) - 3
    while i <= j:
        _testAxis.fromArray( axes, i )
        # project the aabb onto the seperating axis
        r = extents.x * abs( _testAxis.x ) + extents.y * abs( _testAxis.y ) + extents.z * abs( _testAxis.z )
        # project all 3 vertices of the triangle onto the seperating axis
        p0 = v0.dot( _testAxis )
        p1 = v1.dot( _testAxis )
        p2 = v2.dot( _testAxis )
        # actual test, basically see if either of the most extreme of the triangle points intersects r
        if ( max( - max( p0, p1, p2 ), min( p0, p1, p2 ) ) > r ):
            # points of the projected triangle are outside the projected half-length of the aabb
            # the axis is seperating and we can exit
            return False

    return True