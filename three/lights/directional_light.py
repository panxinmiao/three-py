from .light import Light
from .directional_light_shadow import DirectionalLightShadow
from ..core import Object3D

class DirectionalLight(Light):

    isDirectionalLight = True

    def __init__(self, color, intensity=1):
        super().__init__(color, intensity)
        self._type = 'DirectionalLight'

        self.position.copy(Object3D.DefaultUp)
        self.updateMatrix()

        self.target = Object3D()

        self.shadow = DirectionalLightShadow()

    def dispose(self):
        self.shadow.dispose()

    def copy(self, source: 'DirectionalLight'):
        super().copy(source)
        self.target = source.target.clone()
        self.shadow = source.shadow.clone()

        return self
