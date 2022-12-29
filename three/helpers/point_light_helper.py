from ..core import Geometry
from ..geometries import SphereGeometry
from ..materials import MeshBasicMaterial
from ..objects import Mesh

class PointLightHelper(Mesh):

    def __init__(self, light, sphere, color=None) -> None:
        
        if isinstance(sphere, Geometry):
            geometry = sphere
        elif isinstance(sphere, (int, float)):
            geometry = SphereGeometry( sphere, 4, 2 )
        else:
            raise TypeError('sphere must be a Geometry or a number(size)')

        material = MeshBasicMaterial(wireframe= True, fog= False, toneMapped= False)

        super().__init__( geometry, material )

        self.light = light

        self.color = color

        self._type = 'PointLightHelper'

        self.matrix = light.matrixWorld
        self.matrixAutoUpdate = False

        self.update()

    def dispose(self):
        self.geometry.dispose()
        self.material.dispose()

    def updateMatrixWorld(self, *args, **kwargs):
        self.update()
        super().updateMatrixWorld(*args, **kwargs)

    def update(self):
        self.light.updateWorldMatrix(True, False)
        if self.color != None:
            self.material.color.set(self.color)
        else:
            self.material.color.copy(self.light.color)