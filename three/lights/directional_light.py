from .light import Light
from ..core import Object3D

class DirectionalLight(Light):

    isDirectionalLight = True

    def __init__(self, color, intensity=1):
        super().__init__(color, intensity)
        self._type = 'DirectionalLight'

        self.position.set(0, 1, 0)
        self.updateMatrix()

        self.target = Object3D()

    def dispose(self):
        pass

    def copy(self, source: 'DirectionalLight'):
        super().copy(source)
        self.target = source.target.clone()

        return self
