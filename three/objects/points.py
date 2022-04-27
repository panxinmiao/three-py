from ..math import Sphere, Ray, Matrix4, Vector3
from ..core import Object3D, BufferGeometry
from ..materials import PointsMaterial
from warnings import warn
import math

_inverseMatrix = Matrix4()
_ray = Ray()
_sphere = Sphere()
_position = Vector3()

class Points(Object3D):

    def __init__(self, geometry = None, material = None):
        super().__init__()
        geometry = geometry or BufferGeometry()
        material = material or PointsMaterial()

        self.geometry = geometry
        self.material = material

        self.updateMorphTargets()

    def copy( self, source ):

        super().copy( source )

        self.material = source.material
        self.geometry = source.geometry

        return self

    def raycast( self, raycaster, intersects ):
        geometry = self.geometry
        matrixWorld = self.matrixWorld
        threshold = raycaster.params.Points.threshold
        drawRange = geometry.drawRange

        # Checking boundingSphere distance to ray

        if geometry.boundingSphere is None:
            geometry.computeBoundingSphere()

        _sphere.copy( geometry.boundingSphere )
        _sphere.applyMatrix4( matrixWorld )
        _sphere.radius += threshold

        if raycaster.ray.intersectsSphere( _sphere ) == False:
            return

        #

        _inverseMatrix.copy( matrixWorld ).invert()
        _ray.copy( raycaster.ray ).applyMatrix4( _inverseMatrix )

        localThreshold = threshold / ( ( self.scale.x + self.scale.y + self.scale.z ) / 3 )
        localThresholdSq = localThreshold * localThreshold

        if geometry.isBufferGeometry:

            index = geometry.index
            attributes = geometry.attributes
            positionAttribute = attributes.position

            if index:
                start = max( 0, drawRange.start )
                end = min( index.count, ( drawRange.start + drawRange.count ) )

                for i in range( start, end ):
                    a = index.getX( i )
                    _position.fromBufferAttribute( positionAttribute, a )
                    testPoint( _position, a, localThresholdSq, matrixWorld, raycaster, intersects, self )

            else:
                start = max( 0, drawRange.start )
                end = min( positionAttribute.count, ( drawRange.start + drawRange.count ) )

                for i in range( start, end ):
                    _position.fromBufferAttribute( positionAttribute, i )
                    testPoint( _position, i, localThresholdSq, matrixWorld, raycaster, intersects, self )

        else:
            warn( 'THREE.Points.raycast() no longer supports THREE.Geometry. Use THREE.BufferGeometry instead.' )

    def updateMorphTargets(self):
        geometry = self.geometry

        morphAttributes = geometry.morphAttributes
        keys = morphAttributes.keys()

        if len(keys) > 0:
            morphAttribute = morphAttributes[ keys[ 0 ] ]
            if morphAttribute is not None:
                self.morphTargetInfluences = []
                self.morphTargetDictionary = {}
                for m in range(len(morphAttribute)):
                    name = morphAttribute[ m ].name or str( m )
                    self.morphTargetInfluences.append( 0 )
                    self.morphTargetDictionary[ name ] = m



def testPoint( point, index, localThresholdSq, matrixWorld, raycaster, intersects, object ):
    rayPointDistanceSq = _ray.distanceSqToPoint( point )

    if rayPointDistanceSq < localThresholdSq:
        intersectPoint = Vector3()

        _ray.closestPointToPoint( point, intersectPoint )
        intersectPoint.applyMatrix4( matrixWorld )

        distance = raycaster.ray.origin.distanceTo( intersectPoint )

        if distance < raycaster.near or distance > raycaster.far:
            return

        intersects.append( {
            'distance': distance,
            'distanceToRay': math.sqrt( rayPointDistanceSq ),
            'point': intersectPoint,
            'index': index,
            'face': None,
            'object': object
        } )

