from .mesh import Mesh
from ..math import Matrix4
from ..core import InstancedBufferAttribute
from ..structure import Float32Array

_instanceLocalMatrix = Matrix4()
_instanceWorldMatrix = Matrix4()
_instanceIntersects = []
_mesh = Mesh()

class InstancedMesh(Mesh):

    def __init__(self, geometry, material, count) -> None:
        super().__init__(geometry, material)

        self.instanceMatrix = InstancedBufferAttribute( Float32Array( count * 16 ), 16 )
        self.instanceColor = None

        self.count = count
        self.frustumCulled = False

    def copy(self, source:'InstancedMesh') -> 'InstancedMesh':
        super().copy(source)
        self.instanceMatrix.copy(source.instanceMatrix)
        self.instanceColor = source.instanceColor.clone() if source.instanceColor else None
        self.count = source.count
        return self

    def getColorAt(self, index, color):
        color.fromArray(self.instanceColor.array, index * 3)


    def getMatrixAt(self, index, matrix):
        matrix.fromArray(self.instanceMatrix.array, index * 16)

    def rayCast(self, raycaster, intersects):
        matrixWorld = self.matrixWorld
        raycastTimes = self.count

        _mesh.geometry = self.geometry
        _mesh.material = self.material

        if _mesh.material is None:
            return

        for instanceId in range(raycastTimes):

            # calculate the world matrix for each instance
            self.getMatrixAt(instanceId, _instanceLocalMatrix)

            _instanceWorldMatrix.multiplyMatrices(matrixWorld, _instanceLocalMatrix)

            # the mesh represents this single instance
            _mesh.matrixWorld = _instanceWorldMatrix
            _mesh.raycast(raycaster, _instanceIntersects)

            # process the result of raycast
            for intersect in _instanceIntersects:
                intersect.instanceId = instanceId
                intersect.object = self
                intersects.append(intersect)

            _instanceIntersects.clear()

    def setColorAt(self, index, color):

        if self.instanceColor is None:
            self.instanceColor = InstancedBufferAttribute(Float32Array(self.instanceMatrix.count * 3), 3)
        
        color.toArray(self.instanceColor.array, index * 3)

    def setMatrixAt(self, index, matrix):
        matrix.toArray(self.instanceMatrix.array, index * 16)


    def updateMorphTargets(self):
        pass

    def dispose(self):
        self.dispatchEvent({type: 'dispose'})
