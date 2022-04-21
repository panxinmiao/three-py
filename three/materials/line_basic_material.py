
from .material import Material
from ..math import Color

class LineBasicMaterial(Material):
    def __init__(self, parameters=None) -> None:
        '''
        parameters = {
            color: <hex>,
            opacity: <float>,
            linewidth: <float>,
            linecap: "round",
            linejoin: "round"
            }
        '''

        super().__init__()

        self.type = 'LineBasicMaterial'

        self.color =  Color( 0xffffff )

        self.linewidth = 1
        self.linecap = 'round'
        self.linejoin = 'round'

        self.setValues( parameters )

    def copy( self, source: 'Material' ):

        super().copy( source )

        self.color.copy( source.color )

        self.linewidth = source.linewidth
        self.linecap = source.linecap
        self.linejoin = source.linejoin

        return self
