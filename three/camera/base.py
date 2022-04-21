from ..core import Object3D
from ..math import Matrix4
import three

class Camera(Object3D):
    def __init__(self, name=''):
        super().__init__(name = name)
        self._type = 'Camera'
        self.matrixWorldInverse = Matrix4()
        self.projectionMatrix = Matrix4()
        self.projectionMatrixInverse =  Matrix4()

    def copy( self, source:'Camera', recursive ):

        super().copy( source, recursive )

        self.matrixWorldInverse.copy( source.matrixWorldInverse )

        self.projectionMatrix.copy( source.projectionMatrix )
        self.projectionMatrixInverse.copy( source.projectionMatrixInverse )

        return self


    def getWorldDirection(self, target: three.Vector3 ):
        self.updateMatrixWorld(True, False)

        e = self.matrixWorld.elements
        return target.set( - e[ 8 ], - e[ 9 ], - e[ 10 ] ).normalize()


    def updateMatrixWorld(self, force = False):
        super().updateMatrixWorld(force = force)

        self.matrixWorldInverse.getInverse(self.matrixWorld)

    
    def updateWorldMatrix( self, updateParents, updateChildren ):

        super().updateWorldMatrix( updateParents, updateChildren )

        self.matrixWorldInverse.copy( self.matrixWorld ).invert()


    def clone(self):
        return self.__class__().copy( self )