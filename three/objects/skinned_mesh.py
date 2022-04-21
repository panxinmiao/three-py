from .mesh import Mesh
from ..math import Matrix4, Vector3, Vector4
import math
from warnings import warn

_basePosition = Vector3()

_skinIndex = Vector4()
_skinWeight = Vector4()

_vector = Vector3()
_matrix = Matrix4()

class SkinnedMesh(Mesh):

    def __init__(self, geometry=None, material=None) -> None:
        super().__init__(geometry, material)

        self._type = 'SkinnedMesh'

        self.bindMode = 'attached'
        self.bindMatrix = Matrix4()
        self.bindMatrixInverse = Matrix4()

    
    def copy(self, source):
        super().copy( source )

        self.bindMode = source.bindMode
        self.bindMatrix.copy( source.bindMatrix )
        self.bindMatrixInverse.copy( source.bindMatrixInverse )

        self.skeleton = source.skeleton

        return self

    def bind( self, skeleton, bindMatrix = None):

        self.skeleton = skeleton
        if bindMatrix is None:
            self.updateMatrixWorld( True )
            self.skeleton.calculateInverses()
            bindMatrix = self.matrixWorld

        self.bindMatrix.copy( bindMatrix )
        self.bindMatrixInverse.copy( bindMatrix ).invert()

    def pose(self):
        self.skeleton.pose()

    def normalizeSkinWeights(self):
        vector = Vector4()
        skinWeight = self.geometry.attributes.skinWeight

        for i in range(skinWeight.count):
            vector.fromBufferAttribute( skinWeight, i )
            scale = 1.0 / vector.manhattanLength()

            if scale != math.inf:
                vector.multiplyScalar( scale )

            else:
                vector.set( 1, 0, 0, 0 ) # do something reasonable

            skinWeight.setXYZW( i, vector.x, vector.y, vector.z, vector.w )

    def updateMatrixWorld( self, force ):
        super().updateMatrixWorld( force )

        if self.bindMode == 'attached':

            self.bindMatrixInverse.copy( self.matrixWorld ).invert()

        elif self.bindMode == 'detached':

            self.bindMatrixInverse.copy( self.bindMatrix ).invert()

        else:
            warn( 'THREE.SkinnedMesh: Unrecognized bindMode: ' + self.bindMode )


    def boneTransform( self, index, target ):
        skeleton = self.skeleton
        geometry = self.geometry

        _skinIndex.fromBufferAttribute( geometry.attributes.skinIndex, index )
        _skinWeight.fromBufferAttribute( geometry.attributes.skinWeight, index )

        _basePosition.copy( target ).applyMatrix4( self.bindMatrix )

        target.set( 0, 0, 0 )

        for i in range(4):
            weight = _skinWeight.getComponent( i )

            if weight != 0:
                boneIndex = _skinIndex.getComponent( i )

                _matrix.multiplyMatrices( skeleton.bones[ boneIndex ].matrixWorld, skeleton.boneInverses[ boneIndex ] )

                target.addScaledVector( _vector.copy( _basePosition ).applyMatrix4( _matrix ), weight )

            return target.applyMatrix4( self.bindMatrixInverse )

