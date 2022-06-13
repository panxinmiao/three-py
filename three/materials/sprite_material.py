from .material import Material
from ..math import Color

class SpriteMaterial(Material):

    def __init__(self, parameters={}, **kwargs) -> None:
        super().__init__()

        self._type = 'SpriteMaterial'

        self.color =  Color(0xffffff)

        self.map = None

        self.alphaMap = None

        self.rotation = 0

        self.sizeAttenuation = True

        self.transparent = True

        self.fog = True

        if not isinstance(parameters, dict):
            parameters = parameters.__dict__
            
        parameters = parameters.copy()
        parameters.update(kwargs)

        self.setValues( parameters )

    def copy(self, source):
        
        super().copy(source)

        self.color.copy(source.color)

        self.map = source.map

        self.alphaMap = source.alphaMap

        self.rotation = source.rotation

        self.sizeAttenuation = source.sizeAttenuation

        self.fog = source.fog

        return self
