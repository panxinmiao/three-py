from ..core import Object3D
from ..math import Color

class Light(Object3D):

    isLight = True

    def __init__(self, color, intensity = 1):
        super().__init__()
        self._type = 'Light'

        self.color = Color( color )
        self.intensity = intensity

    
    def dispose(self):
        pass


    def copy(self, source, recursive=True):
        super().copy( source, recursive )

        self.color.copy( source.color )
        self.intensity = source.intensity
        return self