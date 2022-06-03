from .material import Material
from ..math import Color

class PointsMaterial(Material):

    def __init__(self, parameters={}, **kwargs) -> None:
        super().__init__()

        self.type = 'PointsMaterial'

        self.color = Color( 0xffffff )

        self.map = None

        self.alphaMap = None

        self.size = 1
        self.sizeAttenuation = True

        if not isinstance(parameters, dict):
            parameters = parameters.__dict__
            
        parameters = parameters.copy()
        parameters.update(kwargs)

        self.setValues( parameters )



    def copy( self, source ):

        super().copy( source )

        self.color.copy( source.color )

        self.map = source.map

        self.alphaMap = source.alphaMap

        self.size = source.size
        self.sizeAttenuation = source.sizeAttenuation

        return self
