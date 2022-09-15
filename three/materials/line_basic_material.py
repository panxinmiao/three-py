
from .material import Material
from ..math import Color

class LineBasicMaterial(Material):

    isLineBasicMaterial = True

    def __init__(self, parameters={}, **kwargs) -> None:

        super().__init__()

        self._type = 'LineBasicMaterial'

        self.color =  Color( 0xffffff )

        self.linewidth = 1
        self.linecap = 'round'
        self.linejoin = 'round'

        if not isinstance(parameters, dict):
            parameters = parameters.__dict__
            
        parameters = parameters.copy()
        parameters.update(kwargs)

        self.setValues( parameters )

    def copy( self, source: 'Material' ):

        super().copy( source )

        self.color.copy( source.color )

        self.linewidth = source.linewidth
        self.linecap = source.linecap
        self.linejoin = source.linejoin

        return self
